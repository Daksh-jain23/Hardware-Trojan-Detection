"""
End-to-end Hardware Trojan detection pipeline.

Pipeline:
    Netlist
      -> Parser
      -> Features
      -> GNN
      -> Suspicious seeds
      -> Expanded suspicious region
      -> Structured evidence
      -> Anonymization
      -> LLM prompt
      -> LLM verdict + explanation

The heuristic is intentionally NOT part of this pipeline.

The trained GNN checkpoint is loaded; this script does not retrain it.

Usage:
    python src/pipeline.py data/TRIT-TS/s13207_T421.v

Optional:
    python src/pipeline.py data/TRIT-TS/s13207_T421.v --skip-llm
    python src/pipeline.py data/TRIT-TS/s13207_T421.v --threshold 0.95
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import random
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch

from anonymizer import anonymize_evidence as anonymize_evidence_full
from heuristic import evaluate_gnn_candidate_region

# ============================================================
# Paths / configuration
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

CHECKPOINT_PATH = ROOT / "checkpoints" / "trojan_gnn.pt"

RESULTS_DIR = ROOT / "results"
EVIDENCE_DIR = RESULTS_DIR / "evidence"
ANONYMIZED_DIR = RESULTS_DIR / "anonymized"
LLM_DIR = RESULTS_DIR / "llm"

SEED = 42
DEFAULT_THRESHOLD = 0.95
DEFAULT_REGION_HOPS = 2
DEFAULT_REGION_CAP = 50


# ============================================================
# Reproducibility
# ============================================================

def set_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# ============================================================
# Generic helpers
# ============================================================

def json_safe(value: Any) -> Any:
    """Convert common numpy/PyTorch values to JSON-safe Python values."""
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(v) for v in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, torch.Tensor):
        if value.numel() == 1:
            return value.detach().cpu().item()
        return value.detach().cpu().tolist()
    if isinstance(value, Path):
        return str(value)
    return value


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def family_from_path(path: Path) -> str:
    """
    Dataset naming convention:
        s13207_T421.v -> s13207
    """
    match = re.match(r"([^_]+)_T", path.stem)
    if match:
        return match.group(1)
    return path.stem.split("_")[0]


# ============================================================
# Parser adapter
# ============================================================

def parse_netlist(netlist_path: Path):
    """
    Use the project's parser.py.

    The existing project has evolved through a few parser function names,
    so this adapter accepts the common names without changing parser.py.
    """
    parser_module = importlib.import_module("parser")

    candidates = [
        "parse_netlist",
        "parse_verilog",
        "parse_file",
        "parse",
    ]

    for name in candidates:
        fn = getattr(parser_module, name, None)
        if not callable(fn):
            continue

        try:
            graph = fn(str(netlist_path))
        except TypeError:
            graph = fn(netlist_path)

        # Some parsers return (graph, metadata).
        if isinstance(graph, tuple):
            for item in graph:
                if hasattr(item, "nodes") and hasattr(item, "edges"):
                    graph = item
                    break

        if hasattr(graph, "nodes") and hasattr(graph, "edges"):
            return graph

    raise RuntimeError(
        "Could not find a usable parser function in src/parser.py. "
        "Expected one of: parse_netlist(), parse_verilog(), "
        "parse_file(), or parse()."
    )


# ============================================================
# Features / PyG
# ============================================================

def load_graph_to_pyg():
    dataset_module = importlib.import_module("dataset")

    fn = getattr(dataset_module, "graph_to_pyg", None)
    if not callable(fn):
        raise RuntimeError(
            "src/dataset.py must provide graph_to_pyg(graph)."
        )

    return fn


def compute_features(graph):
    """
    Validate that the project's feature extractor works on the graph.

    GNN inference itself uses dataset.graph_to_pyg(), which is the same
    conversion used during training.
    """
    features_module = importlib.import_module("features")

    fn = getattr(features_module, "compute_node_features", None)
    if not callable(fn):
        raise RuntimeError(
            "src/features.py must provide compute_node_features(graph)."
        )

    features, nodes = fn(graph)
    return features, nodes


# ============================================================
# GNN
# ============================================================

def load_gnn(checkpoint_path: Path, device: torch.device):
    gnn_module = importlib.import_module("gnn")
    TrojanGNN = getattr(gnn_module, "TrojanGNN")

    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"GNN checkpoint not found: {checkpoint_path}"
        )

    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=False,
    )

    state_dict = checkpoint.get("model_state_dict", checkpoint)

    input_dim = checkpoint.get("input_dim")
    hidden_dim = checkpoint.get("hidden_dim", 64)
    dropout = checkpoint.get("dropout", 0.2)

    if input_dim is None:
        raise RuntimeError(
            "Checkpoint does not contain input_dim."
        )

    model = TrojanGNN(
        input_dim=input_dim,
        hidden_dim=hidden_dim,
        dropout=dropout,
    ).to(device)

    model.load_state_dict(state_dict)
    model.eval()

    return model, checkpoint


def score_graph(model, graph, graph_to_pyg, device):
    """
    Run the trained GNN over the complete circuit.

    Returns:
        scores: {original_node_id: probability}
    """
    data = graph_to_pyg(graph).to(device)

    with torch.no_grad():
        logits = model(
            data.x,
            data.edge_index,
        )
        probabilities = torch.sigmoid(logits).detach().cpu().numpy()

    nodes = list(graph.nodes())

    if len(nodes) != len(probabilities):
        raise RuntimeError(
            "Node count mismatch between NetworkX graph and PyG graph."
        )

    return {
        node: float(probabilities[i])
        for i, node in enumerate(nodes)
    }


# ============================================================
# Suspicious seeds
# ============================================================

def extract_suspicious_seeds(
    graph,
    scores: dict,
    threshold: float,
):
    seeds = {
        node
        for node in graph.nodes()
        if scores.get(node, 0.0) >= threshold
    }

    return seeds


# ============================================================
# Region extraction
# ============================================================

def build_region(
    graph,
    seeds,
    hops: int = DEFAULT_REGION_HOPS,
    cap: int = DEFAULT_REGION_CAP,
):
    """
    Expand the GNN-positive seeds by graph hops.

    If the next expansion exceeds the cap, retain the previous region.
    This matches the project's existing region-expansion behavior.
    """
    context = set(seeds)
    frontier = set(seeds)

    for _ in range(hops):
        next_frontier = set()

        for node in frontier:
            next_frontier.update(graph.predecessors(node))
            next_frontier.update(graph.successors(node))

        candidate = context | next_frontier

        if len(candidate) > cap:
            break

        frontier = next_frontier - context
        context = candidate

    return context


# ============================================================
# Structural statistics
# ============================================================

def gate_type(graph, node):
    data = graph.nodes[node]
    return (
        data.get("gate_type")
        or data.get("type")
        or data.get("cell_type")
        or "?"
    )

def local_structural_patterns(
    graph,
    node_scores: dict,
    region: set,
    threshold: float,
    max_nodes: int = 25,
) -> dict:
    """
    Extract compact structural relationships inside the suspicious region.

    Identifiers are preserved here because this evidence is anonymized
    before being sent to the LLM.
    """

    region = set(region)

    # Sort by GNN score so the most relevant nodes are represented first.
    ranked = sorted(
        region,
        key=lambda n: float(node_scores.get(n, 0.0)),
        reverse=True,
    )

    representative = ranked[:max_nodes]

    nodes = []

    for node in representative:
        score = float(node_scores.get(node, 0.0))

        successors = [
            x for x in graph.successors(node)
            if x in region
        ]

        predecessors = [
            x for x in graph.predecessors(node)
            if x in region
        ]

        high_score_successors = [
            x for x in successors
            if float(node_scores.get(x, 0.0)) >= threshold
        ]

        high_score_predecessors = [
            x for x in predecessors
            if float(node_scores.get(x, 0.0)) >= threshold
        ]

        node_data = graph.nodes[node]

        nodes.append({
            "gate": str(node),
            "gate_type": node_data.get("gate_type"),
            "gnn_score": round(score, 6),
            "fanin": len(list(graph.predecessors(node))),
            "fanout": len(list(graph.successors(node))),
            "region_fanin": len(predecessors),
            "region_fanout": len(successors),
            "high_score_region_fanin": len(high_score_predecessors),
            "high_score_region_fanout": len(high_score_successors),
            "region_predecessors": predecessors[:8],
            "region_successors": successors[:8],
        })

    # Count direct high-score-to-high-score relationships.
    high_score_nodes = {
        n
        for n in region
        if float(node_scores.get(n, 0.0)) >= threshold
    }

    high_score_internal_edges = 0

    for source, target in graph.edges():
        if (
            source in high_score_nodes
            and target in high_score_nodes
        ):
            high_score_internal_edges += 1

    # Identify high-score nodes touching sequential-like nodes.
    sequential_types = {
        "dff",
        "dffs",
        "dffles",
        "dffr",
        "dffrs",
        "dffe",
    }

    high_score_to_sequential = []

    for node in high_score_nodes:
        for target in graph.successors(node):
            if target not in region:
                continue

            target_type = str(
                graph.nodes[target].get("gate_type", "")
            ).lower()

            if any(
                seq_type in target_type
                for seq_type in sequential_types
            ):
                high_score_to_sequential.append({
                    "source": node,
                    "target": target,
                })

    return {
        "representative_node_count": len(nodes),
        "representative_nodes": nodes,
        "high_score_node_count": len(high_score_nodes),
        "high_score_internal_edges": high_score_internal_edges,
        "high_score_to_sequential_count": len(
            high_score_to_sequential
        ),
        "high_score_to_sequential": high_score_to_sequential[:20],
    }

def structural_stats(graph, region):
    """
    Compute structural statistics for a suspicious region.

    Definitions:
      - internal_edges:
          Directed edges where both endpoints are inside the region.
      - boundary_edges:
          All directed edges crossing between the region and the
          surrounding circuit, in either direction.
      - region_exits:
          Region nodes having outgoing connections to nodes outside
          the region.

    Boundary edges and region exits are intentionally different:
      one exit node may have multiple boundary edges.
    """
    region = set(region)

    internal_edges = 0
    boundary_edges = 0
    exits = []

    # Count ALL graph edges exactly once.
    for source, target in graph.edges():
        source_in = source in region
        target_in = target in region

        if source_in and target_in:
            internal_edges += 1
        elif source_in != target_in:
            boundary_edges += 1

    # Region exits are specifically outgoing connections
    # from the suspicious region to the surrounding circuit.
    for node in region:
        successors = list(graph.successors(node))

        outside_successors = [
            successor
            for successor in successors
            if successor not in region
        ]

        if outside_successors:
            exits.append(
                {
                    "gate": str(node),
                    "gate_type": gate_type(graph, node),
                    "connections": [
                        str(successor)
                        for successor in outside_successors
                    ],
                }
            )

    gate_types = {}

    for node in region:
        gt = gate_type(graph, node)
        gate_types[gt] = gate_types.get(gt, 0) + 1

    sequential_markers = (
        "dff",
        "dffs",
        "dffle",
        "dffles",
        "latch",
        "ff",
    )

    sequential = [
        str(node)
        for node in region
        if any(
            marker in str(gate_type(graph, node)).lower()
            for marker in sequential_markers
        )
    ]

    primary_inputs = [
        str(node)
        for node in region
        if (
            graph.in_degree(node) == 0
            or graph.nodes[node].get("primary_input", False)
        )
    ]

    primary_outputs = [
        str(node)
        for node in region
        if (
            graph.out_degree(node) == 0
            or graph.nodes[node].get("primary_output", False)
        )
    ]

    return {
        "internal_edges": internal_edges,
        "boundary_edges": boundary_edges,
        "region_exit_count": len(exits),
        "region_exits": exits,
        "gate_types": gate_types,
        "sequential_like_gate_count": len(sequential),
        "sequential_like_gates": sequential,
        "primary_input_count": len(primary_inputs),
        "primary_output_count": len(primary_outputs),
    }

def depth_values(graph):
    """
    Compute depth from primary inputs.

    Cyclic/sequential graphs are handled gracefully.
    """
    try:
        dag = graph.copy()
        cycles = list(
            __import__("networkx").simple_cycles(dag)
        )

        if cycles:
            return {}

        sources = [
            node
            for node in graph.nodes()
            if graph.in_degree(node) == 0
        ]

        depths = {}
        for source in sources:
            lengths = __import__("networkx").single_source_shortest_path_length(
                graph,
                source,
            )
            for node, distance in lengths.items():
                if node not in depths:
                    depths[node] = distance
                else:
                    depths[node] = min(depths[node], distance)

        return depths

    except Exception:
        return {}


def output_distances(graph):
    try:
        reversed_graph = graph.reverse(copy=False)

        sinks = [
            node
            for node in graph.nodes()
            if graph.out_degree(node) == 0
        ]

        distances = {}

        for sink in sinks:
            lengths = __import__("networkx").single_source_shortest_path_length(
                reversed_graph,
                sink,
            )
            for node, distance in lengths.items():
                if node not in distances:
                    distances[node] = distance
                else:
                    distances[node] = min(
                        distances[node],
                        distance,
                    )

        return distances

    except Exception:
        return {}


# ============================================================
# Evidence
# ============================================================

def build_evidence(
    graph,
    netlist_path: Path,
    scores: dict,
    seeds: set,
    region: set,
    threshold: float,
):
    depths = depth_values(graph)
    output_distance_map = output_distances(graph)

    stats = structural_stats(graph, region)

    seed_scores = [
        scores[node]
        for node in seeds
        if node in scores
    ]

    sorted_seeds = sorted(
        seeds,
        key=lambda node: scores.get(node, 0.0),
        reverse=True,
    )

    suspicious_seed_records = []

    for node in sorted_seeds:
        suspicious_seed_records.append(
            {
                "gate": str(node),
                "type": gate_type(graph, node),
                "gnn_score": round(
                    scores.get(node, 0.0),
                    6,
                ),
                "fanin": graph.in_degree(node),
                "fanout": graph.out_degree(node),
            }
        )

    region_nodes = []

    for node in sorted(
        region,
        key=lambda n: scores.get(n, 0.0),
        reverse=True,
    ):
        record = {
            "gate": str(node),
            "type": gate_type(graph, node),
            "gnn_score": round(
                scores.get(node, 0.0),
                6,
            ),
            "fanin": graph.in_degree(node),
            "fanout": graph.out_degree(node),
        }

        if node in depths:
            record["depth_from_input"] = depths[node]

        if node in output_distance_map:
            record["distance_to_output"] = output_distance_map[node]

        if (
            graph.in_degree(node) == 0
            or graph.nodes[node].get("primary_input", False)
        ):
            record["primary_input"] = True

        if (
            graph.out_degree(node) == 0
            or graph.nodes[node].get("primary_output", False)
        ):
            record["primary_output"] = True

        if any(
            successor not in region
            for successor in graph.successors(node)
        ) or graph.out_degree(node) == 0:
            record["region_exit"] = True

        region_nodes.append(record)

    evidence = {
        "task": "hardware_trojan_detection",
        "decision": None,
        "decision_note": (
            "GNN/localization stage only. Final LLM decision is "
            "produced downstream."
        ),

        "input": {
            "netlist": str(netlist_path.resolve()),
            "family": family_from_path(netlist_path),
        },

        "graph": {
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
        },

        "gnn": {
            "threshold": threshold,
            "max_score": round(
                max(scores.values()) if scores else 0.0,
                6,
            ),
            "mean_score": round(
                float(np.mean(list(scores.values())))
                if scores
                else 0.0,
                6,
            ),
            "median_score": round(
                float(np.median(list(scores.values())))
                if scores
                else 0.0,
                6,
            ),
            "min_score": round(
                min(scores.values()) if scores else 0.0,
                6,
            ),
            "positive_count": len(seeds),
        },

        "suspicious_seeds": suspicious_seed_records,

        "region": {
            "size": len(region),
            "gate_types": stats["gate_types"],
            "internal_edges": stats["internal_edges"],
            "boundary_edges": stats["boundary_edges"],
        },

        "structural_evidence": {
            "primary_inputs": stats["primary_input_count"],
            "primary_outputs": stats["primary_output_count"],
            "sequential_like_gates": stats[
                "sequential_like_gates"
            ],
            "region_exits": stats["region_exits"],
            "internal_edges": stats["internal_edges"],
            "boundary_edges": stats["boundary_edges"],
        },

        "local_structural_patterns": local_structural_patterns(
            graph,
            scores,
            region,
            threshold,
        ),

        "nodes": region_nodes,
    }

    # Deterministic seed facts used by llm_prompt.py.
    evidence["deterministic_facts"] = {
        "suspicious_seed_count": len(seeds),
        "expanded_region_size": len(region),
        "seed_score_max": (
            round(max(seed_scores), 6)
            if seed_scores
            else None
        ),
        "seed_score_min": (
            round(min(seed_scores), 6)
            if seed_scores
            else None
        ),
        "seed_score_mean": (
            round(float(np.mean(seed_scores)), 6)
            if seed_scores
            else None
        ),
        "seed_count_at_or_above_threshold": sum(
            score >= threshold
            for score in seed_scores
        ),
        "seed_count_at_or_above_0_99": sum(
            score >= 0.99
            for score in seed_scores
        ),
        "sequential_like_gate_count": stats[
            "sequential_like_gate_count"
        ],
        "region_exit_count": stats[
            "region_exit_count"
        ],
    }

    return json_safe(evidence)


# ============================================================
# LLM prompt
# ============================================================

def generate_prompt(anonymized_evidence: dict) -> Path:
    """
    Use the project's llm_prompt.py builder.
    """
    module = importlib.import_module("llm_prompt")

    builder = getattr(module, "build_prompt", None)

    if not callable(builder):
        raise RuntimeError(
            "src/llm_prompt.py must provide build_prompt(evidence)."
        )

    prompt = builder(anonymized_evidence)

    input_path = Path(
        anonymized_evidence["input"]["netlist"]
    )

    output_path = (
        LLM_DIR
        / f"{input_path.stem}_prompt.txt"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        prompt,
        encoding="utf-8",
    )

    return output_path


# ============================================================
# LLM execution
# ============================================================

def run_llm(prompt_path: Path) -> Path:
    """
    Use the project's llm.py implementation.

    This keeps provider/model switching in one place:
        ACTIVE_PROVIDER = "ollama"
        ACTIVE_PROVIDER = "gemini"
    """
    module = importlib.import_module("llm")

    # Reuse the existing module's model interface.
    prompt = prompt_path.read_text(
        encoding="utf-8"
    )

    run_function = getattr(module, "run_llm", None)

    if not callable(run_function):
        raise RuntimeError(
            "src/llm.py must provide run_llm(prompt)."
        )

    response = run_function(prompt)

    extract_decision = getattr(
        module,
        "extract_decision",
        None,
    )

    extract_confidence = getattr(
        module,
        "extract_confidence",
        None,
    )

    decision = (
        extract_decision(response)
        if callable(extract_decision)
        else "UNCERTAIN"
    )

    confidence = (
        extract_confidence(response)
        if callable(extract_confidence)
        else "LOW"
    )

    provider = getattr(
        module,
        "ACTIVE_PROVIDER",
        "unknown",
    )

    if provider == "ollama":
        model = getattr(
            module,
            "OLLAMA_MODEL",
            "unknown",
        )
    else:
        model = getattr(
            module,
            "GEMINI_MODEL",
            "unknown",
        )

    result = {
        "task": "hardware_trojan_detection",
        "provider": provider,
        "model": model,
        "decision": decision,
        "confidence": confidence,
        "response": response,
        "prompt_file": str(
            prompt_path.resolve()
        ),
        "llm_constraints": {
            "heuristic_output_used": False,
            "node_names_used_for_decision": False,
        },
    }

    output_path = (
        LLM_DIR
        / (
            prompt_path.stem
            .replace("_prompt", "")
            + f"_{provider}_llm.json"
        )
    )

    output_path.write_text(
        json.dumps(
            result,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("========== LLM RESULT ==========")
    print("Provider   :", provider)
    print("Model      :", model)
    print("Decision   :", decision)
    print("Confidence :", confidence)
    print()
    print(response)
    print()
    print("Saved to   :", output_path.resolve())

    return output_path


# ============================================================
# Main pipeline
# ============================================================

def run_pipeline(
    netlist_path: Path,
    checkpoint_path: Path = CHECKPOINT_PATH,
    threshold: float = DEFAULT_THRESHOLD,
    hops: int = DEFAULT_REGION_HOPS,
    cap: int = DEFAULT_REGION_CAP,
    skip_llm: bool = False,
):
    set_seed()

    if not netlist_path.exists():
        raise FileNotFoundError(
            f"Netlist not found: {netlist_path}"
        )

    print("=" * 60)
    print("HARDWARE TROJAN DETECTION PIPELINE")
    print("=" * 60)
    print("Netlist    :", netlist_path.resolve())
    print("Family     :", family_from_path(netlist_path))
    print("Checkpoint :", checkpoint_path.resolve())
    print("Threshold  :", threshold)
    print("Region hops:", hops)
    print("Region cap :", cap)

    device = (
        torch.device("cuda")
        if torch.cuda.is_available()
        else torch.device("cpu")
    )

    print("Device     :", device)

    # --------------------------------------------------------
    # 1. Parse
    # --------------------------------------------------------

    print()
    print("[1/7] Parsing netlist...")

    graph = parse_netlist(netlist_path)

    print(
        "       nodes =",
        graph.number_of_nodes(),
        "edges =",
        graph.number_of_edges(),
    )

    # --------------------------------------------------------
    # 2. Features
    # --------------------------------------------------------

    print()
    print("[2/7] Computing node features...")

    features, feature_nodes = compute_features(graph)

    print(
        "       nodes =",
        len(feature_nodes),
        "feature_dim =",
        np.asarray(features).shape[1],
    )

    # --------------------------------------------------------
    # 3. GNN
    # --------------------------------------------------------

    print()
    print("[3/7] Loading trained GNN...")

    model, checkpoint = load_gnn(
        checkpoint_path,
        device,
    )

    graph_to_pyg = load_graph_to_pyg()

    print(
        "       checkpoint epoch =",
        checkpoint.get("epoch", "unknown"),
    )
    print(
        "       validation F1 =",
        checkpoint.get("val_f1", "unknown"),
    )

    print()
    print("       Scoring complete circuit...")

    scores = score_graph(
        model,
        graph,
        graph_to_pyg,
        device,
    )

    # --------------------------------------------------------
    # 4. Suspicious seeds
    # --------------------------------------------------------

    print()
    print("[4/7] Extracting suspicious GNN seeds...")

    seeds = extract_suspicious_seeds(
        graph,
        scores,
        threshold,
    )

    print(
        "       suspicious seeds =",
        len(seeds),
    )

    if seeds:
        top_seed = max(
            seeds,
            key=lambda n: scores[n],
        )

        print(
            "       max seed score =",
            f"{scores[top_seed]:.6f}",
        )

    # --------------------------------------------------------
    # 5. Region
    # --------------------------------------------------------

    print()
    print("[5/7] Building suspicious region...")

    region = build_region(
        graph,
        seeds,
        hops=hops,
        cap=cap,
    )

    print(
        "       expanded region =",
        len(region),
        "nodes",
    )

    # --------------------------------------------------------
    # 6. Evidence + anonymization + prompt
    # --------------------------------------------------------

    print()
    print("[6/7] Building structured evidence...")

    evidence = build_evidence(
        graph,
        netlist_path,
        scores,
        seeds,
        region,
        threshold,
    )

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    evidence_path = (
        EVIDENCE_DIR
        / f"{netlist_path.stem}_evidence.json"
    )

    evidence_path.write_text(
        json.dumps(
            evidence,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "       evidence saved =",
        evidence_path.resolve(),
    )

    print()
    print("       Anonymizing evidence...")

    anonymized, _mapping = anonymize_evidence_full(
        evidence
    )

    ANONYMIZED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    anonymized_path = (
        ANONYMIZED_DIR
        / f"{netlist_path.stem}_evidence_anonymized.json"
    )

    anonymized_path.write_text(
        json.dumps(
            anonymized,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "       anonymized evidence saved =",
        anonymized_path.resolve(),
    )

    print()
    print("       Building LLM prompt...")

    prompt_path = generate_prompt(
        anonymized
    )

    print(
        "       prompt saved =",
        prompt_path.resolve(),
    )

    print(
        "       prompt length =",
        len(
            prompt_path.read_text(
                encoding="utf-8"
            )
        ),
        "characters",
    )

    # --------------------------------------------------------
    # 6b. GNN -> Heuristic Verification
    # --------------------------------------------------------
    print()
    print("       Running GNN -> Heuristic structural verification...")
    heuristic_verification = evaluate_gnn_candidate_region(
        graph=graph,
        suspicious_seeds=seeds,
        region_nodes=region,
        gnn_probs=scores,
    )
    heur_path = (
        ROOT / "results" / "heuristic" / f"{netlist_path.stem}_gnn_heuristic.json"
    )
    heur_path.parent.mkdir(parents=True, exist_ok=True)
    heur_path.write_text(json.dumps(heuristic_verification, indent=2), encoding="utf-8")
    print(
        f"       GNN -> Heuristic verdict = {heuristic_verification['verdict']} "
        f"(Score: {heuristic_verification['score']:.4f})"
    )

    # --------------------------------------------------------
    # 7. LLM
    # --------------------------------------------------------

    llm_path = None

    if skip_llm:
        print()
        print("[7/7] LLM skipped (--skip-llm).")
    else:
        print()
        print("[7/7] Running LLM...")
        llm_path = run_llm(prompt_path)

    # --------------------------------------------------------
    # 3-Way Comparison Summary
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("3-WAY COMPARISON: PURE GNN vs. GNN->HEURISTIC vs. GNN->LLM")
    print("=" * 60)

    pure_gnn_verdict = "SUSPICIOUS" if len(seeds) > 0 else "NORMAL"
    max_score = max(scores.values(), default=0.0)
    print(f"1. Pure GNN         : {pure_gnn_verdict:<20} (Seeds: {len(seeds)}, Max Score: {max_score:.4f})")
    print(f"2. GNN -> Heuristic : {heuristic_verification['verdict']:<20} (Confirmed: {len(heuristic_verification['confirmed_seeds'])}/{len(seeds)}, Score: {heuristic_verification['score']:.4f})")

    llm_decision = "SKIPPED"
    llm_confidence = "N/A"
    if llm_path and llm_path.exists():
        try:
            llm_data = json.loads(llm_path.read_text(encoding="utf-8"))
            llm_decision = llm_data.get("decision", "UNKNOWN")
            llm_confidence = llm_data.get("confidence", "UNKNOWN")
            print(f"3. GNN -> LLM       : {llm_decision + ' (' + llm_confidence + ')':<20} (Structural Reasoning Explanation)")
        except Exception:
            print(f"3. GNN -> LLM       : {llm_decision:<20}")
    else:
        print(f"3. GNN -> LLM       : {llm_decision:<20}")

    print("=" * 60)
    print("Netlist       :", netlist_path.resolve())
    print("GNN seeds     :", len(seeds))
    print("Region size   :", len(region))
    print("Evidence      :", evidence_path.resolve())
    print("Anonymized    :", anonymized_path.resolve())
    print("Prompt        :", prompt_path.resolve())

    if llm_path:
        print("LLM result    :", llm_path.resolve())

    return {
        "netlist": netlist_path,
        "graph": graph,
        "scores": scores,
        "seeds": seeds,
        "region": region,
        "pure_gnn": {
            "verdict": pure_gnn_verdict,
            "seed_count": len(seeds),
            "max_score": float(max_score),
        },
        "gnn_to_heuristic": heuristic_verification,
        "gnn_to_llm": {
            "decision": llm_decision,
            "confidence": llm_confidence,
            "llm_path": str(llm_path) if llm_path else None,
        },
        "evidence_path": evidence_path,
        "anonymized_path": anonymized_path,
        "prompt_path": prompt_path,
        "llm_path": llm_path,
        "heuristic_verification_path": heur_path,
    }


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description=(
            "End-to-end Hardware Trojan detection pipeline."
        )
    )

    parser.add_argument(
        "netlist",
        type=Path,
        help="Path to a Verilog netlist.",
    )

    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=CHECKPOINT_PATH,
        help="Path to trained GNN checkpoint.",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="GNN suspicious threshold. Default: 0.95",
    )

    parser.add_argument(
        "--hops",
        type=int,
        default=DEFAULT_REGION_HOPS,
        help="Region expansion hops. Default: 2",
    )

    parser.add_argument(
        "--cap",
        type=int,
        default=DEFAULT_REGION_CAP,
        help="Maximum expanded-region size. Default: 50",
    )

    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Run through evidence/prompt generation but skip the LLM.",
    )

    args = parser.parse_args()

    run_pipeline(
        netlist_path=args.netlist,
        checkpoint_path=args.checkpoint,
        threshold=args.threshold,
        hops=args.hops,
        cap=args.cap,
        skip_llm=args.skip_llm,
    )


if __name__ == "__main__":
    main()
