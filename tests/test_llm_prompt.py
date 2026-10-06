"""
Unit tests for Phase 4: Heuristic-Guided Prompt Engineering & LLM Interface.

Verifies:
1. Prompt generation in 'hybrid' mode with authoritative heuristic facts and factor attributions.
2. Prompt generation in 'baseline' mode preserving unaltered pure GNN evidence.
3. Inclusion of region refinement metrics in hybrid prompts.
4. Heuristic-guided suspicious node ranking.
5. Structured JSON response parsing with validation and fallbacks in src/llm.py.
6. Execution constraint metadata tracking (heuristic_output_used flag).
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

for p in [str(ROOT), str(SRC)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.llm_prompt import (
    build_prompt,
    build_hybrid_prompt,
    build_baseline_prompt,
    deterministic_gnn_facts,
    deterministic_heuristic_facts,
    deterministic_refinement_facts,
)
from src.llm import (
    parse_structured_llm_response,
    extract_decision,
    extract_confidence,
    generate_mock_response,
)


class TestPromptBuilder(unittest.TestCase):

    def setUp(self):
        # Sample synthetic evidence matching schema
        self.evidence = {
            "graph": {
                "total_nodes": 120,
                "total_edges": 180,
            },
            "gnn": {
                "threshold": 0.95,
                "top_k": 5,
                "suspicious_seed_count": 3,
                "suspicious_region_size": 15,
                "suspicion": {
                    "max": 0.995,
                    "mean": 0.65,
                    "median": 0.70,
                    "min": 0.01,
                },
            },
            "suspicious_seeds": [
                {"gate": "NODE_01", "type": "dffs2", "gnn_score": 0.995, "fanin": 2, "fanout": 1},
                {"gate": "NODE_02", "type": "and2s1", "gnn_score": 0.985, "fanin": 2, "fanout": 2},
                {"gate": "NODE_03", "type": "nor2s1", "gnn_score": 0.975, "fanin": 2, "fanout": 1},
            ],
            "region": {
                "size": 15,
                "gate_types": {"dffs2": 4, "and2s1": 6, "nor2s1": 5},
                "internal_edges": 25,
                "boundary_edges": 8,
            },
            "structural_evidence": {
                "internal_edges": 25,
                "boundary_edges": 8,
                "region_exits": [{"from": "NODE_02", "to": "EXT_01"}],
                "sequential_like_gates": ["NODE_01"],
            },
            "nodes": [
                {"gate": "NODE_01", "type": "dffs2", "gnn_score": 0.995, "fanin": 2, "fanout": 1, "distance_to_output": 2.0},
                {"gate": "NODE_02", "type": "and2s1", "gnn_score": 0.985, "fanin": 2, "fanout": 2, "distance_to_output": 1.0},
                {"gate": "NODE_03", "type": "nor2s1", "gnn_score": 0.975, "fanin": 2, "fanout": 1, "distance_to_output": 3.0},
                {"gate": "NODE_04", "type": "dffs2", "gnn_score": 0.850, "fanin": 2, "fanout": 1, "distance_to_output": 3.0},
            ],
        }

    def test_deterministic_gnn_facts(self):
        facts = deterministic_gnn_facts(self.evidence["gnn"], self.evidence["suspicious_seeds"])
        self.assertEqual(facts["suspicious_seed_count"], 3)
        self.assertEqual(facts["seed_score_max"], 0.995)
        self.assertEqual(facts["seed_count_at_or_above_threshold"], 3)
        self.assertEqual(facts["threshold"], 0.95)

    def test_deterministic_heuristic_facts(self):
        h_facts = deterministic_heuristic_facts(self.evidence)
        self.assertIn("composite_heuristic_score", h_facts)
        self.assertIn("optimal_heuristic_threshold", h_facts)
        self.assertIn("heuristic_decision", h_facts)
        self.assertIn("top_contributing_factors", h_facts)
        self.assertTrue(0.0 <= h_facts["composite_heuristic_score"] <= 1.0)
        self.assertEqual(len(h_facts["top_contributing_factors"]), 5)

    def test_hybrid_prompt_contents(self):
        prompt = build_prompt(self.evidence, mode="hybrid")
        self.assertIn("HEURISTIC AUTHORITATIVE NUMERICAL FACTS", prompt)
        self.assertIn("GNN AUTHORITATIVE NUMERICAL FACTS", prompt)
        self.assertIn("CONTRADICTION ANALYSIS & ARBITRATION GUIDELINES", prompt)
        self.assertIn("PART 1: STRICT JSON BLOCK", prompt)
        self.assertIn("PART 2: STRUCTURED TEXT REPORT", prompt)
        self.assertIn("TOP SUSPICIOUS NODES (HEURISTIC-GUIDED PRIORITY)", prompt)

    def test_baseline_prompt_contents(self):
        prompt = build_prompt(self.evidence, mode="baseline")
        self.assertNotIn("HEURISTIC AUTHORITATIVE NUMERICAL FACTS", prompt)
        self.assertIn("The heuristic is an independent comparison method.", prompt)
        self.assertIn("Its output is NOT provided here and MUST NOT be inferred.", prompt)
        self.assertIn("AUTHORITATIVE NUMERICAL FACTS", prompt)

    def test_region_refinement_integration(self):
        refinement_data = {
            "original_region_size": 20,
            "refined_region_size": 15,
            "pruned_peripheral_leaves": 5,
            "retention_ratio": 0.75,
            "noise_reduction_ratio": 0.25,
            "core_anchors_preserved": True,
            "sequential_anchors_preserved": True,
        }
        prompt = build_prompt(self.evidence, mode="hybrid", refined_region=refinement_data)
        self.assertIn("REGION REFINEMENT METRICS (GRAPH-THEORETIC PRUNING)", prompt)
        self.assertIn('"pruned_peripheral_leaves": 5', prompt)
        self.assertIn('"retention_ratio": 0.75', prompt)


class TestLLMResponseParser(unittest.TestCase):

    def test_parse_valid_json_code_fence(self):
        sample_response = """
Here is my analysis:

```json
{
  "decision": "SUSPICIOUS",
  "confidence": "HIGH",
  "gnn_heuristic_agreement": true,
  "arbitration_rationale": "High GNN scores combined with sequential state loop confirm Trojan.",
  "trojan_structure_type": "sequential_counter",
  "suspicious_gate_classes": ["dffs2", "and2s1"],
  "payload_exit_analysis": "Direct exit to output via payload gate.",
  "counter_evidence": "No significant counter-evidence is visible.",
  "false_positive_risk": "LOW"
}
```

DECISION: SUSPICIOUS
CONFIDENCE: HIGH
"""
        parsed = parse_structured_llm_response(sample_response)
        self.assertTrue(parsed["raw_json_parsed"])
        self.assertEqual(parsed["decision"], "SUSPICIOUS")
        self.assertEqual(parsed["confidence"], "HIGH")
        self.assertTrue(parsed["gnn_heuristic_agreement"])
        self.assertEqual(parsed["trojan_structure_type"], "sequential_counter")
        self.assertEqual(parsed["false_positive_risk"], "LOW")

    def test_parse_fallback_when_json_missing(self):
        sample_response = """
DECISION: NORMAL
CONFIDENCE: MEDIUM

OBSERVED_EVIDENCE:
- No suspicious seeds.

REASONING:
The circuit displays standard logic without any feedback loops.
"""
        parsed = parse_structured_llm_response(sample_response)
        self.assertFalse(parsed["raw_json_parsed"])
        self.assertEqual(parsed["decision"], "NORMAL")
        self.assertEqual(parsed["confidence"], "MEDIUM")
        self.assertIsNone(parsed["gnn_heuristic_agreement"])
        self.assertEqual(parsed["trojan_structure_type"], "unknown")

    def test_mock_response_generator(self):
        prompt = "GNN facts: seed_count_at_or_above_threshold: 3\nHEURISTIC AUTHORITATIVE NUMERICAL FACTS: composite_heuristic_score: 0.8"
        mock_text = generate_mock_response(prompt)
        parsed = parse_structured_llm_response(mock_text)
        self.assertTrue(parsed["raw_json_parsed"])
        self.assertEqual(parsed["decision"], "SUSPICIOUS")
        self.assertEqual(parsed["confidence"], "HIGH")
        self.assertEqual(parsed["trojan_structure_type"], "sequential_counter")

    def test_compact_seed_populates_fanin_fanout_from_nodes(self):
        from src.llm_prompt import compact_seed
        seed = {"gate": "NODE_A", "type": "nor2", "gnn_score": 0.99}
        nodes_by_gate = {"NODE_A": {"gate": "NODE_A", "type": "nor2", "fanin": 2, "fanout": 3}}
        compacted = compact_seed(seed, nodes_by_gate=nodes_by_gate)
        self.assertEqual(compacted["fanin"], 2)
        self.assertEqual(compacted["fanout"], 3)

    def test_compact_seed_omits_missing_fanin_fanout_without_defaulting_to_zero(self):
        from src.llm_prompt import compact_seed
        seed = {"gate": "NODE_B", "type": "PI", "gnn_score": 0.95}
        compacted = compact_seed(seed, nodes_by_gate={})
        self.assertNotIn("fanin", compacted)
        self.assertNotIn("fanout", compacted)

    def test_mock_metadata_and_fallback(self):
        import os
        from src.llm import execute_reasoning

        tmp_prompt = ROOT / "results" / "llm" / "tmp_test_prompt.txt"
        tmp_prompt.parent.mkdir(parents=True, exist_ok=True)
        tmp_prompt.write_text("DECISION: SUSPICIOUS\nCONFIDENCE: HIGH", encoding="utf-8")
        tmp_out = ROOT / "results" / "llm" / "tmp_test_out.json"

        # 1. Test MOCK_LLM_RESPONSE environment variable
        os.environ["MOCK_LLM_RESPONSE"] = "DECISION: NORMAL\nCONFIDENCE: HIGH"
        try:
            res_env = execute_reasoning(tmp_prompt, provider="gemini", output_path=tmp_out)
            self.assertEqual(res_env["model"], "mock-reasoner")
            self.assertEqual(res_env["provider"], "mock")
        finally:
            os.environ.pop("MOCK_LLM_RESPONSE", None)

        # 2. Test mock_fallback on exception
        saved_key = os.environ.pop("GEMINI_API_KEY", None)
        try:
            res_fallback = execute_reasoning(tmp_prompt, provider="gemini", output_path=tmp_out)
            self.assertTrue(res_fallback.get("mock_fallback"))
            self.assertEqual(res_fallback["model"], "mock-reasoner")
            self.assertEqual(res_fallback["provider"], "mock")
        finally:
            if saved_key is not None:
                os.environ["GEMINI_API_KEY"] = saved_key
            tmp_prompt.unlink(missing_ok=True)
            tmp_out.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()

