"""
Structured evidence extraction for Hardware Trojan detection.

Pipeline:

    Verilog
       ↓
    Parser
       ↓
    41 structural features
       ↓
    Trained GNN
       ↓
    Suspicious nodes
       ↓
    Local suspicious region
       ↓
    THIS FILE
       ↓
    Structured evidence
       ↓
    LLM

The purpose of this file is NOT to make the final Trojan decision.

It converts GNN + graph information into structured evidence that can
later be supplied to the LLM.

This prevents the LLM from having to infer circuit topology from raw
Verilog text.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, deque
from pathlib import Path
from typing import Dict, Iterable, List, Set

import networkx as nx
import numpy as np
import torch

from parser import parse_netlist
from dataset import graph_to_pyg
from gnn import TrojanGNN


# ============================================================
# Configuration
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

CHECKPOINT_PATH = ROOT / "checkpoints" / "trojan_gnn.pt"

DEFAULT_THRESHOLD = 0.95

# Number of highest-scoring nodes used as initial suspicious seeds.
TOP_K = 15

# Expand suspicious nodes through the circuit.
HOPS = 2

# Maximum region size sent downstream.
MAX_REGION_SIZE = 50

# Maximum number of individual gates shown in detailed evidence.
MAX_DETAILED_GATES = 50


# ============================================================
# Device
# ============================================================

def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


# ============================================================
# Model loading
# ============================================================

def load_model(
    checkpoint_path: Path = CHECKPOINT_PATH,
    device: torch.device | None = None,
):
    """
    Load the trained TrojanGNN checkpoint.

    The training code stores:
        model_state_dict
        input_dim
        hidden_dim
        dropout
    """

    if device is None:
        device = get_device()

    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"GNN checkpoint not found:\n{checkpoint_path}\n\n"
            "Run train_gnn.py first."
        )

    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=False,
    )

    # Support both the current checkpoint format and a raw
    # state_dict checkpoint.
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:

        state_dict = checkpoint["model_state_dict"]

        input_dim = int(
            checkpoint.get("input_dim", 41)
        )

        hidden_dim = int(
            checkpoint.get("hidden_dim", 64)
        )

        dropout = float(
            checkpoint.get("dropout", 0.2)
        )

    else:

        state_dict = checkpoint

        input_dim = 41
        hidden_dim = 64
        dropout = 0.2

    model = TrojanGNN(
        input_dim=input_dim,
        hidden_dim=hidden_dim,
        dropout=dropout,
    )

    model.load_state_dict(state_dict)

    model.to(device)
    model.eval()

    return model


# ============================================================
# GNN scoring
# ============================================================

@torch.no_grad()
def score_graph(
    model,
    graph,
    device: torch.device,
):
    """
    Run the trained GNN on a complete circuit.

    Returns:
        scores:
            dictionary:
                gate_name -> Trojan probability

        nodes:
            nodes in exactly the same order used by graph_to_pyg()
    """

    data = graph_to_pyg(graph)
    data = data.to(device)

    logits = model(
        data.x,
        data.edge_index,
    )

    probabilities = torch.sigmoid(logits)

    probabilities = probabilities.detach().cpu().numpy().reshape(-1)

    nodes = list(graph.nodes())

    if len(nodes) != len(probabilities):
        raise RuntimeError(
            "Node count mismatch between NetworkX graph and PyG graph."
        )

    scores = {
        node: float(probability)
        for node, probability in zip(nodes, probabilities)
    }

    return scores, nodes


# ============================================================
# Suspicious seeds
# ============================================================

def select_suspicious_seeds(
    scores: Dict,
    top_k: int = TOP_K,
    threshold: float = DEFAULT_THRESHOLD,
) -> List:
    """
    Select initial suspicious gates.

    We use two mechanisms:

    1. Gates above the trained decision threshold.
    2. Top-K GNN-ranked gates.

    The union makes the evidence layer robust when a Trojan contains
    multiple gates with slightly different scores.
    """

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    threshold_nodes = [
        node
        for node, score in ranked
        if score >= threshold
    ]

    top_nodes = [
        node
        for node, _ in ranked[:top_k]
    ]

    selected = []

    seen = set()

    for node in threshold_nodes + top_nodes:

        if node not in seen:

            selected.append(node)
            seen.add(node)

    return selected


# ============================================================
# Region expansion
# ============================================================

def expand_region(
    graph: nx.DiGraph,
    seeds: Iterable,
    hops: int = HOPS,
    max_size: int = MAX_REGION_SIZE,
) -> Set:
    """
    Expand suspicious seed gates through the circuit.

    Both predecessors and successors are included because a Trojan
    structure can be connected through either direction relative to
    an individual suspicious gate.
    """

    seeds = list(seeds)

    region = set(seeds)

    frontier = set(seeds)

    for _ in range(hops):

        next_frontier = set()

        for node in frontier:

            if node not in graph:
                continue

            next_frontier.update(
                graph.predecessors(node)
            )

            next_frontier.update(
                graph.successors(node)
            )

        next_frontier -= region

        if not next_frontier:
            break

        # Avoid exploding the region.
        remaining = max_size - len(region)

        if remaining <= 0:
            break

        if len(next_frontier) > remaining:

            # Prefer nodes with stronger GNN-local connectivity.
            next_frontier = set(
                list(next_frontier)[:remaining]
            )

        region.update(next_frontier)

        frontier = next_frontier

    return region


# ============================================================
# Gate type helpers
# ============================================================

def gate_type(graph, node) -> str:
    """
    Retrieve gate type from the parser metadata.

    The parser may use different attribute names depending on the
    netlist, so several common names are supported.
    """

    data = graph.nodes[node]

    for key in (
        "gate_type",
        "type",
        "cell_type",
        "kind",
    ):

        value = data.get(key)

        if value is not None:
            return str(value)

    return "UNKNOWN"


def is_primary_input(graph, node) -> bool:
    """
    Detect primary-input nodes.
    """

    data = graph.nodes[node]

    node_type = gate_type(graph, node).upper()

    if node_type in {
        "PI",
        "PRIMARY_INPUT",
        "INPUT",
    }:
        return True

    if graph.in_degree(node) == 0:
        return True

    return bool(
        data.get("is_primary_input", False)
    )


def is_primary_output(graph, node) -> bool:
    """
    Detect primary-output nodes.
    """

    data = graph.nodes[node]

    node_type = gate_type(graph, node).upper()

    if node_type in {
        "PO",
        "PRIMARY_OUTPUT",
        "OUTPUT",
    }:
        return True

    if graph.out_degree(node) == 0:
        return True

    return bool(
        data.get("is_primary_output", False)
    )


# ============================================================
# Structural statistics
# ============================================================

def calculate_depths(graph: nx.DiGraph):
    """
    Approximate distance from circuit inputs.

    Sequential circuits can contain cycles, so we use a BFS over the
    directed graph starting from zero-indegree nodes.

    If a node is unreachable because of feedback, it receives a
    reasonable fallback value.
    """

    depths = {}

    sources = [
        node
        for node in graph.nodes()
        if graph.in_degree(node) == 0
    ]

    queue = deque()

    for node in sources:

        depths[node] = 0
        queue.append(node)

    while queue:

        node = queue.popleft()

        current_depth = depths[node]

        for successor in graph.successors(node):

            candidate = current_depth + 1

            if (
                successor not in depths
                or candidate < depths[successor]
            ):

                depths[successor] = candidate
                queue.append(successor)

    fallback = max(depths.values(), default=0) + 1

    for node in graph.nodes():

        depths.setdefault(
            node,
            fallback,
        )

    return depths


def calculate_distance_to_output(graph: nx.DiGraph):
    """
    Approximate distance from each node to a circuit output.
    """

    reversed_graph = graph.reverse(copy=False)

    distances = {}

    sources = [
        node
        for node in graph.nodes()
        if graph.out_degree(node) == 0
    ]

    queue = deque()

    for node in sources:

        distances[node] = 0
        queue.append(node)

    while queue:

        node = queue.popleft()

        current_distance = distances[node]

        for predecessor in reversed_graph.successors(node):

            candidate = current_distance + 1

            if (
                predecessor not in distances
                or candidate < distances[predecessor]
            ):

                distances[predecessor] = candidate
                queue.append(predecessor)

    fallback = max(
        distances.values(),
        default=0,
    ) + 1

    for node in graph.nodes():

        distances.setdefault(
            node,
            fallback,
        )

    return distances


# ============================================================
# Region edge analysis
# ============================================================

def analyze_edges(
    graph: nx.DiGraph,
    region: Set,
):
    """
    Separate edges into:

        internal:
            both endpoints are inside region

        boundary:
            one endpoint is inside and the other is outside
    """

    internal = []
    boundary = []

    for source, target in graph.edges():

        source_inside = source in region
        target_inside = target in region

        if source_inside and target_inside:

            internal.append(
                (source, target)
            )

        elif source_inside or target_inside:

            boundary.append(
                (source, target)
            )

    return internal, boundary


def find_region_exits(
    graph: nx.DiGraph,
    region: Set,
):
    """
    Find gates inside the suspicious region that drive logic outside
    the region.

    These are particularly important because a Trojan payload normally
    has to reconnect with legitimate circuit logic.
    """

    exits = []

    for node in region:

        outside_successors = [
            successor
            for successor in graph.successors(node)
            if successor not in region
        ]

        if outside_successors:

            exits.append(
                {
                    "gate": str(node),
                    "gate_type": gate_type(graph, node),
                    "connections": [
                        str(x)
                        for x in outside_successors
                    ],
                }
            )

    return exits


# ============================================================
# Signal-flow extraction
# ============================================================

def extract_signal_paths(
    graph: nx.DiGraph,
    region: Set,
    max_paths: int = 30,
):
    """
    Extract short structural paths through the suspicious region.

    This gives the LLM explicit topology instead of forcing it to
    reconstruct the topology itself.
    """

    paths = []

    subgraph = graph.subgraph(region)

    try:
        sources = [
            node
            for node in subgraph.nodes()
            if subgraph.in_degree(node) == 0
        ]

        targets = [
            node
            for node in subgraph.nodes()
            if subgraph.out_degree(node) == 0
        ]

        for source in sources:

            for target in targets:

                if len(paths) >= max_paths:
                    break

                if source == target:
                    continue

                try:

                    path = nx.shortest_path(
                        subgraph,
                        source,
                        target,
                    )

                except nx.NetworkXNoPath:

                    continue

                paths.append(
                    [
                        {
                            "gate": str(node),
                            "type": gate_type(
                                graph,
                                node,
                            ),
                        }
                        for node in path
                    ]
                )

            if len(paths) >= max_paths:
                break

    except Exception:
        pass

    return paths


# ============================================================
# Detailed node evidence
# ============================================================

def build_node_evidence(
    graph: nx.DiGraph,
    region: Set,
    scores: Dict,
    depths: Dict,
    output_distances: Dict,
):
    """
    Build structured information for every gate in the region.
    """

    ranked = sorted(
        region,
        key=lambda node: scores.get(node, 0.0),
        reverse=True,
    )

    ranked = ranked[
        :MAX_DETAILED_GATES
    ]

    evidence = []

    region_set = set(region)

    for node in ranked:

        predecessors = list(
            graph.predecessors(node)
        )

        successors = list(
            graph.successors(node)
        )

        outside_successors = [
            successor
            for successor in successors
            if successor not in region_set
        ]

        evidence.append(
            {
                "gate": str(node),

                "type": gate_type(
                    graph,
                    node,
                ),

                "gnn_score": round(
                    float(scores.get(node, 0.0)),
                    6,
                ),

                "fanin": int(
                    graph.in_degree(node)
                ),

                "fanout": int(
                    graph.out_degree(node)
                ),

                "depth_from_input": int(
                    depths.get(node, 0)
                ),

                "distance_to_output": int(
                    output_distances.get(node, 0)
                ),

                "primary_input": is_primary_input(
                    graph,
                    node,
                ),

                "primary_output": is_primary_output(
                    graph,
                    node,
                ),

                "inputs": [
                    str(x)
                    for x in predecessors
                ],

                "outputs": [
                    str(x)
                    for x in successors
                ],

                "region_exit": bool(
                    outside_successors
                ),

                "external_outputs": [
                    str(x)
                    for x in outside_successors
                ],
            }
        )

    return evidence


# ============================================================
# Gate-type statistics
# ============================================================

def gate_type_summary(
    graph: nx.DiGraph,
    region: Set,
):
    counts = Counter(
        gate_type(graph, node)
        for node in region
    )

    return dict(
        sorted(
            counts.items(),
            key=lambda item: (-item[1], item[0]),
        )
    )


def fanin_summary(
    graph: nx.DiGraph,
    region: Set,
):
    counts = Counter(
        graph.in_degree(node)
        for node in region
    )

    return {
        str(k): int(v)
        for k, v in sorted(counts.items())
    }


# ============================================================
# Suspicion statistics
# ============================================================

def suspicion_summary(
    region: Set,
    scores: Dict,
):
    values = [
        float(scores.get(node, 0.0))
        for node in region
    ]

    if not values:
        return {
            "max": 0.0,
            "mean": 0.0,
            "median": 0.0,
            "min": 0.0,
        }

    return {
        "max": round(max(values), 6),
        "mean": round(
            float(np.mean(values)),
            6,
        ),
        "median": round(
            float(np.median(values)),
            6,
        ),
        "min": round(min(values), 6),
    }


# ============================================================
# Main evidence builder
# ============================================================

def build_evidence(
    graph: nx.DiGraph,
    scores: Dict,
    threshold: float = DEFAULT_THRESHOLD,
    top_k: int = TOP_K,
    hops: int = HOPS,
    max_region_size: int = MAX_REGION_SIZE,
):
    """
    Build the complete structured evidence object.

    IMPORTANT:
    This function does not decide whether the circuit is a Trojan.

    It only reports evidence.
    """

    seeds = select_suspicious_seeds(
        scores=scores,
        top_k=top_k,
        threshold=threshold,
    )

    region = expand_region(
        graph=graph,
        seeds=seeds,
        hops=hops,
        max_size=max_region_size,
    )

    depths = calculate_depths(graph)

    output_distances = calculate_distance_to_output(
        graph
    )

    internal_edges, boundary_edges = analyze_edges(
        graph,
        region,
    )

    exits = find_region_exits(
        graph,
        region,
    )

    nodes = build_node_evidence(
        graph=graph,
        region=region,
        scores=scores,
        depths=depths,
        output_distances=output_distances,
    )

    signal_paths = extract_signal_paths(
        graph,
        region,
    )

    suspicious_nodes = sorted(
        [
            node
            for node in region
            if scores.get(node, 0.0) >= threshold
        ],
        key=lambda node: scores.get(node, 0.0),
        reverse=True,
    )

    evidence = {
        "task": "hardware_trojan_detection",

        "decision": None,

        "decision_note": (
            "This object contains structural evidence only. "
            "The final Trojan decision is deferred to the downstream "
            "reasoning stage."
        ),

        "graph": {
            "total_nodes": int(
                graph.number_of_nodes()
            ),

            "total_edges": int(
                graph.number_of_edges()
            ),
        },

        "gnn": {
            "threshold": float(threshold),

            "top_k": int(top_k),

            "suspicious_seed_count": len(seeds),

            "suspicious_region_size": len(region),

            "suspicion": suspicion_summary(
                region,
                scores,
            ),
        },

        "suspicious_seeds": [
            {
                "gate": str(node),
                "type": gate_type(
                    graph,
                    node,
                ),
                "gnn_score": round(
                    float(scores[node]),
                    6,
                ),
            }
            for node in seeds
        ],

        "high_confidence_nodes": [
            {
                "gate": str(node),
                "type": gate_type(
                    graph,
                    node,
                ),
                "gnn_score": round(
                    float(scores[node]),
                    6,
                ),
            }
            for node in suspicious_nodes
        ],

        "region": {
            "size": len(region),

            "internal_edges": len(
                internal_edges
            ),

            "boundary_edges": len(
                boundary_edges
            ),

            "gate_types": gate_type_summary(
                graph,
                region,
            ),

            "fanin_distribution": fanin_summary(
                graph,
                region,
            ),

            "exits": exits,
        },

        "structural_evidence": {
            "primary_inputs": [
                str(node)
                for node in region
                if is_primary_input(
                    graph,
                    node,
                )
            ],

            "primary_outputs": [
                str(node)
                for node in region
                if is_primary_output(
                    graph,
                    node,
                )
            ],

            "sequential_like_gates": [
                item["gate"]
                for item in nodes
                if any(
                    token in item["type"].lower()
                    for token in (
                        "dff",
                        "ff",
                        "latch",
                        "reg",
                    )
                )
            ],

            "region_exits": exits,

            "signal_paths": signal_paths,
        },

        "nodes": nodes,
    }

    return evidence


# ============================================================
# Pretty printing
# ============================================================

def print_evidence(evidence: Dict):
    """
    Human-readable terminal representation.
    """

    print()
    print("=" * 60)
    print("STRUCTURED HARDWARE TROJAN EVIDENCE")
    print("=" * 60)

    graph_info = evidence["graph"]

    print()
    print("GRAPH")
    print("-----")
    print(
        "Total nodes :",
        graph_info["total_nodes"],
    )
    print(
        "Total edges :",
        graph_info["total_edges"],
    )

    gnn_info = evidence["gnn"]

    print()
    print("GNN")
    print("---")
    print(
        "Threshold            :",
        gnn_info["threshold"],
    )
    print(
        "Seed nodes            :",
        gnn_info["suspicious_seed_count"],
    )
    print(
        "Suspicious region     :",
        gnn_info["suspicious_region_size"],
    )

    suspicion = gnn_info["suspicion"]

    print(
        "Maximum GNN score     :",
        suspicion["max"],
    )
    print(
        "Mean regional score   :",
        suspicion["mean"],
    )
    print(
        "Median regional score :",
        suspicion["median"],
    )

    print()
    print("SUSPICIOUS SEEDS")
    print("----------------")

    for index, item in enumerate(
        evidence["suspicious_seeds"],
        1,
    ):

        print(
            f"{index:2d}. "
            f"{item['gate']:35s} "
            f"{item['type']:12s} "
            f"score={item['gnn_score']:.4f}"
        )

    region = evidence["region"]

    print()
    print("REGION")
    print("------")

    print(
        "Size           :",
        region["size"],
    )

    print(
        "Internal edges :",
        region["internal_edges"],
    )

    print(
        "Boundary edges:",
        region["boundary_edges"],
    )

    print(
        "Gate types     :",
        region["gate_types"],
    )

    print()
    print("REGION EXITS")
    print("------------")

    if not region["exits"]:

        print("None")

    else:

        for exit_info in region["exits"]:

            print(
                f"{exit_info['gate']} "
                f"({exit_info['gate_type']}) -> "
                f"{', '.join(exit_info['connections'])}"
            )

    print()
    print("SEQUENTIAL-LIKE GATES")
    print("---------------------")

    sequential = evidence[
        "structural_evidence"
    ][
        "sequential_like_gates"
    ]

    if sequential:

        for node in sequential:
            print(" ", node)

    else:

        print("None")

    print()
    print("STRUCTURED EVIDENCE READY FOR LLM")
    print("----------------------------------")

    print(
        "Fields:",
        ", ".join(
            evidence.keys()
        )
    )


# ============================================================
# Save JSON
# ============================================================

def save_evidence(
    evidence: Dict,
    output_path: Path,
):
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            evidence,
            file,
            indent=2,
        )


# ============================================================
# CLI
# ============================================================

def main():

    if len(sys.argv) < 2:

        print(
            "Usage:\n"
            "  python src/evidence.py "
            "path/to/netlist.v"
        )

        sys.exit(1)

    netlist_path = Path(
        sys.argv[1]
    )

    if not netlist_path.exists():

        raise FileNotFoundError(
            f"Netlist not found: {netlist_path}"
        )

    device = get_device()

    print(
        "========== HARDWARE TROJAN EVIDENCE =========="
    )

    print(
        "Device:",
        device,
    )

    if torch.cuda.is_available():

        print(
            "GPU:",
            torch.cuda.get_device_name(0),
        )

    print(
        "Netlist:",
        netlist_path,
    )

    print(
        "Checkpoint:",
        CHECKPOINT_PATH,
    )

    # --------------------------------------------------------
    # Parse
    # --------------------------------------------------------

    print()
    print("Parsing netlist...")

    graph = parse_netlist(
        netlist_path
    )

    print(
        "Nodes:",
        graph.number_of_nodes(),
    )

    print(
        "Edges:",
        graph.number_of_edges(),
    )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    print()
    print("Loading GNN...")

    model = load_model(
        CHECKPOINT_PATH,
        device,
    )

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    print(
        "Running GNN..."
    )

    scores, nodes = score_graph(
        model,
        graph,
        device,
    )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    evidence = build_evidence(
        graph=graph,
        scores=scores,
        threshold=DEFAULT_THRESHOLD,
        top_k=TOP_K,
        hops=HOPS,
        max_region_size=MAX_REGION_SIZE,
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print_evidence(
        evidence
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output_dir = (
        ROOT
        / "results"
        / "evidence"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / f"{netlist_path.stem}_evidence.json"
    )

    save_evidence(
        evidence,
        output_path,
    )

    print()
    print(
        "Evidence JSON saved to:",
        output_path,
    )


if __name__ == "__main__":
    main()