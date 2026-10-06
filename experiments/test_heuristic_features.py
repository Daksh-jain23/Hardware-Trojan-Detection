import json
import sys
from pathlib import Path

# Add project root to sys.path
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


def main():
    print("==================================================")
    print("  PHASE 1: HEURISTIC MODULE VERIFICATION")
    print("==================================================")
    print(f"Loading evidence from: {EVIDENCE_PATH.name}")

    with open(EVIDENCE_PATH, "r") as f:
        evidence = json.load(f)

    print("Evidence loaded successfully.")

    # 1. Feature Extraction
    features = extract_heuristic_features(evidence)
    print("\n--- Extracted Heuristic Features (17 total) ---")
    gnn_features = [
        "max_gnn_score", "mean_gnn_score", "median_gnn_score",
        "std_gnn_score", "score_iqr", "high_confidence_count",
        "high_confidence_ratio", "confidence_margin"
    ]
    graph_features = [
        "region_size", "internal_edges", "boundary_edges",
        "connectivity", "structural_density", "sequential_count",
        "sequential_ratio", "exit_count", "exit_ratio",
        "po_proximity", "trigger_concentration"
    ]

    print("\n[GNN Distribution Features]")
    for name in gnn_features:
        print(f"  {name:25s}: {features[name]:.6f}")

    print("\n[Circuit Structural Features]")
    for name in graph_features:
        print(f"  {name:25s}: {features[name]:.6f}")

    # 2. End-to-End Analysis
    result = analyze_heuristic(evidence)

    print("\n--- Heuristic Detection Decision ---")
    print(f"  Composite Score       : {result['heuristic_score']:.6f}")
    print(f"  Decision Threshold    : {result['threshold']:.2f}")
    print(f"  Classification        : {result['decision']}")
    print(f"  Summary               : {result['summary']}")

    print("\n--- Factor Attribution (Top Contributors to Score) ---")
    for rank, factor in enumerate(result["factor_attribution"], start=1):
        print(
            f"  {rank}. {factor['feature']:22s} | "
            f"Value: {factor['value']:.4f} | "
            f"Weight: {factor['weight']:.4f} | "
            f"Contribution: {factor['contribution']:.4f} | "
            f"{factor['description']}"
        )

    print("\n--- Top Suspicious Nodes (GNN + Structural Ranking) ---")
    for rank, node in enumerate(result["top_suspicious_nodes"][:5], start=1):
        seq_tag = "[SEQ]" if node["is_sequential"] else "     "
        print(
            f"  {rank:2d}. {node['gate']:30s} {seq_tag} "
            f"GNN: {node['gnn_score']:.4f} | "
            f"Fanin: {node['fanin']} | Fanout: {node['fanout']} | "
            f"PO-Dist: {node['po_distance']} | "
            f"Priority: {node['composite_priority']:.4f}"
        )

    print("\n==================================================")
    print("  PHASE 1 TEST COMPLETED SUCCESSFULLY")
    print("==================================================")


if __name__ == "__main__":
    main()