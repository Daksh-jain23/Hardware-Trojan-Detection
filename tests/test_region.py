"""
Unit tests for region expansion and localization.
"""

import sys
import unittest
from pathlib import Path

import networkx as nx

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from region import expand_region, select_top_k


class TestRegionExpansion(unittest.TestCase):

    def setUp(self):
        # Create a linear chain of nodes
        self.graph = nx.DiGraph()
        for i in range(20):
            self.graph.add_node(f"N{i}", gate_type="and")
        for i in range(19):
            self.graph.add_edge(f"N{i}", f"N{i+1}")

        self.scores = {f"N{i}": (0.99 if i == 5 else 0.1) for i in range(20)}

    def test_seed_selection(self):
        seeds = select_top_k(self.scores, k=1)
        self.assertEqual(seeds, ["N5"])

    def test_hop_expansion(self):
        # 1-hop around N5 should include predecessors (N4) and successors (N6)
        region = expand_region(self.graph, seed_nodes=["N5"], scores=self.scores, hops=1, max_size=50)
        self.assertIn("N5", region)
        self.assertIn("N4", region)
        self.assertIn("N6", region)
        self.assertNotIn("N2", region)

    def test_max_size_cap(self):
        region = expand_region(self.graph, seed_nodes=["N5"], scores=self.scores, hops=5, max_size=4)
        self.assertLessEqual(len(region), 4, "Region must respect max_size cap.")


if __name__ == "__main__":
    unittest.main()
