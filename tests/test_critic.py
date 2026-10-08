"""
Unit tests for the Actor-Critic verification loop and deterministic fact checker.
"""

import unittest
from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from critic import (
    audit_actor_factual_claims,
    build_critic_audit_prompt,
    build_actor_refinement_prompt,
    run_actor_critic_loop,
)


class TestActorCritic(unittest.TestCase):

    def setUp(self):
        self.evidence_a = {
            "region_size": 36,
            "gnn_seeds_count": 15,
            "max_gnn_score": 0.99,
            "avg_gnn_score": 0.72,
            "internal_edges": 50,
            "internal_edge_density": 1.38,
            "region_exits_count": 5,
            "exit_ratio": 0.14,
            "sequential_gate_count": 5,
            "gate_types": {"dffs2": 5, "xor2s3": 10},
        }
        self.evidence_b = {
            "region_size": 36,
            "gnn_seeds_count": 0,
            "max_gnn_score": 0.10,
            "avg_gnn_score": 0.02,
            "internal_edges": 25,
            "internal_edge_density": 0.69,
            "region_exits_count": 20,
            "exit_ratio": 0.55,
            "sequential_gate_count": 0,
            "gate_types": {"nor2s3": 20},
        }

    def test_fact_check_detects_hallucination(self):
        # Actor claims Region A has 12 DFFs when evidence has 5
        actor_text = "Region A contains 12 sequential flip-flops and an internal density of 1.38."
        warnings = audit_actor_factual_claims(actor_text, self.evidence_a, self.evidence_b)
        self.assertTrue(len(warnings) > 0)
        self.assertIn("Claimed 12 sequential flip-flops", warnings[0])

    def test_fact_check_passes_on_accurate_claims(self):
        actor_text = "Region A contains 5 sequential flip-flops and an internal density of 1.38 with an exit ratio of 0.14."
        warnings = audit_actor_factual_claims(actor_text, self.evidence_a, self.evidence_b)
        self.assertEqual(len(warnings), 0)

    def test_build_critic_audit_prompt(self):
        actor_text = "ASSESSMENT: REGION_A\nCONFIDENCE: HIGH\nJUSTIFICATION: Region A has high density."
        prompt = build_critic_audit_prompt(
            self.evidence_a, self.evidence_b, actor_text, ["Test warning"]
        )
        self.assertIn("Senior ASIC Verification Engineer", prompt)
        self.assertIn("Test warning", prompt)
        self.assertIn("REGION A", prompt)
        self.assertIn("REGION B", prompt)

    def test_build_actor_refinement_prompt(self):
        orig = "Original A/B prompt"
        init = "ASSESSMENT: REGION_A"
        crit = "CRITIQUE: Region B could be benign"
        refine = build_actor_refinement_prompt(orig, init, crit)
        self.assertIn("YOUR INITIAL HYPOTHESIS", refine)
        self.assertIn("SENIOR HARDWARE AUDITOR CRITIQUE", refine)

    def test_run_actor_critic_loop_offline_resilience(self):
        # Test simulated caller
        def dummy_caller(p):
            if "SENIOR HARDWARE AUDITOR" in p:
                return "VERDICT: ACCEPT\nCRITIQUE: Factual grounding verified.\nRECOMMENDED_ASSESSMENT: REGION_A"
            elif "Auditor" in p or "Senior" in p:
                return "VERDICT: ACCEPT"
            return "ASSESSMENT: REGION_A\nCONFIDENCE: HIGH\nJUSTIFICATION: Region A is dense."

        result = run_actor_critic_loop(
            prompt="Choose A or B",
            evidence_a=self.evidence_a,
            evidence_b=self.evidence_b,
            llm_caller=dummy_caller,
        )
        self.assertIn("final_response", result)
        self.assertEqual(result["turns_completed"], 3)

    def test_critic_prompts_have_no_leakage(self):
        from anonymizer import assert_no_leakage
        actor_text = "ASSESSMENT: REGION_A\nCONFIDENCE: HIGH\nJUSTIFICATION: Region A has high density."
        critic_prompt = build_critic_audit_prompt(
            self.evidence_a, self.evidence_b, actor_text, ["Sample warning"]
        )
        self.assertTrue(assert_no_leakage(critic_prompt))
        refine_prompt = build_actor_refinement_prompt("Choose A or B", actor_text, "CRITIQUE: Good")
        self.assertTrue(assert_no_leakage(refine_prompt))


if __name__ == "__main__":
    unittest.main()

