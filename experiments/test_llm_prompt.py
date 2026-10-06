"""
Evaluation of Heuristic-Guided Prompt Engineering & LLM Interface (Phase 4).

Validates:
1. Baseline vs. Hybrid prompt construction.
2. Injection of authoritative heuristic facts, factor attributions, and contradiction guidance.
3. Integration of refined region compression metrics.
4. Parsing and extraction of structured JSON responses.
5. Strict constraint metadata tracking (heuristic_output_used: True/False).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

for p in [str(ROOT), str(SRC)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from llm_prompt import build_prompt
from llm import execute_reasoning, parse_structured_llm_response


def run_phase4_benchmark() -> Dict[str, Any]:
    evidence_path = ROOT / "results" / "anonymized" / "s13207_T421_evidence_anonymized.json"
    if not evidence_path.exists():
        raise FileNotFoundError(f"Evidence file missing: {evidence_path}")

    with evidence_path.open("r", encoding="utf-8") as f:
        evidence = json.load(f)

    print("============================================================")
    print("PHASE 4 BENCHMARK: PROMPT ENGINEERING & LLM INTERFACE")
    print("============================================================")
    print(f"Evidence File: {evidence_path.name}")

    # 1. Build Baseline Prompt
    baseline_prompt = build_prompt(evidence, mode="baseline")
    baseline_prompt_path = ROOT / "results" / "llm" / "s13207_T421_baseline_prompt.txt"
    baseline_prompt_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_prompt_path.write_text(baseline_prompt, encoding="utf-8")

    # 2. Build Hybrid Prompt (with simulated/cached refinement facts)
    refinement_metrics = {
        "original_region_size": 47,
        "refined_region_size": 35,
        "pruned_peripheral_leaves": 12,
        "retention_ratio": 0.7447,
        "noise_reduction_ratio": 0.2553,
        "core_anchors_preserved": True,
        "sequential_anchors_preserved": True,
    }
    hybrid_prompt = build_prompt(
        evidence,
        mode="hybrid",
        refined_region=refinement_metrics,
    )
    hybrid_prompt_path = ROOT / "results" / "llm" / "s13207_T421_hybrid_prompt.txt"
    hybrid_prompt_path.write_text(hybrid_prompt, encoding="utf-8")

    print("\n--- Prompt Metrics ---")
    print(f"Baseline Prompt Length: {len(baseline_prompt)} chars (~ {len(baseline_prompt)//4} tokens)")
    print(f"Hybrid Prompt Length  : {len(hybrid_prompt)} chars (~ {len(hybrid_prompt)//4} tokens)")

    # 3. Verify Hybrid Elements
    has_heuristic_facts = "HEURISTIC AUTHORITATIVE NUMERICAL FACTS" in hybrid_prompt
    has_refinement_metrics = "REGION REFINEMENT METRICS" in hybrid_prompt
    has_contradiction = "CONTRADICTION ANALYSIS & ARBITRATION GUIDELINES" in hybrid_prompt
    has_json_schema = "PART 1: STRICT JSON BLOCK" in hybrid_prompt
    has_node_priorities = "TOP SUSPICIOUS NODES (HEURISTIC-GUIDED PRIORITY)" in hybrid_prompt

    print("\n--- Hybrid Prompt Content Verification ---")
    print(f"Heuristic Numerical Facts Present : {has_heuristic_facts}")
    print(f"Region Refinement Metrics Present : {has_refinement_metrics}")
    print(f"Contradiction Analysis Guidance   : {has_contradiction}")
    print(f"Strict JSON Schema Specified      : {has_json_schema}")
    print(f"Heuristic Node Priorities Present : {has_node_priorities}")

    # 4. Verify Baseline Independence
    baseline_excludes_heuristic = "HEURISTIC AUTHORITATIVE NUMERICAL FACTS" not in baseline_prompt
    baseline_declares_independence = "The heuristic is an independent comparison method" in baseline_prompt
    print(f"Baseline Excludes Heuristic Facts : {baseline_excludes_heuristic}")
    print(f"Baseline Declares Independence    : {baseline_declares_independence}")

    # 5. Execute LLM Reasoning (Mock Runner for reproducible offline verification)
    print("\n--- Executing LLM Reasoning (Baseline & Hybrid) ---")
    baseline_result = execute_reasoning(
        prompt_path=baseline_prompt_path,
        mock=True,
    )
    hybrid_result = execute_reasoning(
        prompt_path=hybrid_prompt_path,
        mock=True,
    )

    # 6. Verify Execution Constraints & Metadata
    hybrid_flag = hybrid_result["llm_constraints"]["heuristic_output_used"]
    baseline_flag = baseline_result["llm_constraints"]["heuristic_output_used"]

    print("\n--- Constraints & Metadata Tracking ---")
    print(f"Hybrid Prompt - heuristic_output_used   : {hybrid_flag} (Expected: True)")
    print(f"Baseline Prompt - heuristic_output_used : {baseline_flag} (Expected: False)")

    # 7. Check Structured Output Quality
    struct_out = hybrid_result["structured_output"]
    print("\n--- Structured JSON Output Validation ---")
    print(f"Decision              : {struct_out.get('decision')}")
    print(f"Confidence            : {struct_out.get('confidence')}")
    print(f"Agreement             : {struct_out.get('gnn_heuristic_agreement')}")
    print(f"Trojan Archetype      : {struct_out.get('trojan_structure_type')}")
    print(f"False Positive Risk   : {struct_out.get('false_positive_risk')}")
    print(f"Arbitration Rationale : {struct_out.get('arbitration_rationale')[:80]}...")

    benchmark_summary = {
        "circuit": "s13207_T421",
        "baseline_prompt_chars": len(baseline_prompt),
        "baseline_prompt_tokens": len(baseline_prompt) // 4,
        "hybrid_prompt_chars": len(hybrid_prompt),
        "hybrid_prompt_tokens": len(hybrid_prompt) // 4,
        "verification": {
            "has_heuristic_facts": has_heuristic_facts,
            "has_refinement_metrics": has_refinement_metrics,
            "has_contradiction": has_contradiction,
            "has_json_schema": has_json_schema,
            "has_node_priorities": has_node_priorities,
            "baseline_excludes_heuristic": baseline_excludes_heuristic,
            "baseline_declares_independence": baseline_declares_independence,
            "hybrid_heuristic_output_used": hybrid_flag,
            "baseline_heuristic_output_used": baseline_flag,
            "structured_json_valid": struct_out.get("raw_json_parsed", False),
        },
        "llm_output": {
            "decision": struct_out.get("decision"),
            "confidence": struct_out.get("confidence"),
            "trojan_structure_type": struct_out.get("trojan_structure_type"),
            "gnn_heuristic_agreement": struct_out.get("gnn_heuristic_agreement"),
            "false_positive_risk": struct_out.get("false_positive_risk"),
        }
    }

    out_file = ROOT / "results" / "llm" / "phase4_prompt_benchmark.json"
    out_file.write_text(json.dumps(benchmark_summary, indent=2), encoding="utf-8")
    print(f"\nSaved benchmark metrics to: {out_file.resolve()}")
    return benchmark_summary


if __name__ == "__main__":
    run_phase4_benchmark()
