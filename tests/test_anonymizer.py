"""
Unit tests for evidence anonymizer and zero-leakage assertions.
"""

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from anonymizer import anonymize_evidence, assert_no_leakage


class TestAnonymizer(unittest.TestCase):

    def setUp(self):
        self.evidence = {
            "circuit": "s13207_T421",
            "suspicious_seeds": [
                {"gate": "troj21_0counter_reg_0_", "gnn_score": 0.998},
                {"gate": "troj21_0Trojan_out0_reg", "gnn_score": 0.985},
            ],
            "structural_evidence": {
                "sequential_like_gates": ["troj21_0counter_reg_0_"],
                "region_exits": ["troj21_0Trojan_out0_reg"],
            },
            "local_structural_patterns": {
                "representative_nodes": [
                    {
                        "gate": "troj21_0counter_reg_0_",
                        "region_predecessors": ["U105", "troj21_0Trojan_out0_reg"],
                        "region_successors": ["U204"],
                    }
                ],
                "high_score_to_sequential": [
                    {
                        "source": "U105",
                        "target": "troj21_0counter_reg_0_",
                    }
                ],
            },
        }

    def test_anonymization_replaces_all_identifiers(self):
        anon_evidence, mapping = anonymize_evidence(self.evidence)

        # Mapping should map original names to NODE_XXXX
        self.assertIn("troj21_0counter_reg_0_", mapping)
        self.assertTrue(mapping["troj21_0counter_reg_0_"].startswith("NODE_"))

        # Check in seeds
        seed_gates = [s["gate"] for s in anon_evidence["suspicious_seeds"]]
        for g in seed_gates:
            self.assertTrue(g.startswith("NODE_"), f"Gate {g} was not anonymized")

        # Check in region exits
        for exit_node in anon_evidence["structural_evidence"]["region_exits"]:
            self.assertTrue(exit_node.startswith("NODE_"))

        # Check in local patterns
        rep_nodes = anon_evidence["local_structural_patterns"]["representative_nodes"]
        self.assertTrue(rep_nodes[0]["gate"].startswith("NODE_"))
        for p in rep_nodes[0]["region_predecessors"]:
            self.assertTrue(p.startswith("NODE_"))

    def test_assert_no_leakage_success(self):
        anon_evidence, mapping = anonymize_evidence(self.evidence)
        # Should succeed without raising
        self.assertTrue(assert_no_leakage(anon_evidence, mapping))

    def test_assert_no_leakage_catches_leaks(self):
        # Un-anonymized data should be rejected
        with self.assertRaises(ValueError):
            assert_no_leakage("This contains troj21_0counter_reg_0_")

        with self.assertRaises(ValueError):
            assert_no_leakage("This contains trojan_out")


if __name__ == "__main__":
    unittest.main()
