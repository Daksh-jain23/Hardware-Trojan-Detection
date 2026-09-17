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
# Structural region description
# ============================================================

def region_description(
    graph,
    region: SuspiciousRegion,
):
    """
    Convert a suspicious region into a compact textual description.

    This is NOT the final LLM prompt yet.

    It is the intermediate representation between:

        GNN → region → LLM
    """

    lines = []

    lines.append(
        f"Region size: {len(region.nodes)} gates"
    )

    lines.append(
        f"Seed gates: {len(region.seed_nodes)}"
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
    print("========== SUSPICIOUS REGION ==========")

    print(
        "Region size:",
        len(region.nodes)
    )

    print(
        "Seed gates:",
        region.seed_nodes
    )

    print()

    print(
        region_description(
            graph,
            region,
        )
    )

    return graph, region


# ============================================================
# Command-line interface
# ============================================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) != 2:

        print(
            "Usage:"
        )

        print(
            "python src/region.py <netlist.v>"
        )

        sys.exit(1)

    analyze_netlist(
        sys.argv[1]
    )