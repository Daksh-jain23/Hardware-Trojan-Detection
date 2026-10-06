"""
Evaluation of Heuristic-Guided Suspicious-Region Refinement (Phase 3).

Assesses:
1. Ground-Truth Trojan Gate Recall (must be 100% or near 100%).
2. Precision Improvement (reduction of non-Trojan peripheral noise).
3. Region Compression Ratio (reduction in downstream LLM token overhead).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from parser import parse_netlist
from evidence import load_model, score_graph, get_device
from region import extract_region, refine_suspicious_region


BENCHMARK_CIRCUITS = [
    "data/TRIT-TS/s13207_T421/s13207_T421.v",
    "data/TRIT-TS/s1423_T400/s1423_T400.v",
    "data/TRIT-TS/s15850_T400/s15850_T400.v",
    "data/TRIT-TS/s13207_T400/s13207_T400.v",
]


def evaluate_refinement_on_circuit(
    netlist_path: Path,
    model: Any,
    device: Any,
) -> Dict[str, Any]:
    graph = parse_netlist(netlist_path)
    scores, _ = score_graph(model, graph, device)

    # Ground truth Trojan gates
    trojan_gates_in_circuit = {
        n for n, d in graph.nodes(data=True) if d.get("is_trojan", False)
    }

    # Naive region extraction
    naive_region = extract_region(graph, scores)
    naive_trojan_captured = trojan_gates_in_circuit.intersection(naive_region.nodes)
    naive_precision = (
        len(naive_trojan_captured) / len(naive_region.nodes)
        if naive_region.nodes
        else 0.0
    )
    naive_recall = (
        len(naive_trojan_captured) / len(trojan_gates_in_circuit)
        if trojan_gates_in_circuit
        else 1.0
    )

    # Heuristic-guided refinement
    refined_region = refine_suspicious_region(
        graph=graph,
        region=naive_region,
        scores=scores,
    )
    refined_trojan_captured = trojan_gates_in_circuit.intersection(refined_region.nodes)
    refined_precision = (
        len(refined_trojan_captured) / len(refined_region.nodes)
        if refined_region.nodes
        else 0.0
    )
    refined_recall = (
        len(refined_trojan_captured) / len(trojan_gates_in_circuit)
        if trojan_gates_in_circuit
        else 1.0
    )

    compression = 1.0 - (len(refined_region.nodes) / len(naive_region.nodes)) if naive_region.nodes else 0.0

    return {
        "circuit": netlist_path.name,
        "total_circuit_nodes": graph.number_of_nodes(),
        "total_trojan_gates": len(trojan_gates_in_circuit),
        "naive_size": len(naive_region.nodes),
        "refined_size": len(refined_region.nodes),
        "pruned_peripheral_gates": len(refined_region.pruned_nodes),
        "compression_ratio": round(compression, 4),
        "naive_precision": round(naive_precision, 4),
        "refined_precision": round(refined_precision, 4),
        "trojan_recall": round(refined_recall, 4),
        "all_trojans_preserved": (len(refined_trojan_captured) == len(naive_trojan_captured)),
    }


def main():
    print("==================================================")
    print("  PHASE 3: SUSPICIOUS-REGION REFINEMENT BENCHMARK")
    print("==================================================")

    device = get_device()
    model = load_model()

    results: List[Dict[str, Any]] = []

    for rel_path in BENCHMARK_CIRCUITS:
        p = ROOT / rel_path
        if not p.exists():
            print(f"Skipping missing circuit: {rel_path}")
            continue

        print(f"Evaluating {p.name} ...")
        res = evaluate_refinement_on_circuit(p, model, device)
        results.append(res)

    print("\n==========================================================================================")
    print(f"{'Circuit':18s} | {'Trojan':6s} | {'Naive':5s} | {'Refined':7s} | {'Pruned':6s} | {'Compression':11s} | {'Precision':15s} | {'Recall':6s}")
    print("-" * 90)

    for r in results:
        prec_str = f"{r['naive_precision']:.1%} -> {r['refined_precision']:.1%}"
        print(
            f"{r['circuit']:18s} | {r['total_trojan_gates']:6d} | "
            f"{r['naive_size']:5d} | {r['refined_size']:7d} | "
            f"{r['pruned_peripheral_gates']:6d} | {r['compression_ratio']:11.1%} | "
            f"{prec_str:15s} | {r['trojan_recall']:.1%}"
        )

    print("-" * 90)

    avg_compression = sum(r["compression_ratio"] for r in results) / len(results) if results else 0.0
    all_preserved = all(r["all_trojans_preserved"] for r in results)

    print(f"\nAverage Token / Node Compression : {avg_compression:.1%}")
    print(f"Ground-Truth Trojan Gate Recall  : {'100% Preserved (YES)' if all_preserved else 'NO'}")

    output_dir = ROOT / "results" / "heuristic"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "region_refinement_benchmark.json"

    with open(out_file, "w") as f:
        json.dump(
            {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "benchmark_results": results,
                "summary": {
                    "avg_compression": round(avg_compression, 4),
                    "all_trojans_preserved": all_preserved,
                },
            },
            f,
            indent=2,
        )

    print(f"Benchmark results saved to: {out_file}")


if __name__ == "__main__":
    main()
