"""
Unit tests for independent heuristic baseline detector.
"""

import sys
import unittest
from pathlib import Path

import networkx as nx

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from heuristic import detect_trojan_heuristic


class TestHeuristicDetector(unittest.TestCase):

    def setUp(self):
        # Create a clean normal circuit graph
        self.clean_graph = nx.DiGraph()
        for i in range(10):
            self.clean_graph.add_node(f"PI_{i}", gate_type="PI")
            self.clean_graph.add_node(f"G_{i}", gate_type="and")
            self.clean_graph.add_node(f"PO_{i}", gate_type="PO")
            self.clean_graph.add_edge(f"PI_{i}", f"G_{i}")
            self.clean_graph.add_edge(f"G_{i}", f"PO_{i}")

        # Create a graph with a wide comparator trigger tree and counter cluster
        self.trojan_graph = self.clean_graph.copy()
        # High fan-in comparator tree
        self.trojan_graph.add_node("TRG1", gate_type="and")
        for i in range(6):
            self.trojan_graph.add_edge(f"PI_{i}", "TRG1")

        # 3 flip-flops in a tight feedback loop
        for f in range(3):
            self.trojan_graph.add_node(f"FF_{f}", gate_type="dff")
        self.trojan_graph.add_edge("FF_0", "FF_1")
        self.trojan_graph.add_edge("FF_1", "FF_2")
        self.trojan_graph.add_edge("FF_2", "FF_0")
        self.trojan_graph.add_edge("TRG1", "FF_0")

    def test_heuristic_output_schema(self):
        res = detect_trojan_heuristic(self.clean_graph, circuit_name="clean_test")
        self.assertIn("decision", res)
        self.assertIn("score", res)
        self.assertIn("threshold", res)
        self.assertIn("anomalous_node_count", res)
        self.assertIn("verdict_explanation", res)
        self.assertIn(res["decision"], {"SUSPICIOUS", "NORMAL", "UNCERTAIN"})

    def test_heuristic_detects_anomaly(self):
        clean_res = detect_trojan_heuristic(self.clean_graph, circuit_name="clean_test")
        trojan_res = detect_trojan_heuristic(self.trojan_graph, circuit_name="trojan_test")

        # The trojan-like graph should score noticeably higher than the clean graph
        self.assertGreater(
            trojan_res["score"],
            clean_res["score"],
            "Trojan-like topology should yield higher heuristic anomaly score.",
        )

    def test_heuristic_determinism(self):
        res1 = detect_trojan_heuristic(self.trojan_graph, threshold=0.65)
        res2 = detect_trojan_heuristic(self.trojan_graph, threshold=0.65)
        self.assertEqual(res1["score"], res2["score"])
        self.assertEqual(res1["decision"], res2["decision"])

    def test_evaluate_gnn_candidate_region(self):
        from heuristic import evaluate_gnn_candidate_region
        # 1. Trojan cluster: tightly connected trigger and DFF loop
        trojan_seeds = {"TRG1", "FF_0", "FF_1"}
        trojan_region = {"TRG1", "FF_0", "FF_1", "FF_2"}
        verif_trojan = evaluate_gnn_candidate_region(
            self.trojan_graph,
            suspicious_seeds=trojan_seeds,
            region_nodes=trojan_region,
        )
        self.assertEqual(verif_trojan["verdict"], "SUSPICIOUS_CONFIRMED")
        self.assertGreaterEqual(verif_trojan["score"], 0.40)
        self.assertGreaterEqual(len(verif_trojan["confirmed_seeds"]), 1)

        # 2. Empty seeds should cleanly return FILTERED_OUT_CLEAN
        verif_empty = evaluate_gnn_candidate_region(
            self.clean_graph,
            suspicious_seeds=set(),
            region_nodes=set(),
        )
        self.assertEqual(verif_empty["verdict"], "FILTERED_OUT_CLEAN")
        self.assertEqual(verif_empty["score"], 0.0)


if __name__ == "__main__":
    unittest.main()
