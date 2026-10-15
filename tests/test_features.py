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


def test_canonical_gate_type_mapping():
    from features import canonical_gate_type, _type_index, TYPE_INDEX

    # Verify standard cells map to distinct functional categories
    assert canonical_gate_type("nor5s1") == "nor"
    assert canonical_gate_type("nnd4s1") == "nand"
    assert canonical_gate_type("dffs2") == "dff"
    assert canonical_gate_type("dffles2") == "dff"
    assert canonical_gate_type("xor2s1") == "xor"
    assert canonical_gate_type("xnr2s1") == "xnor"
    assert canonical_gate_type("aoi23s2") == "complex"
    assert canonical_gate_type("oai21s3") == "complex"
    assert canonical_gate_type("mxi21s3") == "mux"
    assert canonical_gate_type("i1s1") == "not"
    assert canonical_gate_type("hi1s1") == "buf"

    # Verify dff is NOT mapped to buf
    assert _type_index("dffs2") == TYPE_INDEX["dff"]
    assert _type_index("dffs2") != TYPE_INDEX["buf"]
    assert _type_index("nor5s1") == TYPE_INDEX["nor"]
    assert _type_index("nor5s1") != TYPE_INDEX["buf"]
