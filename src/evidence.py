"""
Structured evidence extraction for Hardware Trojan detection.

Converts GNN suspicion scores and circuit graph topology into a structured
dictionary of evidence that can be analyzed by downstream reasoning stages
or the LLM agent without exposing raw netlist Verilog syntax.
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

# Paths and default hyperparameters
ROOT = Path(__file__).resolve().parent.parent
CHECKPOINT_PATH = ROOT / "checkpoints" / "trojan_gnn.pt"

DEFAULT_THRESHOLD = 0.95
TOP_K = 15
HOPS = 2
MAX_REGION_SIZE = 50
MAX_DETAILED_GATES = 50


def get_device() -> torch.device:
    """Select CUDA if available, otherwise CPU."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model(
    checkpoint_path: Path = CHECKPOINT_PATH,
    device: torch.device | None = None,
):
    """Load the trained TrojanGNN model from disk."""
    if device is None:
        device = get_device()

    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"GNN checkpoint not found: {checkpoint_path}\nRun train_gnn.py first."
        )

    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)

    # Support checkpoint dict with metadata or raw state dict
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
        input_dim = int(checkpoint.get("input_dim", 41))
        hidden_dim = int(checkpoint.get("hidden_dim", 64))
        dropout = float(checkpoint.get("dropout", 0.2))
    else:
        state_dict = checkpoint
        input_dim = 41
        hidden_dim = 64
        dropout = 0.2

    model = TrojanGNN(input_dim=input_dim, hidden_dim=hidden_dim, dropout=dropout)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model


@torch.no_grad()
def score_graph(model, graph, device: torch.device):
    """
    Run GNN inference on a circuit graph.

    Returns:
        scores: Dict mapping gate name -> Trojan probability (float)
        nodes: List of gate names in the order used by graph_to_pyg
    """
    data = graph_to_pyg(graph).to(device)
    logits = model(data.x, data.edge_index)
    probabilities = torch.sigmoid(logits).detach().cpu().numpy().reshape(-1)

    nodes = list(graph.nodes())
    if len(nodes) != len(probabilities):
        raise RuntimeError("Node count mismatch between NetworkX graph and PyG graph.")

    scores = {node: float(prob) for node, prob in zip(nodes, probabilities)}
    return scores, nodes


def select_suspicious_seeds(
    scores: Dict,
    top_k: int = TOP_K,
    threshold: float = DEFAULT_THRESHOLD,
) -> List:
    """Select nodes whose GNN scores meet or exceed the detection threshold."""
    ranked = sorted(scores.items(), key=lambda item: (-item[1], str(item[0])), reverse=True)
    return [node for node, score in ranked if score >= threshold]


def select_ranked_context_nodes(scores: Dict, top_k: int = TOP_K) -> List:
    """Return top-k ranked nodes used as structural context even if below threshold."""
    ranked = sorted(scores.items(), key=lambda item: (-item[1], str(item[0])))
    return [node for node, _ in ranked[:top_k]]


def expand_region(
    graph: nx.DiGraph,
    seeds: Iterable,
    hops: int = HOPS,
    max_size: int = MAX_REGION_SIZE,
) -> Set:
    """
    Expand candidate seed gates through k-hop graph connectivity.
    Expands in both directions (predecessors and successors).
    """
    region = set(seeds)
    frontier = set(seeds)

    for _ in range(hops):
        next_frontier = set()
        for node in frontier:
            if node not in graph:
                continue
            next_frontier.update(graph.predecessors(node))
            next_frontier.update(graph.successors(node))

        next_frontier -= region
        if not next_frontier:
            break

        remaining = max_size - len(region)
        if remaining <= 0:
            break

        if len(next_frontier) > remaining:
            # Deterministic ordering for reproducibility across runs
            next_frontier = set(sorted(next_frontier, key=str)[:remaining])

        region.update(next_frontier)
        frontier = next_frontier

    return region


def gate_type(graph, node) -> str:
    """Retrieve gate cell type from node attributes."""
    data = graph.nodes[node]
    for key in ("gate_type", "type", "cell_type", "kind"):
        value = data.get(key)
        if value is not None:
            return str(value)
    return "UNKNOWN"


def is_primary_input(graph, node) -> bool:
    """Check if node is a primary input."""
    data = graph.nodes[node]
    node_type = gate_type(graph, node).upper()
    if node_type in {"PI", "PRIMARY_INPUT", "INPUT"}:
        return True
    if graph.in_degree(node) == 0:
        return True
    return bool(data.get("is_primary_input", False))


def is_primary_output(graph, node) -> bool:
    """Check if node is a primary output."""
    data = graph.nodes[node]
    node_type = gate_type(graph, node).upper()
    if node_type in {"PO", "PRIMARY_OUTPUT", "OUTPUT"}:
        return True
    if graph.out_degree(node) == 0:
        return True
    return bool(data.get("is_primary_output", False))


def calculate_depths(graph: nx.DiGraph):
    """Calculate BFS distance of each gate from circuit inputs."""
    depths = {}
    sources = [node for node in graph.nodes() if graph.in_degree(node) == 0]
    queue = deque()

    for node in sources:
        depths[node] = 0
        queue.append(node)

    while queue:
        node = queue.popleft()
        current_depth = depths[node]
        for successor in graph.successors(node):
            candidate = current_depth + 1
            if successor not in depths or candidate < depths[successor]:
                depths[successor] = candidate
                queue.append(successor)

    fallback = max(depths.values(), default=0) + 1
    for node in graph.nodes():
        depths.setdefault(node, fallback)

    return depths


def calculate_distance_to_output(graph: nx.DiGraph):
    """Calculate BFS distance of each gate to circuit outputs."""
    reversed_graph = graph.reverse(copy=False)
    distances = {}
    sources = [node for node in graph.nodes() if graph.out_degree(node) == 0]
    queue = deque()

    for node in sources:
        distances[node] = 0
        queue.append(node)

    while queue:
        node = queue.popleft()
        current_distance = distances[node]
        for predecessor in reversed_graph.successors(node):
            candidate = current_distance + 1
            if predecessor not in distances or candidate < distances[predecessor]:
                distances[predecessor] = candidate
                queue.append(predecessor)

    fallback = max(distances.values(), default=0) + 1
    for node in graph.nodes():
        distances.setdefault(node, fallback)

    return distances


def analyze_edges(graph: nx.DiGraph, region: Set):
    """Separate edges into internal (both inside region) and boundary (one inside)."""
    internal = []
    boundary = []
    for source, target in graph.edges():
        source_inside = source in region
        target_inside = target in region
        if source_inside and target_inside:
            internal.append((source, target))
        elif source_inside or target_inside:
            boundary.append((source, target))
    return internal, boundary


def find_region_exits(graph: nx.DiGraph, region: Set):
    """Find gates inside the region driving signals outside the region."""
    exits = []
    for node in region:
        outside_successors = [s for s in graph.successors(node) if s not in region]
        if outside_successors:
            exits.append({
                "gate": str(node),
                "gate_type": gate_type(graph, node),
                "connections": [str(x) for x in outside_successors],
            })
    return exits


def extract_signal_paths(graph: nx.DiGraph, region: Set, max_paths: int = 30):
    """Extract shortest paths inside the region subgraph to illustrate signal flow."""
    paths = []
    subgraph = graph.subgraph(region)
    try:
        sources = [node for node in subgraph.nodes() if subgraph.in_degree(node) == 0]
        targets = [node for node in subgraph.nodes() if subgraph.out_degree(node) == 0]

        for source in sources:
            for target in targets:
                if len(paths) >= max_paths:
                    break
                if source == target:
                    continue
                try:
                    path = nx.shortest_path(subgraph, source, target)
                except nx.NetworkXNoPath:
                    continue
                paths.append([{"gate": str(n), "type": gate_type(graph, n)} for n in path])
            if len(paths) >= max_paths:
                break
    except Exception:
        pass
    return paths


def build_node_evidence(graph: nx.DiGraph, region: Set, scores: Dict, depths: Dict, output_distances: Dict):
    """Build detailed property dictionary for top-scoring gates in the region."""
    ranked = sorted(region, key=lambda node: scores.get(node, 0.0), reverse=True)[:MAX_DETAILED_GATES]
    evidence = []
    region_set = set(region)

    for node in ranked:
        predecessors = list(graph.predecessors(node))
        successors = list(graph.successors(node))
        outside_successors = [s for s in successors if s not in region_set]

        evidence.append({
            "gate": str(node),
            "type": gate_type(graph, node),
            "gnn_score": round(float(scores.get(node, 0.0)), 6),
            "fanin": int(graph.in_degree(node)),
            "fanout": int(graph.out_degree(node)),
            "depth_from_input": int(depths.get(node, 0)),
            "distance_to_output": int(output_distances.get(node, 0)),
            "primary_input": is_primary_input(graph, node),
            "primary_output": is_primary_output(graph, node),
            "inputs": [str(x) for x in predecessors],
            "outputs": [str(x) for x in successors],
            "region_exit": bool(outside_successors),
            "external_outputs": [str(x) for x in outside_successors],
        })
    return evidence


def gate_type_summary(graph: nx.DiGraph, region: Set):
    """Return count of each gate type in the region."""
    counts = Counter(gate_type(graph, node) for node in region)
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def fanin_summary(graph: nx.DiGraph, region: Set):
    """Return fan-in distribution of gates in the region."""
    counts = Counter(graph.in_degree(node) for node in region)
    return {str(k): int(v) for k, v in sorted(counts.items())}


def suspicion_summary(region: Set, scores: Dict):
    """Compute summary statistics for GNN scores within the region."""
    values = [float(scores.get(node, 0.0)) for node in region]
    if not values:
        return {"max": 0.0, "mean": 0.0, "median": 0.0, "min": 0.0}

    return {
        "max": round(max(values), 6),
        "mean": round(float(np.mean(values)), 6),
        "median": round(float(np.median(values)), 6),
        "min": round(min(values), 6),
    }


def build_evidence(
    graph: nx.DiGraph,
    scores: Dict,
    threshold: float = DEFAULT_THRESHOLD,
    top_k: int = TOP_K,
    hops: int = HOPS,
    max_region_size: int = MAX_REGION_SIZE,
):
    """
    Construct the structured evidence object for a circuit given GNN scores.
    Reports graph statistics, seed nodes, k-hop region, exits, and signal paths.
    """
    suspicious_seeds = select_suspicious_seeds(scores=scores, top_k=top_k, threshold=threshold)
    ranked_context_nodes = select_ranked_context_nodes(scores=scores, top_k=top_k)

    # Use seeds + ranked context to anchor the region expansion
    region_anchors = list(dict.fromkeys(suspicious_seeds + ranked_context_nodes))
    region = expand_region(graph=graph, seeds=region_anchors, hops=hops, max_size=max_region_size)

    depths = calculate_depths(graph)
    output_distances = calculate_distance_to_output(graph)
    internal_edges, boundary_edges = analyze_edges(graph, region)
    exits = find_region_exits(graph, region)
    nodes = build_node_evidence(
        graph=graph,
        region=region,
        scores=scores,
        depths=depths,
        output_distances=output_distances,
    )
    signal_paths = extract_signal_paths(graph, region)

    suspicious_nodes = sorted(
        [node for node in region if scores.get(node, 0.0) >= threshold],
        key=lambda node: scores.get(node, 0.0),
        reverse=True,
    )

    evidence = {
        "task": "hardware_trojan_detection",
        "decision": None,
        "decision_note": (
            "This object contains structural evidence only. "
            "The final Trojan decision is deferred to the downstream reasoning stage."
        ),
        "graph": {
            "total_nodes": int(graph.number_of_nodes()),
            "total_edges": int(graph.number_of_edges()),
        },
        "gnn": {
            "threshold": float(threshold),
            "top_k": int(top_k),
            "suspicious_seed_count": len(suspicious_seeds),
            "ranked_context_count": len(ranked_context_nodes),
            "suspicious_region_size": len(region),
            "suspicion": suspicion_summary(region, scores),
        },
        "suspicious_seeds": [
            {
                "gate": str(node),
                "type": gate_type(graph, node),
                "gnn_score": round(float(scores[node]), 6),
            }
            for node in suspicious_seeds
        ],
        "ranked_context_nodes": [
            {
                "gate": str(node),
                "type": gate_type(graph, node),
                "gnn_score": round(float(scores[node]), 6),
            }
            for node in ranked_context_nodes
        ],
        "high_confidence_nodes": [
            {
                "gate": str(node),
                "type": gate_type(graph, node),
                "gnn_score": round(float(scores[node]), 6),
            }
            for node in suspicious_nodes
        ],
        "region": {
            "size": len(region),
            "internal_edges": len(internal_edges),
            "boundary_edges": len(boundary_edges),
            "gate_types": gate_type_summary(graph, region),
            "fanin_distribution": fanin_summary(graph, region),
            "exits": exits,
        },
        "structural_evidence": {
            "primary_inputs": [str(node) for node in region if is_primary_input(graph, node)],
            "primary_outputs": [str(node) for node in region if is_primary_output(graph, node)],
            "sequential_like_gates": [
                item["gate"]
                for item in nodes
                if any(token in item["type"].lower() for token in ("dff", "ff", "latch", "reg"))
            ],
            "internal_edge_density": round(len(internal_edges) / max(1, len(region)), 4),
            "exit_ratio": round(len(exits) / max(1, len(region)), 4),
            "multi_input_gates": [item["gate"] for item in nodes if item["fanin"] >= 3],
            "payload_candidate_gates": [
                item["gate"]
                for item in nodes
                if item.get("region_exit")
                and any(op in item["type"].lower() for op in ("xor", "xnr", "xnor", "mux", "and", "or", "inv"))
            ],
            "region_exits": exits,
            "signal_paths": signal_paths,
        },
        "nodes": nodes,
    }
    return evidence


def print_evidence(evidence: Dict):
    """Print a clean terminal summary of the extracted evidence."""
    print("\n" + "=" * 60)
    print("STRUCTURED HARDWARE TROJAN EVIDENCE")
    print("=" * 60)

    graph_info = evidence["graph"]
    print("\nGRAPH\n-----")
    print("Total nodes :", graph_info["total_nodes"])
    print("Total edges :", graph_info["total_edges"])

    gnn_info = evidence["gnn"]
    print("\nGNN\n---")
    print("Threshold            :", gnn_info["threshold"])
    print("Seed nodes           :", gnn_info["suspicious_seed_count"])
    print("Suspicious region    :", gnn_info["suspicious_region_size"])

    suspicion = gnn_info["suspicion"]
    print("Maximum GNN score    :", suspicion["max"])
    print("Mean regional score  :", suspicion["mean"])
    print("Median regional score:", suspicion["median"])

    print("\nSUSPICIOUS SEEDS\n----------------")
    for index, item in enumerate(evidence["suspicious_seeds"], 1):
        print(f"{index:2d}. {item['gate']:35s} {item['type']:12s} score={item['gnn_score']:.4f}")

    region = evidence["region"]
    print("\nREGION\n------")
    print("Size           :", region["size"])
    print("Internal edges :", region["internal_edges"])
    print("Boundary edges :", region["boundary_edges"])
    print("Gate types     :", region["gate_types"])

    print("\nREGION EXITS\n------------")
    if not region["exits"]:
        print("None")
    else:
        for exit_info in region["exits"]:
            print(f"{exit_info['gate']} ({exit_info['gate_type']}) -> {', '.join(exit_info['connections'])}")

    print("\nSEQUENTIAL-LIKE GATES\n---------------------")
    sequential = evidence["structural_evidence"]["sequential_like_gates"]
    if sequential:
        for node in sequential:
            print(" ", node)
    else:
        print("None")

    print("\nSTRUCTURED EVIDENCE READY FOR LLM\n----------------------------------")
    print("Fields:", ", ".join(evidence.keys()))


def save_evidence(evidence: Dict, output_path: Path):
    """Save evidence dictionary to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(evidence, file, indent=2)


def main():
    if len(sys.argv) < 2:
        print("Usage:\n  python src/evidence.py path/to/netlist.v")
        sys.exit(1)

    netlist_path = Path(sys.argv[1])
    if not netlist_path.exists():
        raise FileNotFoundError(f"Netlist not found: {netlist_path}")

    device = get_device()
    print("========== HARDWARE TROJAN EVIDENCE ==========")
    print("Device     :", device)
    if torch.cuda.is_available():
        print("GPU        :", torch.cuda.get_device_name(0))
    print("Netlist    :", netlist_path)
    print("Checkpoint :", CHECKPOINT_PATH)

    print("\nParsing netlist...")
    graph = parse_netlist(netlist_path)
    print("Nodes:", graph.number_of_nodes())
    print("Edges:", graph.number_of_edges())

    print("\nLoading GNN...")
    model = load_model(CHECKPOINT_PATH, device)

    print("Running GNN...")
    scores, nodes = score_graph(model, graph, device)

    evidence = build_evidence(
        graph=graph,
        scores=scores,
        threshold=DEFAULT_THRESHOLD,
        top_k=TOP_K,
        hops=HOPS,
        max_region_size=MAX_REGION_SIZE,
    )

    print_evidence(evidence)

    output_dir = ROOT / "results" / "evidence"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{netlist_path.stem}_evidence.json"
    save_evidence(evidence, output_path)
    print("\nEvidence JSON saved to:", output_path)


if __name__ == "__main__":
    main()
