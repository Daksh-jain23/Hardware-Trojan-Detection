"""
Unit tests for node feature extraction.
"""

import sys
import unittest
from pathlib import Path

import networkx as nx
import numpy as np

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from features import compute_node_features, FEATURE_DIM


class TestFeatureExtraction(unittest.TestCase):

    def setUp(self):
        # Create a small synthetic directed circuit graph
        self.graph = nx.DiGraph()
        self.graph.add_node("PI1", gate_type="PI")
        self.graph.add_node("PI2", gate_type="PI")
        self.graph.add_node("G1", gate_type="and")
        self.graph.add_node("G2", gate_type="or")
        self.graph.add_node("G3", gate_type="xor")
        self.graph.add_node("PO1", gate_type="PO")

        self.graph.add_edge("PI1", "G1")
        self.graph.add_edge("PI2", "G1")
        self.graph.add_edge("G1", "G2")
        self.graph.add_edge("G2", "G3")
        self.graph.add_edge("G3", "PO1")

    def test_feature_dimension_assertion(self):
        self.assertEqual(FEATURE_DIM, 41)

        features, nodes = compute_node_features(self.graph)

        self.assertEqual(len(nodes), self.graph.number_of_nodes())
        self.assertIsInstance(features, np.ndarray)
        self.assertEqual(features.shape[0], self.graph.number_of_nodes())
        self.assertEqual(features.shape[1], 41, "Feature dimension must be exactly 41.")

    def test_features_validity(self):
        features, _ = compute_node_features(self.graph)

        # Ensure no NaNs or Infs
        self.assertFalse(np.isnan(features).any(), "Features must not contain NaN.")
        self.assertFalse(np.isinf(features).any(), "Features must not contain Inf.")


if __name__ == "__main__":
    unittest.main()
