"""
Suspicious-region extraction for Hardware Trojan detection.

Pipeline:

    netlist
       ↓
    GNN
       ↓
    gate suspicion scores
       ↓
    top suspicious gates
       ↓
    graph neighborhood expansion
       ↓
    suspicious region

The important idea is that we DO NOT send the complete circuit
to the LLM.

The GNN first narrows the circuit down to a small region.
The region is then converted into structural text for the LLM.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np
import torch
import networkx as nx

from parser import parse_netlist
from dataset import graph_to_pyg
from gnn import TrojanGNN


# ============================================================
# Configuration
# ============================================================

CHECKPOINT_PATH = Path("checkpoints/trojan_gnn.pt")

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

HIDDEN_DIM = 64
DROPOUT = 0.2

# Number of highest-scoring gates used as seeds.
TOP_K = 15

# Expand suspicious seeds by graph hops.
HOPS = 2

# Maximum number of gates sent to the next stage.
MAX_REGION_SIZE = 50


# ============================================================
# Region object
# ============================================================

@dataclass
class SuspiciousRegion:

    nodes: Set[str]

    seed_nodes: List[str]

    scores: Dict[str, float]

    source: str | None = None

    def __len__(self):
        return len(self.nodes)


@dataclass
class RefinedRegion:

    nodes: Set[str]

    seed_nodes: List[str]

    pruned_nodes: Set[str]

    scores: Dict[str, float]

    retention_ratio: float

    source: str | None = None

    def __len__(self):
        return len(self.nodes)


# ============================================================
# Load trained GNN
# ============================================================

def load_model(
    input_dim: int,
    checkpoint_path: Path = CHECKPOINT_PATH,
):
    """
    Load the trained TrojanGNN checkpoint.
    """

    if not checkpoint_path.exists():

        raise FileNotFoundError(
            f"GNN checkpoint not found: "
            f"{checkpoint_path.resolve()}"
        )

    model = TrojanGNN(
        input_dim=input_dim,
        hidden_dim=HIDDEN_DIM,
        dropout=DROPOUT,
    )

    checkpoint = torch.load(
        checkpoint_path,
        map_location=DEVICE,
        weights_only=False,
    )

    # Support both:
    #
    # torch.save(model.state_dict(), ...)
    #
    # and:
    #
    # torch.save({"model_state_dict": ...}, ...)
    #
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:

        state_dict = checkpoint["model_state_dict"]

    else:

        state_dict = checkpoint

    model.load_state_dict(state_dict)

    model.to(DEVICE)
    model.eval()

    return model


# ============================================================
# GNN inference
# ============================================================

@torch.no_grad()
def score_graph(
    model,
    graph,
):
    """
    Run the trained GNN on one complete circuit.

    Returns:

        scores:
            Dictionary:
                gate_name -> Trojan probability

        nodes:
            Node ordering used by the PyG graph.
    """

    data = graph_to_pyg(graph)
    data = data.to(DEVICE)

    output = model(
        data.x,
        data.edge_index,
    )

    # Some models return [N].
    # Some return [N, 1].
    if output.ndim == 2 and output.shape[1] == 1:

        logits = output[:, 0]

    else:

        logits = output

    probabilities = torch.sigmoid(logits)

    probabilities = probabilities.detach().cpu().numpy()

    # graph_to_pyg uses compute_node_features internally,
    # therefore recreate the same node ordering.
    from features import compute_node_features

    _, nodes = compute_node_features(graph)

    scores = {
        node: float(probability)
        for node, probability in zip(
            nodes,
            probabilities,
        )
    }

    return scores, nodes


# ============================================================
# Select suspicious seeds
# ============================================================

def select_top_k(
    scores: Dict[str, float],
    k: int = TOP_K,
):
    """
    Select the K highest-scoring gates.
    """

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        node
        for node, _ in ranked[:k]
    ]


# ============================================================
# Region expansion
# ============================================================

def expand_region(
    graph,
    seed_nodes: List[str],
    scores: Dict[str, float],
    hops: int = HOPS,
    max_size: int = MAX_REGION_SIZE,
):
    """
    Expand suspicious seeds through the circuit topology.

    We use an undirected view for neighborhood discovery because
    both upstream and downstream context are useful.

    Nodes are ranked by GNN suspicion score when the region needs
    to be capped.
    """

    region = set(seed_nodes)

    frontier = set(seed_nodes)

    undirected = graph.to_undirected(as_view=True)

    for _ in range(hops):

        next_frontier = set()

        for node in frontier:

            if node not in graph:
                continue

            for neighbor in undirected.neighbors(node):

                if neighbor not in region:

                    next_frontier.add(neighbor)

        if not next_frontier:
            break

        region.update(next_frontier)

        frontier = next_frontier

        if len(region) >= max_size:
            break

    # --------------------------------------------------------
    # Limit region size.
    #
    # Keep the most suspicious gates.
    # --------------------------------------------------------

    if len(region) > max_size:

        ranked = sorted(
            region,
            key=lambda node: scores.get(node, 0.0),
            reverse=True,
        )

        region = set(
            ranked[:max_size]
        )

    return region


# ============================================================
# Build suspicious region
# ============================================================

def extract_region(
    graph,
    scores: Dict[str, float],
    top_k: int = TOP_K,
    hops: int = HOPS,
    max_size: int = MAX_REGION_SIZE,
):
    """
    Convert GNN scores into one suspicious circuit region.
    """

    seeds = select_top_k(
        scores,
        k=top_k,
    )

    region_nodes = expand_region(
        graph,
        seeds,
        scores,
        hops=hops,
        max_size=max_size,
    )

    return SuspiciousRegion(
        nodes=region_nodes,
        seed_nodes=seeds,
        scores=scores,
    )


# ============================================================
# Heuristic Suspicious-Region Refinement
# ============================================================

def refine_suspicious_region(
    graph: nx.DiGraph,
    region: SuspiciousRegion,
    scores: Dict[str, float],
    gnn_threshold: float = 0.95,
    prune_threshold: float = 0.30,
    preserve_critical_paths: bool = True,
    preserve_sequential: bool = True,
) -> RefinedRegion:
    """
    Graph-theoretic suspicious-region refinement for Hardware Trojan detection.

    Prunes non-suspicious peripheral leaves that dilute internal connectivity and
    add unnecessary token overhead, while guaranteeing the preservation of core
    seeds, sequential trigger elements, and active trigger-to-payload reconnection paths.

    Parameters:
    -----------
    graph: nx.DiGraph
        Complete netlist graph
    region: SuspiciousRegion
        Initial unrefined candidate region
    scores: Dict[str, float]
        GNN node suspiciousness probabilities
    gnn_threshold: float
        Threshold defining high-confidence seeds that cannot be pruned
    prune_threshold: float
        Suspicion boundary below which peripheral leaf nodes are pruned
    preserve_critical_paths: bool
        Whether to protect all nodes along shortest paths between seeds and exits
    preserve_sequential: bool
        Whether to protect sequential flip-flops/registers connected to seeds

    Returns:
    --------
    RefinedRegion: Compact, high-precision candidate region
    """
    candidate_nodes = set(region.nodes)
    if not candidate_nodes:
        return RefinedRegion(
            nodes=set(),
            seed_nodes=[],
            pruned_nodes=set(),
            scores=scores,
            retention_ratio=1.0,
            source=region.source,
        )

    # 1. Core Anchors (High-confidence seeds)
    core_anchors = {
        n for n in candidate_nodes
        if scores.get(n, 0.0) >= gnn_threshold or n in region.seed_nodes
    }

    # 2. Sequential State Anchors (Flip-flops, registers characteristic of triggers)
    sequential_anchors = set()
    if preserve_sequential:
        for n in candidate_nodes:
            if n not in graph:
                continue
            gate_data = graph.nodes[n]
            gtype = str(gate_data.get("gate_type", "")).lower()
            if any(k in gtype for k in ["dff", "reg", "latch"]):
                # Retain sequential gates with moderate score or connected to seeds
                if scores.get(n, 0.0) >= 0.40 or any(
                    pred in core_anchors for pred in graph.predecessors(n)
                ) or any(
                    succ in core_anchors for succ in graph.successors(n)
                ):
                    sequential_anchors.add(n)

    # 3. Critical Path Protection (Seed-to-Exit Reconnection Paths)
    critical_path_nodes = set()
    if preserve_critical_paths:
        sub_undirected = graph.subgraph(candidate_nodes).to_undirected()
        exit_nodes = {
            n for n in candidate_nodes
            if any(succ not in candidate_nodes for succ in graph.successors(n))
        }

        for seed in core_anchors:
            for ex in exit_nodes:
                if nx.has_path(sub_undirected, seed, ex):
                    try:
                        for path in nx.all_shortest_paths(sub_undirected, seed, ex):
                            critical_path_nodes.update(path)
                    except Exception:
                        pass

    # Protected set: cannot be pruned under any circumstances
    protected_nodes = core_anchors.union(sequential_anchors).union(critical_path_nodes)

    # 4. Multi-pass Iterative Leaf Pruning
    current_nodes = set(candidate_nodes)
    changed = True
    while changed:
        changed = False
        sub_current = graph.subgraph(current_nodes).to_undirected()
        to_prune = set()

        for node in current_nodes:
            if node in protected_nodes:
                continue

            node_score = scores.get(node, 0.0)
            internal_degree = sub_current.degree(node)

            # Prune dead-end leaf nodes with low GNN suspicion
            if node_score < prune_threshold and internal_degree <= 1:
                to_prune.add(node)

        if to_prune:
            current_nodes -= to_prune
            changed = True

    pruned_nodes = candidate_nodes - current_nodes
    retention_ratio = len(current_nodes) / len(candidate_nodes) if candidate_nodes else 1.0

    return RefinedRegion(
        nodes=current_nodes,
        seed_nodes=region.seed_nodes,
        pruned_nodes=pruned_nodes,
        scores=scores,
        retention_ratio=round(retention_ratio, 4),
        source=region.source,
    )


# ============================================================
# Structural region description
# ============================================================

def region_description(
    graph,
    region: SuspiciousRegion | RefinedRegion,
):
    """
    Convert a suspicious or refined region into a compact textual description.
    """
    lines = []

    lines.append(
        f"Region size: {len(region.nodes)} gates"
    )

    lines.append(
        f"Seed gates: {len(region.seed_nodes)}"
    )

    if isinstance(region, RefinedRegion) and region.pruned_nodes:
        lines.append(
            f"Pruned peripheral gates: {len(region.pruned_nodes)} "
            f"(compression ratio: {1.0 - region.retention_ratio:.1%})"
        )

    lines.append("")

    # --------------------------------------------------------
    # Rank gates by GNN suspicion.
    # --------------------------------------------------------

    ranked_nodes = sorted(
        region.nodes,
        key=lambda node: region.scores.get(node, 0.0),
        reverse=True,
    )

    lines.append("Suspicious gates:")

    for node in ranked_nodes:

        data = graph.nodes[node]

        gate_type = data.get(
            "gate_type",
            "unknown",
        )

        score = region.scores.get(
            node,
            0.0,
        )

        predecessors = list(
            graph.predecessors(node)
        )

        successors = list(
            graph.successors(node)
        )

        lines.append(
            f"{node}: "
            f"type={gate_type}, "
            f"score={score:.4f}, "
            f"fanin={len(predecessors)}, "
            f"fanout={len(successors)}"
        )

    # --------------------------------------------------------
    # Internal / external connections.
    # --------------------------------------------------------

    internal_edges = 0
    boundary_edges = 0

    for source, target in graph.edges():

        source_inside = source in region.nodes
        target_inside = target in region.nodes

        if source_inside and target_inside:

            internal_edges += 1

        elif source_inside or target_inside:

            boundary_edges += 1

    lines.append("")

    lines.append(
        f"Internal edges: {internal_edges}"
    )

    lines.append(
        f"Boundary edges: {boundary_edges}"
    )

    # --------------------------------------------------------
    # Boundary exits.
    #
    # These are particularly important because a Trojan
    # payload eventually reconnects to legitimate logic.
    # --------------------------------------------------------

    exits = []

    for node in region.nodes:

        for successor in graph.successors(node):

            if successor not in region.nodes:

                exits.append(
                    (node, successor)
                )

    lines.append("")

    lines.append(
        f"Region exits: {len(exits)}"
    )

    if exits:

        lines.append(
            "Exit connections:"
        )

        for source, target in exits:

            lines.append(
                f"  {source} -> {target}"
            )

    return "\n".join(lines)


# ============================================================
# Full inference
# ============================================================

def analyze_netlist(
    netlist_path: str | Path,
):
    """
    Complete GNN → suspicious region pipeline.
    """

    netlist_path = Path(
        netlist_path
    )

    print()
    print("========== GNN REGION ANALYSIS ==========")

    print(
        "Device:",
        DEVICE,
    )

    print(
        "Netlist:",
        netlist_path,
    )

    # --------------------------------------------------------
    # Parse
    # --------------------------------------------------------

    graph = parse_netlist(
        netlist_path
    )

    print(
        "Nodes:",
        graph.number_of_nodes()
    )

    print(
        "Edges:",
        graph.number_of_edges()
    )

    # --------------------------------------------------------
    # Convert once to determine feature dimension.
    # --------------------------------------------------------

    data = graph_to_pyg(
        graph
    )

    input_dim = data.x.shape[1]

    print(
        "Features:",
        input_dim
    )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model = load_model(
        input_dim
    )

    # --------------------------------------------------------
    # GNN inference
    # --------------------------------------------------------

    scores, nodes = score_graph(
        model,
        graph,
    )

    # --------------------------------------------------------
    # Region extraction
    # --------------------------------------------------------

    region = extract_region(
        graph,
        scores,
    )

    region.source = str(
        netlist_path
    )

    # --------------------------------------------------------
    # Print ranked gates
    # --------------------------------------------------------

    print()
    print("========== TOP SUSPICIOUS GATES ==========")

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    for rank, (node, score) in enumerate(
        ranked[:TOP_K],
        start=1,
    ):

        gate_type = graph.nodes[node].get(
            "gate_type",
            "unknown",
        )

        print(
            f"{rank:2d}. "
            f"{node:35s} "
            f"{gate_type:12s} "
            f"score={score:.4f}"
        )

    # --------------------------------------------------------
    # Region information
    # --------------------------------------------------------

    print()
    print("========== NAIVE SUSPICIOUS REGION ==========")
    print("Region size:", len(region.nodes))
    print("Seed gates :", len(region.seed_nodes))
    print()
    print(region_description(graph, region))

    # --------------------------------------------------------
    # Phase 3: Heuristic-Guided Suspicious Region Refinement
    # --------------------------------------------------------
    print()
    print("========== REFINED SUSPICIOUS REGION ==========")
    refined_region = refine_suspicious_region(
        graph=graph,
        region=region,
        scores=scores,
    )

    print("Refined size           :", len(refined_region.nodes))
    print("Pruned peripheral gates:", len(refined_region.pruned_nodes))
    print("Size compression ratio :", f"{1.0 - refined_region.retention_ratio:.1%}")
    if refined_region.pruned_nodes:
        print("Pruned nodes           :", sorted(refined_region.pruned_nodes)[:10])

    print()
    print(region_description(graph, refined_region))

    return graph, region, refined_region


# ============================================================
# Command-line interface
# ============================================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) != 2:
        print("Usage:")
        print("python src/region.py <netlist.v>")
        sys.exit(1)

    analyze_netlist(sys.argv[1])