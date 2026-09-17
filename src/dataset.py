"""
Dataset utilities for Hardware Trojan detection.

Each Verilog netlist becomes one graph.

The GNN performs node-level classification:

    0 -> normal gate
    1 -> Trojan gate

We keep complete circuits as separate samples so that later we can
split by circuit family rather than randomly splitting individual nodes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import torch
from torch_geometric.data import Data

from parser import parse_netlist


# ============================================================
# Configuration
# ============================================================

DATA_ROOT = Path("data/TRIT-TS")


# These are the circuit families present in the TRIT-TS dataset.
# We discover them automatically from the directory structure.
FAMILIES = [
    "s13207",
    "s1423",
    "s15850",
    "s35932",
]


# ============================================================
# Dataset sample
# ============================================================

@dataclass
class GraphSample:
    """
    One complete netlist graph.

    graph:
        NetworkX directed graph.

    family:
        Circuit family, e.g. s13207.

    source:
        Original Verilog file.
    """

    graph: object
    family: str
    source: str


# ============================================================
# NetworkX -> PyTorch Geometric
# ============================================================

def graph_to_pyg(graph) -> Data:
    """
    Convert a parsed NetworkX graph into a PyTorch Geometric Data object.
    """

    # Import here to avoid unnecessary circular imports.
    from features import compute_node_features

    X, nodes = compute_node_features(graph)

    # --------------------------------------------------------
    # Node labels
    # --------------------------------------------------------

    y = torch.tensor(
        [
            1 if graph.nodes[node].get("is_trojan", False) else 0
            for node in nodes
        ],
        dtype=torch.long,
    )

    # --------------------------------------------------------
    # Edge list
    # --------------------------------------------------------

    node_to_idx = {
        node: i
        for i, node in enumerate(nodes)
    }

    edges = []

    for source, target in graph.edges():

        edges.append(
            [
                node_to_idx[source],
                node_to_idx[target],
            ]
        )

    if edges:

        edge_index = torch.tensor(
            edges,
            dtype=torch.long,
        ).t().contiguous()

    else:

        edge_index = torch.empty(
            (2, 0),
            dtype=torch.long,
        )

    # --------------------------------------------------------
    # Feature tensor
    # --------------------------------------------------------

    x = torch.tensor(
        X,
        dtype=torch.float32,
    )

    return Data(
        x=x,
        edge_index=edge_index,
        y=y,
    )


# ============================================================
# Find netlists
# ============================================================

def find_netlists():
    """
    Find all .v files under data/TRIT-TS.

    Example:

        data/TRIT-TS/
        ├── s13207_T421/
        │   └── s13207_T421.v
        ├── s13207_T611/
        │   └── s13207_T611.v
        └── ...

    Returns a list of Verilog paths.
    """

    if not DATA_ROOT.exists():

        raise FileNotFoundError(
            f"Dataset directory not found: {DATA_ROOT.resolve()}"
        )

    files = sorted(
        DATA_ROOT.rglob("*.v")
    )

    if not files:

        raise FileNotFoundError(
            f"No Verilog files found under {DATA_ROOT.resolve()}"
        )

    return files


# ============================================================
# Determine circuit family
# ============================================================

def get_family(path: Path) -> str:
    """
    Determine circuit family from the filename.

    Examples:

        s13207_T421.v -> s13207
        s1423_T600.v  -> s1423
        s35932_T431.v -> s35932
    """

    name = path.stem

    # Everything before the first "_T".
    if "_T" in name:

        return name.split("_T", 1)[0]

    # Fallback: use the parent directory.
    return path.parent.name.split("_T", 1)[0]


# ============================================================
# Build dataset
# ============================================================

def build_node_level_dataset(
    families=None,
):
    """
    Parse all netlists and return a list of GraphSample objects.

    Important:
    We do NOT combine all nodes into one giant dataset.

    Each Verilog circuit remains a separate graph.

    This allows us to later perform family-level train/validation/test
    splits without leaking information between related nodes.
    """

    if families is None:

        families = FAMILIES

    families = set(families)

    paths = find_netlists()

    samples = []

    print()
    print("========== BUILDING DATASET ==========")

    for path in paths:

        family = get_family(path)

        if family not in families:
            continue

        try:

            parsed = parse_netlist(path)

            samples.append(
                GraphSample(
                    graph=parsed,
                    family=family,
                    source=str(path),
                )
            )

        except Exception as exc:

            print(
                f"[WARNING] Failed to parse {path}: {exc}"
            )

    if not samples:

        raise RuntimeError(
            "No matching netlists were parsed."
        )

    print("Netlists loaded :", len(samples))

    print()
    print("Graphs by family:")

    for family in sorted(families):

        count = sum(
            1
            for sample in samples
            if sample.family == family
        )

        print(
            f"  {family:10s}: {count}"
        )

    return samples


# ============================================================
# Simple test
# ============================================================

if __name__ == "__main__":

    samples = build_node_level_dataset()

    print()
    print("========== DATASET TEST ==========")

    for sample in samples[:5]:

        graph = sample.graph

        print()
        print("Family       :", sample.family)
        print("File         :", sample.source)
        print("Nodes        :", graph.number_of_nodes())
        print("Edges        :", graph.number_of_edges())

        trojan_count = sum(
            1
            for node in graph.nodes
            if graph.nodes[node].get("is_trojan", False)
        )

        print("Trojan nodes :", trojan_count)