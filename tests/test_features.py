import sys
from pathlib import Path

import networkx as nx


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from features import FEATURE_DIM, compute_node_features


def test_features_have_expected_dimension_and_finite_values():
    graph = nx.DiGraph()
    graph.add_node("pi", gate_type="PI", node_kind="pi")
    graph.add_node("g", gate_type="and", node_kind="gate")
    graph.add_node("po", gate_type="PO", node_kind="po")
    graph.add_edges_from((("pi", "g"), ("g", "po")))

    features, nodes = compute_node_features(graph)

    assert nodes == ["pi", "g", "po"]
    assert features.shape == (3, FEATURE_DIM)
    assert features.dtype.name == "float32"
