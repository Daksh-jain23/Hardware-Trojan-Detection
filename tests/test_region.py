import unittest
import sys
from pathlib import Path
import networkx as nx

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from src.region import (
    SuspiciousRegion,
    RefinedRegion,
    extract_region,
    refine_suspicious_region,
    region_description,
)


class TestRegionRefinement(unittest.TestCase):

    def setUp(self):
        # Create a synthetic circuit graph with:
        # - Core Trojan trigger nodes: T1, T2, T3 (sequential DFF)
        # - Payload gate: P1
        # - Normal logic: N1, N2, N3
        # - Peripheral leaf nodes: L1, L2 (low score, degree 1)
        self.graph = nx.DiGraph()

        # Nodes
        self.graph.add_node("T1", gate_type="and2s1", is_trojan=True)
        self.graph.add_node("T2", gate_type="nor2s1", is_trojan=True)
        self.graph.add_node("T3", gate_type="dffs2", is_trojan=True) # Sequential trigger
        self.graph.add_node("P1", gate_type="xor2s1", is_trojan=True) # Payload
        self.graph.add_node("N1", gate_type="and2s1", is_trojan=False)
        self.graph.add_node("L1", gate_type="buf", is_trojan=False)
        self.graph.add_node("L2", gate_type="not", is_trojan=False)
        self.graph.add_node("EXT_OUT", gate_type="PO", is_trojan=False)

        # Edges
        self.graph.add_edge("T1", "T2")
        self.graph.add_edge("T2", "T3")
        self.graph.add_edge("T3", "P1")
        self.graph.add_edge("P1", "EXT_OUT") # Exit
        self.graph.add_edge("N1", "T1")
        self.graph.add_edge("N1", "L1") # L1 is leaf connected only to N1
        self.graph.add_edge("T2", "L2") # L2 is leaf connected only to T2

        # Scores
        self.scores = {
            "T1": 0.99,
            "T2": 0.98,
            "T3": 0.95,
            "P1": 0.96,
            "N1": 0.40,
            "L1": 0.05,
            "L2": 0.02,
            "EXT_OUT": 0.01,
        }

        self.candidate_nodes = {"T1", "T2", "T3", "P1", "N1", "L1", "L2"}
        self.seed_nodes = ["T1", "T2", "P1"]
        self.region = SuspiciousRegion(
            nodes=self.candidate_nodes,
            seed_nodes=self.seed_nodes,
            scores=self.scores,
            source="synthetic_test",
        )

    def test_refinement_prunes_peripheral_leaves(self):
        refined = refine_suspicious_region(
            graph=self.graph,
            region=self.region,
            scores=self.scores,
            gnn_threshold=0.95,
            prune_threshold=0.30,
        )

        self.assertIsInstance(refined, RefinedRegion)

        # L1 and L2 should be pruned (leaf nodes with score < 0.30)
        self.assertIn("L1", refined.pruned_nodes)
        self.assertIn("L2", refined.pruned_nodes)
        self.assertNotIn("L1", refined.nodes)
        self.assertNotIn("L2", refined.nodes)

        # Core Trojan anchors must be 100% retained
        self.assertIn("T1", refined.nodes)
        self.assertIn("T2", refined.nodes)
        self.assertIn("T3", refined.nodes)
        self.assertIn("P1", refined.nodes)

        # Compression ratio must be positive
        self.assertGreater(refined.retention_ratio, 0.0)
        self.assertLess(refined.retention_ratio, 1.0)
        self.assertEqual(len(refined.nodes) + len(refined.pruned_nodes), len(self.candidate_nodes))

    def test_region_description_formatting(self):
        refined = refine_suspicious_region(
            graph=self.graph,
            region=self.region,
            scores=self.scores,
        )
        desc = region_description(self.graph, refined)
        self.assertIn("Region size:", desc)
        self.assertIn("Pruned peripheral gates:", desc)
        self.assertIn("Suspicious gates:", desc)


if __name__ == "__main__":
    unittest.main()
