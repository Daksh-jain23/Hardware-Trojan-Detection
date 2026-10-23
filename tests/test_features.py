import sys
import unittest
from pathlib import Path

import networkx as nx

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from features import (
    FEATURE_DIM,
    TYPE_INDEX,
    _type_index,
    canonical_gate_type,
    compute_node_features,
)


class TestFeatures(unittest.TestCase):

    def test_features_have_expected_dimension_and_finite_values(self):
        graph = nx.DiGraph()
        graph.add_node("pi", gate_type="PI", node_kind="pi")
        graph.add_node("g", gate_type="and", node_kind="gate")
        graph.add_node("po", gate_type="PO", node_kind="po")
        graph.add_edges_from((("pi", "g"), ("g", "po")))

        features, nodes = compute_node_features(graph)

        self.assertEqual(nodes, ["pi", "g", "po"])
        self.assertEqual(features.shape, (3, FEATURE_DIM))
        self.assertEqual(features.dtype.name, "float32")

    def test_canonical_gate_type_mapping(self):
        # Verify standard cells map to distinct functional categories
        self.assertEqual(canonical_gate_type("nor5s1"), "nor")
        self.assertEqual(canonical_gate_type("nnd4s1"), "nand")
        self.assertEqual(canonical_gate_type("dffs2"), "dff")
        self.assertEqual(canonical_gate_type("dffles2"), "dff")
        self.assertEqual(canonical_gate_type("xor2s1"), "xor")
        self.assertEqual(canonical_gate_type("xnr2s1"), "xnor")
        self.assertEqual(canonical_gate_type("aoi23s2"), "complex")
        self.assertEqual(canonical_gate_type("oai21s3"), "complex")
        self.assertEqual(canonical_gate_type("mxi21s3"), "mux")
        self.assertEqual(canonical_gate_type("i1s1"), "not")
        self.assertEqual(canonical_gate_type("hi1s1"), "buf")

        # Verify dff is NOT mapped to buf
        self.assertEqual(_type_index("dffs2"), TYPE_INDEX["dff"])
        self.assertNotEqual(_type_index("dffs2"), TYPE_INDEX["buf"])
        self.assertEqual(_type_index("nor5s1"), TYPE_INDEX["nor"])
        self.assertNotEqual(_type_index("nor5s1"), TYPE_INDEX["buf"])


if __name__ == "__main__":
    unittest.main()
