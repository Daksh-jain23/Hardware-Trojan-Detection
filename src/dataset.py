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

# ============================================================
# Configuration
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

# Search paths for datasets. If present, both TRIT-TS and TRIT-TC are supported.
DEFAULT_DATA_ROOTS = [
    ROOT_DIR / "data" / "TRIT-TS",
    ROOT_DIR / "data" / "TRIT-TC",
]

# Known families across TRIT-TS and TRIT-TC benchmark suites
ALL_KNOWN_FAMILIES = [
    "c2670",
    "c3540",
    "c5315",
    "c6288",
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
        Circuit family, e.g. s13207 or c2670.

    source:
        Original Verilog file path.
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

def find_netlists(
    data_roots: Path | str | list[Path | str] | None = None,
    files: list[Path | str] | None = None,
) -> list[Path]:
    """
    Find Verilog files from specified files, directories, or default dataset roots.

    Supports:
        - Specific files: files=['path/to/c2670_T001.v', ...]
        - Whole dataset directories: data_roots='data/TRIT-TC' or ['data/TRIT-TS', 'data/TRIT-TC']
    """
    if files:
        resolved = [Path(f).resolve() for f in files]
        existing = [f for f in resolved if f.exists()]
        if not existing:
            raise FileNotFoundError(f"None of the specified files exist: {files}")
        return sorted(existing)

    if data_roots is None:
        data_roots = [p for p in DEFAULT_DATA_ROOTS if p.exists()]
        if not data_roots:
            data_roots = [ROOT_DIR / "data"]
    elif isinstance(data_roots, (str, Path)):
        data_roots = [Path(data_roots)]

    discovered: list[Path] = []
    for root in data_roots:
        p = Path(root)
        if not p.is_absolute():
            p = ROOT_DIR / p
        if p.is_file() and p.suffix == ".v":
            discovered.append(p.resolve())
        elif p.is_dir():
            discovered.extend(p.rglob("*.v"))

    discovered = sorted(set(discovered))
    if not discovered:
        raise FileNotFoundError(
            f"No Verilog (.v) files found in data roots: {[str(r) for r in data_roots]}"
        )

    return discovered


# ============================================================
# Determine circuit family
# ============================================================

def get_family(path: Path) -> str:
    """
    Determine circuit family from the filename or parent directory.

    Examples:
        c2670_T001.v  -> c2670
        s13207_T421.v -> s13207
        s1423_T600.v  -> s1423
        s35932_T431.v -> s35932
    """
    path = Path(path)
    name = path.stem

    if "_T" in name:
        return name.split("_T", 1)[0]

    parent_name = path.parent.name
    if "_T" in parent_name:
        return parent_name.split("_T", 1)[0]

    return name.split("_")[0]


# ============================================================
# Build dataset
# ============================================================

def build_node_level_dataset(
    families: list[str] | set[str] | None = None,
    data_roots: Path | str | list[Path | str] | None = None,
    files: list[Path | str] | None = None,
    max_samples: int | None = None,
) -> list[GraphSample]:
    """
    Parse netlists and return a list of GraphSample objects.

    Parameters:
        families: Optional filter for circuit families (e.g. ['s13207', 'c2670']).
                  If None, includes all discovered families.
        data_roots: Directory or list of directories to scan (TRIT-TS, TRIT-TC, etc.).
        files: Optional explicit list of .v files.
        max_samples: Optional limit on the number of netlists loaded.
    """
    paths = find_netlists(data_roots=data_roots, files=files)

    if families is not None:
        families_set = set(families)
    else:
        families_set = None

    samples: list[GraphSample] = []

    print()
    print("========== BUILDING DATASET ==========")
    print(f"Total candidate files found: {len(paths)}")

    for path in paths:
        if max_samples and len(samples) >= max_samples:
            break

        family = get_family(path)
        if families_set is not None and family not in families_set:
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
            print(f"[WARNING] Failed to parse {path}: {exc}")

    if not samples:
        raise RuntimeError("No matching netlists were parsed.")

    print("Netlists loaded :", len(samples))
    print()
    print("Graphs by family:")

    discovered_families = sorted(set(s.family for s in samples))
    for fam in discovered_families:
        count = sum(1 for sample in samples if sample.family == fam)
        print(f"  {fam:10s}: {count}")

    return samples


# ============================================================
# Dataset Splitting (by Family or by File Split)
# ============================================================

def split_dataset(
    samples: list[GraphSample],
    split_by: str = "family",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    train_families: list[str] | None = None,
    val_families: list[str] | None = None,
    test_families: list[str] | None = None,
    seed: int = 42,
) -> tuple[list[GraphSample], list[GraphSample], list[GraphSample]]:
    """
    Split GraphSample dataset into Train, Validation, and Test sets.

    Supports:
        1. Explicit family split (zero leakage across related circuits).
        2. Automatic family split (proportional partition of circuit families).
        3. Random file-level split across all circuits.
    """
    import random
    rng = random.Random(seed)

    # Mode 1: Explicit families
    if train_families or val_families or test_families:
        tr_fam = set(train_families or [])
        va_fam = set(val_families or [])
        te_fam = set(test_families or [])

        train_set = [s for s in samples if s.family in tr_fam]
        val_set = [s for s in samples if s.family in va_fam]
        test_set = [s for s in samples if s.family in te_fam]
        return train_set, val_set, test_set

    # Mode 2: Split by circuit families automatically
    if split_by == "family":
        families = sorted(set(s.family for s in samples))
        rng.shuffle(families)

        n_fam = len(families)
        n_train = max(1, int(round(n_fam * train_ratio)))
        n_val = max(1, int(round(n_fam * val_ratio))) if n_fam >= 3 else 0

        tr_fam = set(families[:n_train])
        va_fam = set(families[n_train:n_train + n_val])
        te_fam = set(families[n_train + n_val:])
        if not te_fam and len(families) >= 2:
            te_fam = {families[-1]}
            tr_fam.discard(families[-1])
            va_fam.discard(families[-1])

        train_set = [s for s in samples if s.family in tr_fam]
        val_set = [s for s in samples if s.family in va_fam]
        test_set = [s for s in samples if s.family in te_fam]
        return train_set, val_set, test_set

    # Mode 3: Split by individual files / samples
    shuffled = list(samples)
    rng.shuffle(shuffled)
    n = len(shuffled)
    n_train = max(1, int(round(n * train_ratio)))
    n_val = max(0, int(round(n * val_ratio)))

    train_set = shuffled[:n_train]
    val_set = shuffled[n_train:n_train + n_val]
    test_set = shuffled[n_train + n_val:]
    return train_set, val_set, test_set


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