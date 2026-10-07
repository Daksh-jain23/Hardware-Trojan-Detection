"""
Unit tests for evaluation metrics and pipeline execution components.
"""

import sys
import unittest
from pathlib import Path

import numpy as np
import torch

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from evaluation import calculate_metrics, print_comparative_table


class TestEvaluationMetrics(unittest.TestCase):
    def test_calculate_metrics_perfect(self):
        y_true = np.array([0, 0, 0, 1, 1])
        probs = np.array([0.1, 0.2, 0.05, 0.95, 0.98])
        metrics = calculate_metrics(y_true, probs, threshold=0.90)

        self.assertEqual(metrics["accuracy"], 1.0)
        self.assertEqual(metrics["precision"], 1.0)
        self.assertEqual(metrics["recall"], 1.0)
        self.assertEqual(metrics["f1"], 1.0)
        self.assertEqual(metrics["fp_rate"], 0.0)
        self.assertEqual(metrics["fn_rate"], 0.0)
        self.assertEqual(metrics["specificity"], 1.0)
        self.assertEqual(metrics["tp"], 2)
        self.assertEqual(metrics["tn"], 3)
        self.assertEqual(metrics["fp"], 0)
        self.assertEqual(metrics["fn"], 0)

    def test_calculate_metrics_with_errors(self):
        y_true = np.array([0, 0, 1, 1])
        probs = np.array([0.8, 0.2, 0.9, 0.3])
        # Preds: [1, 0, 1, 0]
        # TN=1, FP=1, TP=1, FN=1
        metrics = calculate_metrics(y_true, probs, threshold=0.5)

        self.assertEqual(metrics["tn"], 1)
        self.assertEqual(metrics["fp"], 1)
        self.assertEqual(metrics["tp"], 1)
        self.assertEqual(metrics["fn"], 1)
        self.assertAlmostEqual(metrics["fp_rate"], 0.5)
        self.assertAlmostEqual(metrics["fn_rate"], 0.5)
        self.assertAlmostEqual(metrics["specificity"], 0.5)
        self.assertAlmostEqual(metrics["accuracy"], 0.5)

    def test_comparative_table_runs_without_exception(self):
        gnn = {"accuracy": 0.999, "precision": 0.95, "recall": 0.80, "f1": 0.86,
               "fp_rate": 0.0001, "fn_rate": 0.20, "specificity": 0.9999,
               "roc_auc": 0.99, "average_precision": 0.95, "tp": 160, "fp": 10, "tn": 86000, "fn": 40, "total_nodes": 86210}
        heur = {"accuracy": 0.998, "precision": 1.0, "recall": 0.17, "f1": 0.29,
                "fp_rate": 0.0, "fn_rate": 0.83, "specificity": 1.0,
                "roc_auc": 0.72, "average_precision": 0.18, "tp": 34, "fp": 0, "tn": 86010, "fn": 166, "total_nodes": 86210}
        # Should not raise any error
        print_comparative_table(gnn, heur)


if __name__ == "__main__":
    unittest.main()

