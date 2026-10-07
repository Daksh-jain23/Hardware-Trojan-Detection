import sys
from pathlib import Path

import networkx as nx


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from evidence import expand_region, select_ranked_context_nodes, select_suspicious_seeds


def test_positive_seeds_are_separate_from_ranked_context():
    scores = {"a": 0.96, "b": 0.94, "c": 0.10}

    assert select_suspicious_seeds(scores, threshold=0.95) == ["a"]
    assert select_ranked_context_nodes(scores, top_k=2) == ["a", "b"]


def test_capped_region_selection_is_deterministic():
    graph = nx.DiGraph()
    graph.add_edges_from(("seed", node) for node in ("z", "a", "m"))

    assert expand_region(graph, ["seed"], hops=1, max_size=2) == {"seed", "a"}
