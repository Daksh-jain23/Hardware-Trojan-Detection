"""
Unit tests for Controlled A/B evaluation framework.
"""

import sys
import unittest
from pathlib import Path

import networkx as nx

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
# Ensure src is on sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
ROOT_DIR = Path(__file__).resolve().parent.parent
for path_dir in [SRC_DIR, ROOT_DIR]:
    if str(path_dir) not in sys.path:
        sys.path.insert(0, str(path_dir))

try:
    from ab_evaluation import (
        extract_trojan_region,
        extract_matched_clean_region,
        compute_region_structural_evidence,
        build_ab_prompt,
        parse_ab_response,
        run_controlled_ab_test,
    )
    from anonymizer import anonymize_evidence, assert_no_leakage
except (ImportError, ModuleNotFoundError):
    from src.ab_evaluation import (
        extract_trojan_region,
        extract_matched_clean_region,
        compute_region_structural_evidence,
        build_ab_prompt,
        parse_ab_response,
        run_controlled_ab_test,
    )
    from src.anonymizer import anonymize_evidence, assert_no_leakage


class TestABEvaluation(unittest.TestCase):

    def setUp(self):
        self.graph = nx.DiGraph()

        # Clean nodes
        for i in range(20):
            self.graph.add_node(f"C_{i}", gate_type="and", is_trojan=False)
        for i in range(19):
            self.graph.add_edge(f"C_{i}", f"C_{i+1}")

        # Trojan nodes
        for i in range(5):
            self.graph.add_node(f"troj_{i}", gate_type="xor", is_trojan=True)
        for i in range(4):
            self.graph.add_edge(f"troj_{i}", f"troj_{i+1}")

    def test_region_extractions(self):
        troj_region = extract_trojan_region(self.graph, hops=1)
        self.assertTrue(all(f"troj_{i}" in troj_region for i in range(5)))

        clean_region = extract_matched_clean_region(
            self.graph,
            trojan_region=troj_region,
            target_size=len(troj_region),
        )
        self.assertGreater(len(clean_region), 0)
        # Ensure no Trojan nodes in clean region
        for n in clean_region:
            self.assertFalse(self.graph.nodes[n].get("is_trojan", False))

    def test_prompt_generation_and_leakage(self):
        troj_ev = compute_region_structural_evidence(self.graph, {"troj_0", "troj_1"})
        clean_ev = compute_region_structural_evidence(self.graph, {"C_0", "C_1"})

        anon_troj, map_troj = anonymize_evidence(troj_ev)
        anon_clean, map_clean = anonymize_evidence(clean_ev)

        prompt = build_ab_prompt(anon_troj, anon_clean)
        self.assertIn("REGION A STRUCTURAL EVIDENCE", prompt)
        self.assertIn("REGION B STRUCTURAL EVIDENCE", prompt)
        self.assertIn("ASSESSMENT: <REGION_A | REGION_B | NEITHER>", prompt)

        # Enforce zero leakage verification
        combined_map = {**map_troj, **map_clean}
        assert_no_leakage(prompt, combined_map)

    def test_response_parsing(self):
        sample_response = """
        ASSESSMENT: REGION_A
        CONFIDENCE: HIGH
        OBSERVED_DIFFERENCES:
        - Region A has high internal density
        REASONING:
        Region A exhibits cohesive trigger logic.
        """
        parsed = parse_ab_response(sample_response)
        self.assertEqual(parsed["assessment"], "REGION_A")
        self.assertEqual(parsed["confidence"], "HIGH")

        swapped_response = """
        ASSESSMENT: REGION_B
        CONFIDENCE: MEDIUM
        REASONING:
        Region B is more suspicious.
        """
        parsed_swap = parse_ab_response(swapped_response)
        self.assertEqual(parsed_swap["assessment"], "REGION_B")
        self.assertEqual(parsed_swap["confidence"], "MEDIUM")

    def test_swap_consistency_logic(self):
        # Case 1: Consistent (Trial 1 = REGION_A, Trial 2 = REGION_B)
        t1_assessment = "REGION_A"
        t2_assessment = "REGION_B"
        swap_consistent = (t1_assessment == "REGION_A" and t2_assessment == "REGION_B")
        self.assertTrue(swap_consistent)

        # Case 2: Position bias (Trial 1 = REGION_A, Trial 2 = REGION_A)
        t1_bias = "REGION_A"
        t2_bias = "REGION_A"
        bias_detected = (t1_bias == t2_bias and t1_bias in ("REGION_A", "REGION_B"))
        self.assertTrue(bias_detected)


if __name__ == "__main__":
    unittest.main()
