import json
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.heuristic import (
    extract_heuristic_features,
    calculate_heuristic_score,
    classify_heuristic,
    explain_heuristic_decision,
    rank_suspicious_nodes,
    analyze_heuristic,
)

EVIDENCE_PATH = ROOT / "results" / "evidence" / "s13207_T421_evidence.json"


class TestHeuristicModule(unittest.TestCase):

    def setUp(self):
        self.assertTrue(EVIDENCE_PATH.exists(), f"Evidence file not found: {EVIDENCE_PATH}")
        with open(EVIDENCE_PATH, "r") as f:
            self.evidence = json.load(f)

    def test_feature_extraction(self):
        features = extract_heuristic_features(self.evidence)
        self.assertIsInstance(features, dict)

        required_keys = [
            "max_gnn_score", "mean_gnn_score", "median_gnn_score",
            "std_gnn_score", "score_iqr", "high_confidence_count",
            "high_confidence_ratio", "confidence_margin",
            "region_size", "internal_edges", "boundary_edges",
            "connectivity", "structural_density", "sequential_count",
            "sequential_ratio", "exit_count", "exit_ratio",
            "po_proximity", "trigger_concentration"
        ]
        for key in required_keys:
            self.assertIn(key, features)

        # Assert mathematical bounds
        self.assertTrue(0.0 <= features["max_gnn_score"] <= 1.0)
        self.assertTrue(0.0 <= features["connectivity"] <= 1.0)
        self.assertTrue(0.0 <= features["sequential_ratio"] <= 1.0)
        self.assertEqual(features["region_size"], 47.0)

    def test_scoring_and_classification(self):
        features = extract_heuristic_features(self.evidence)
        score = calculate_heuristic_score(features)
        self.assertTrue(0.0 <= score <= 1.0)

        decision = classify_heuristic(score, threshold=0.50)
        self.assertIn(decision, {"SUSPICIOUS", "NORMAL", "UNCERTAIN"})

    def test_attribution_and_ranking(self):
        result = analyze_heuristic(self.evidence)
        self.assertIn("heuristic_score", result)
        self.assertIn("factor_attribution", result)
        self.assertGreater(len(result["factor_attribution"]), 0)
        self.assertIn("top_suspicious_nodes", result)
        self.assertGreater(len(result["top_suspicious_nodes"]), 0)

        top_node = result["top_suspicious_nodes"][0]
        self.assertIn("composite_priority", top_node)
        self.assertIn("gnn_score", top_node)
        self.assertTrue(top_node["composite_priority"] > 0)

    def test_node_scoring_null_and_string_safety(self):
        # Synthetic evidence containing null and string edge cases
        synthetic_evidence = {
            "nodes": [
                {
                    "gate": "NODE_NULL_FIELDS",
                    "type": None,
                    "gnn_score": None,
                    "fanin": None,
                    "fanout": None,
                    "distance_to_output": None,
                },
                {
                    "gate": "NODE_STRING_FIELDS",
                    "type": "dffs2",
                    "gnn_score": "0.98",
                    "fanin": "2.0",
                    "fanout": "3",
                    "distance_to_output": "14.5",
                },
                {
                    "gate": "NODE_MISSING_FIELDS",
                },
            ]
        }
        ranked = rank_suspicious_nodes(synthetic_evidence)
        self.assertEqual(len(ranked), 3)

        # 1. Null fields node
        null_node = next(n for n in ranked if n["gate"] == "NODE_NULL_FIELDS")
        self.assertEqual(null_node["gnn_score"], 0.0)
        self.assertEqual(null_node["fanin"], 0)
        self.assertEqual(null_node["fanout"], 0)
        self.assertEqual(null_node["po_distance"], 999.0)

        # 2. String fields node
        str_node = next(n for n in ranked if n["gate"] == "NODE_STRING_FIELDS")
        self.assertEqual(str_node["gnn_score"], 0.98)
        self.assertEqual(str_node["fanin"], 2)
        self.assertEqual(str_node["fanout"], 3)
        self.assertEqual(str_node["po_distance"], 14.5)
        self.assertTrue(str_node["is_sequential"])

        # 3. Missing fields node
        missing_node = next(n for n in ranked if n["gate"] == "NODE_MISSING_FIELDS")
        self.assertEqual(missing_node["gnn_score"], 0.0)
        self.assertEqual(missing_node["fanin"], 0)
        self.assertEqual(missing_node["fanout"], 0)
        self.assertEqual(missing_node["po_distance"], 999.0)

    def test_load_optimized_weights_validation(self):
        import tempfile
        from src.heuristic import load_optimized_weights, DEFAULT_WEIGHTS, DEFAULT_HEURISTIC_THRESHOLD

        # Case 1: Empty dict -> should fall back to DEFAULT_WEIGHTS
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as f:
            json.dump({"optimal_weights": {}, "optimal_threshold": 0.45}, f)
            temp_path = Path(f.name)
        try:
            weights, threshold = load_optimized_weights(temp_path)
            self.assertEqual(weights, DEFAULT_WEIGHTS)
            self.assertEqual(threshold, 0.45)
        finally:
            temp_path.unlink(missing_ok=True)

        # Case 2: Zero-sum dict -> should fall back to DEFAULT_WEIGHTS
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as f:
            json.dump({"optimal_weights": {"feat1": 0.0, "feat2": 0.0}, "optimal_threshold": 0.45}, f)
            temp_path = Path(f.name)
        try:
            weights, threshold = load_optimized_weights(temp_path)
            self.assertEqual(weights, DEFAULT_WEIGHTS)
            self.assertEqual(threshold, 0.45)
        finally:
            temp_path.unlink(missing_ok=True)

        # Case 3: Valid numeric dict with float conversions
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as f:
            json.dump({"optimal_weights": {"max_gnn_score": "0.6", "connectivity": 0.4}, "optimal_threshold": 0.55}, f)
            temp_path = Path(f.name)
        try:
            weights, threshold = load_optimized_weights(temp_path)
            self.assertEqual(weights, {"max_gnn_score": 0.6, "connectivity": 0.4})
            self.assertEqual(threshold, 0.55)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_analyze_heuristic_threshold_selection(self):
        from src.heuristic import analyze_heuristic, DEFAULT_HEURISTIC_THRESHOLD

        # 1. Caller provides weights but NO threshold -> must use DEFAULT_HEURISTIC_THRESHOLD
        custom_weights = {"max_gnn_score": 0.8, "connectivity": 0.2}
        res_custom_no_tau = analyze_heuristic(self.evidence, weights=custom_weights, threshold=None)
        self.assertEqual(res_custom_no_tau["threshold"], DEFAULT_HEURISTIC_THRESHOLD)

        # 2. Caller provides weights AND explicit threshold -> must preserve explicit threshold
        res_custom_with_tau = analyze_heuristic(self.evidence, weights=custom_weights, threshold=0.72)
        self.assertEqual(res_custom_with_tau["threshold"], 0.72)

        # 3. Caller provides NO weights but explicit threshold -> must preserve explicit threshold
        res_no_w_with_tau = analyze_heuristic(self.evidence, weights=None, threshold=0.68)
        self.assertEqual(res_no_w_with_tau["threshold"], 0.68)


if __name__ == "__main__":
    unittest.main()
