"""
Suspicious-region extraction for Hardware Trojan detection.

Legacy / standalone region utility that extracts a localized suspicious subgraph
around top GNN seed nodes. This module is retained for backward compatibility.
For full structured evidence generation, use src/evidence.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple

import networkx as nx
import numpy as np
import torch

from dataset import graph_to_pyg
from gnn import TrojanGNN
from parser import parse_netlist
from evidence import (
    CHECKPOINT_PATH,
    DEFAULT_THRESHOLD,
    HOPS,
    MAX_REGION_SIZE,
    TOP_K,
    expand_region,
    gate_type,
    get_device,
    is_primary_input,
    is_primary_output,
    load_model,
    score_graph,
    select_suspicious_seeds,
)


@dataclass
class SuspiciousRegion:
    """Localized candidate subgraph summary."""
    nodes: Set[str]
    seed_nodes: List[str]
    internal_edges: int
    boundary_edges: int
    gate_types: Dict[str, int]
    primary_inputs: int
    primary_outputs: int
    flip_flops: int


def is_sequential_gate(graph: nx.DiGraph, node: str) -> bool:
    """Check if node is a flip-flop or sequential element."""
    gt = gate_type(graph, node).lower()
    return any(token in gt for token in ("dff", "ff", "latch", "reg"))


def extract_suspicious_region(
    graph: nx.DiGraph,
    scores: Dict[str, float],
    top_k: int = TOP_K,
    hops: int = HOPS,
    max_region_size: int = MAX_REGION_SIZE,
) -> SuspiciousRegion:
    """Extract candidate region around highest-scoring seed gates."""
    ranked = sorted(scores.items(), key=lambda item: (-item[1], str(item[0])))
    seeds = [node for node, _ in ranked[:top_k]]
    region_nodes = expand_region(graph, seeds=seeds, hops=hops, max_size=max_region_size)

    # Edge breakdown
    internal = 0
    boundary = 0
    for u, v in graph.edges():
        u_in = u in region_nodes
        v_in = v in region_nodes
        if u_in and v_in:
            internal += 1
        elif u_in or v_in:
            boundary += 1

    from collections import Counter
    gt_counts = dict(Counter(gate_type(graph, n) for n in region_nodes))
    pi_count = sum(1 for n in region_nodes if is_primary_input(graph, n))
    po_count = sum(1 for n in region_nodes if is_primary_output(graph, n))
    ff_count = sum(1 for n in region_nodes if is_sequential_gate(graph, n))

    return SuspiciousRegion(
        nodes=region_nodes,
        seed_nodes=seeds,
        internal_edges=internal,
        boundary_edges=boundary,
        gate_types=gt_counts,
        primary_inputs=pi_count,
        primary_outputs=po_count,
        flip_flops=ff_count,
    )


def region_description(graph: nx.DiGraph, region: SuspiciousRegion) -> str:
    """Generate textual summary of the suspicious region."""
    lines = [
        "Suspicious Region Summary:",
        f"  Total gates     : {len(region.nodes)}",
        f"  Seed gates      : {len(region.seed_nodes)}",
        f"  Internal edges  : {region.internal_edges}",
        f"  Boundary edges  : {region.boundary_edges}",
        f"  Primary inputs  : {region.primary_inputs}",
        f"  Primary outputs : {region.primary_outputs}",
        f"  Sequential (DFF): {region.flip_flops}",
        f"  Gate types      : {region.gate_types}",
    ]
    return "\n".join(lines)


def analyze_netlist(netlist_path: str | Path):
    """Analyze a single netlist file and print suspicious region summary."""
    path = Path(netlist_path)
    if not path.exists():
        raise FileNotFoundError(f"Netlist not found: {path}")

    graph = parse_netlist(path)
    device = get_device()
    model = load_model(CHECKPOINT_PATH, device=device)
    scores, _ = score_graph(model, graph, device)
    region = extract_suspicious_region(graph, scores)

    print(f"Netlist: {path}")
    print(region_description(graph, region))
    return graph, region


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage:\n  python src/region.py <netlist.v>")
        sys.exit(1)
    analyze_netlist(sys.argv[1])
