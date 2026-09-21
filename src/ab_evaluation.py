"""
Controlled A/B Evaluation Framework for Hardware Trojan Structural Reasoning.

Purpose:
Scientifically evaluate whether the LLM's structural reasoning:
1. Actually identifies Trojan logic from structural evidence rather than noise.
2. Is robust when presentation order is swapped (Swap Consistency).
3. Exhibits position bias (e.g. always favoring 'Region A' regardless of content).
4. Free of identifier leakage (zero benchmark or Trojan naming clues).

Evaluation Architecture:
- Ground-truth Trojan Region (around nodes where is_trojan=True)
- Matched Clean Region (non-Trojan subnetwork of similar size and depth)

Trial 1:
  Region A = Trojan
  Region B = Clean

Trial 2 (Swapped):
  Region A = Clean
  Region B = Trojan

Both regions are fully anonymized with neutral IDs before LLM inference.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx
import numpy as np

# Ensure src on sys.path
SRC_DIR = Path(__file__).resolve().parent
ROOT = SRC_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from parser import parse_netlist
from anonymizer import anonymize_evidence, assert_no_leakage
from llm import run_llm

DEFAULT_OUTPUT_DIR = ROOT / "results" / "ab_evaluation"


# ============================================================
# Region Extraction (Trojan & Clean)
# ============================================================

def extract_trojan_region(
    graph: nx.DiGraph,
    hops: int = 2,
    max_size: int = 50,
) -> Set[str]:
    """Extract neighborhood around ground-truth Trojan nodes."""
    trojan_nodes = {
        n for n in graph.nodes()
        if graph.nodes[n].get("is_trojan", False)
    }

    if not trojan_nodes:
        return set()

    region = set(trojan_nodes)
    frontier = set(trojan_nodes)

    for _ in range(hops):
        next_frontier = set()
        for node in frontier:
            for nbr in list(graph.predecessors(node)) + list(graph.successors(node)):
                if nbr not in region:
                    next_frontier.add(nbr)
                    region.add(nbr)
                    if len(region) >= max_size:
                        return region
        frontier = next_frontier

    return region


def extract_matched_clean_region(
    graph: nx.DiGraph,
    trojan_region: Set[str],
    target_size: int,
    hops: int = 2,
    seed_random: int = 42,
) -> Set[str]:
    """
    Extract a matched clean region from the circuit with zero Trojan nodes
    and disconnected from the Trojan region.
    """
    rng = random.Random(seed_random)

    # Candidate clean nodes: not in trojan_region, not Trojan, and not 1-hop from trojan_region
    forbidden = set(trojan_region)
    for n in trojan_region:
        forbidden.update(graph.predecessors(n))
        forbidden.update(graph.successors(n))

    candidates = [
        n for n in graph.nodes()
        if n not in forbidden
        and not graph.nodes[n].get("is_trojan", False)
        and graph.nodes[n].get("gate_type") not in {"PI", "PO"}
    ]

    if not candidates:
        # Fallback to any non-trojan node
        candidates = [
            n for n in graph.nodes()
            if not graph.nodes[n].get("is_trojan", False)
        ]

    # Try several random seeds to find a well-connected clean subgraph of target size
    best_region: Set[str] = set()

    for seed_node in rng.sample(candidates, min(len(candidates), 20)):
        cur_region = {seed_node}
        frontier = {seed_node}

        for _ in range(hops + 1):
            next_frontier = set()
            for node in frontier:
                for nbr in list(graph.predecessors(node)) + list(graph.successors(node)):
                    if nbr not in forbidden and nbr not in cur_region:
                        cur_region.add(nbr)
                        next_frontier.add(nbr)
                        if len(cur_region) >= target_size:
                            return cur_region
            frontier = next_frontier

        if len(cur_region) > len(best_region):
            best_region = cur_region

    return best_region


# ============================================================
# Compact Structural Evidence for a Region
# ============================================================

def compute_region_structural_evidence(
    graph: nx.DiGraph,
    region: Set[str],
) -> Dict[str, Any]:
    """Compute deterministic structural metrics for a specific subnetwork."""
    region = set(region)
    subgraph = graph.subgraph(region)

    internal_edges = 0
    boundary_edges = 0
    region_exits = set()

    for node in region:
        for succ in graph.successors(node):
            if succ in region:
                internal_edges += 1
            else:
                boundary_edges += 1
                region_exits.add(node)
        for pred in graph.predecessors(node):
            if pred not in region:
                boundary_edges += 1

    # Gate type distribution
    gate_types: Dict[str, int] = {}
    sequential_gates: List[str] = []

    for node in region:
        gt = str(graph.nodes[node].get("gate_type", "unknown")).lower()
        gate_types[gt] = gate_types.get(gt, 0) + 1
        if any(st in gt for st in ["dff", "latch"]):
            sequential_gates.append(node)

    # Representative nodes summary
    nodes_summary = []
    for node in sorted(region)[:15]:
        nodes_summary.append({
            "gate": node,
            "gate_type": graph.nodes[node].get("gate_type", ""),
            "fanin": graph.in_degree(node),
            "fanout": graph.out_degree(node),
            "region_fanin": len([p for p in graph.predecessors(node) if p in region]),
            "region_fanout": len([s for s in graph.successors(node) if s in region]),
        })

    return {
        "region_size": len(region),
        "internal_edges": internal_edges,
        "boundary_edges": boundary_edges,
        "region_exits_count": len(region_exits),
        "region_exits": list(region_exits)[:10],
        "gate_types": gate_types,
        "sequential_gate_count": len(sequential_gates),
        "sequential_gates": sequential_gates[:10],
        "representative_nodes": nodes_summary,
    }


# ============================================================
# A/B Prompt Formulation & Parsing
# ============================================================

def build_ab_prompt(
    region_a_evidence: Dict[str, Any],
    region_b_evidence: Dict[str, Any],
) -> str:
    """
    Build neutral comparative prompt presenting Region A and Region B.
    Neither region mentions Trojan labels, ground truth, or original identifiers.
    """
    prompt = f"""
You are an expert hardware security evaluator comparing two gate-level circuit regions (Region A and Region B).

Both regions come from digital netlists, and one or both may contain suspicious or Trojan-like structural patterns
(such as hidden comparator trees, isolated sequential counters, or anomalous state-holding clusters).
All node identifiers have been anonymized to neutral format (e.g. NODE_0001) to ensure unbiased structural evaluation.

============================================================
REGION A STRUCTURAL EVIDENCE
============================================================
{json.dumps(region_a_evidence, indent=2)}

============================================================
REGION B STRUCTURAL EVIDENCE
============================================================
{json.dumps(region_b_evidence, indent=2)}

============================================================
EVALUATION INSTRUCTIONS
============================================================
Carefully compare the topology, internal connectivity, gate-type composition, and sequential structure of Region A versus Region B:
1. Examine internal edge density vs boundary crossings in both regions.
2. Examine whether sequential gates form isolated feedback/counter structures or standard datapath pipelines.
3. Note any trigger-like gate configurations (e.g. high fan-in comparators with narrow exit points).
4. Maintain strict scientific objectivity: do not assume Region A is more suspicious merely because it is listed first.
5. Provide a comparative structural explanation and identify which region is MORE SUSPICIOUS, or if they are EQUALLY_SUSPICIOUS / EQUALLY_NORMAL.

============================================================
REQUIRED OUTPUT FORMAT
============================================================
ASSESSMENT: <REGION_A | REGION_B | NEITHER>
CONFIDENCE: <LOW | MEDIUM | HIGH>

OBSERVED_DIFFERENCES:
- 2 to 4 concrete comparative observations between Region A and Region B

REASONING:
A short paragraph explaining which region exhibits topology more characteristic of hidden/Trojan logic and why.
""".strip()

    assert_no_leakage(prompt)
    return prompt


def parse_ab_response(response_text: str) -> Dict[str, str]:
    """Parse the structured decision from LLM comparative response."""
    match = re.search(
        r"ASSESSMENT\s*:\s*(REGION_A|REGION_B|NEITHER)",
        response_text,
        flags=re.IGNORECASE,
    )
    assessment = match.group(1).upper() if match else "NEITHER"

    conf_match = re.search(
        r"CONFIDENCE\s*:\s*(LOW|MEDIUM|HIGH)",
        response_text,
        flags=re.IGNORECASE,
    )
    confidence = conf_match.group(1).upper() if conf_match else "LOW"

    return {
        "assessment": assessment,
        "confidence": confidence,
        "raw_response": response_text,
    }


# ============================================================
# Core Controlled A/B Evaluation
# ============================================================

def run_controlled_ab_test(
    netlist_path: Path,
    hops: int = 2,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    skip_llm: bool = False,
) -> Dict[str, Any]:
    """
    Execute full controlled A/B evaluation with swap consistency test.

    Trial 1: Region A = Trojan, Region B = Clean
    Trial 2: Region A = Clean,  Region B = Trojan
    """
    print("=" * 60)
    print("CONTROLLED A/B EVALUATION: SWAP CONSISTENCY")
    print("=" * 60)
    print("Netlist:", netlist_path.resolve())

    # 1. Parse netlist
    graph = parse_netlist(netlist_path)

    # 2. Extract regions
    trojan_region = extract_trojan_region(graph, hops=hops)
    if not trojan_region:
        raise ValueError(f"No ground-truth Trojan nodes found in netlist: {netlist_path}")

    clean_region = extract_matched_clean_region(
        graph,
        trojan_region=trojan_region,
        target_size=len(trojan_region),
        hops=hops,
    )

    print(f"Trojan region size: {len(trojan_region)} nodes")
    print(f"Matched clean size: {len(clean_region)} nodes")

    # 3. Compute structural evidence
    trojan_ev = compute_region_structural_evidence(graph, trojan_region)
    clean_ev = compute_region_structural_evidence(graph, clean_region)

    # 4. Anonymize both independently
    anon_trojan, _ = anonymize_evidence(trojan_ev)
    anon_clean, _ = anonymize_evidence(clean_ev)

    # TRIAL 1: A = Trojan, B = Clean
    prompt_trial_1 = build_ab_prompt(anon_trojan, anon_clean)

    # TRIAL 2: A = Clean, B = Trojan (SWAPPED)
    prompt_trial_2 = build_ab_prompt(anon_clean, anon_trojan)

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = netlist_path.stem

    p1_file = output_dir / f"{stem}_ab_trial1_prompt.txt"
    p2_file = output_dir / f"{stem}_ab_trial2_swapped_prompt.txt"
    p1_file.write_text(prompt_trial_1, encoding="utf-8")
    p2_file.write_text(prompt_trial_2, encoding="utf-8")

    if skip_llm:
        print("\nLLM inference skipped (--skip-llm). Prompts generated successfully.")
        return {
            "circuit": stem,
            "trojan_region_size": len(trojan_region),
            "clean_region_size": len(clean_region),
            "trial_1_prompt": str(p1_file),
            "trial_2_prompt": str(p2_file),
        }

    print("\nRunning Trial 1 (A = Trojan, B = Clean)...")
    res1_raw = run_llm(prompt_trial_1)
    res1 = parse_ab_response(res1_raw)
    print(f"       Trial 1 Result: Assessment = {res1['assessment']}, Confidence = {res1['confidence']}")

    print("\nRunning Trial 2 Swapped (A = Clean, B = Trojan)...")
    res2_raw = run_llm(prompt_trial_2)
    res2 = parse_ab_response(res2_raw)
    print(f"       Trial 2 Result: Assessment = {res2['assessment']}, Confidence = {res2['confidence']}")

    # ============================================================
    # Metrics Evaluation
    # ============================================================
    # Ground truth: Trojan is Region A in Trial 1, and Region B in Trial 2.
    correct_trial_1 = (res1["assessment"] == "REGION_A")
    correct_trial_2 = (res2["assessment"] == "REGION_B")

    # Swap consistency: Did the LLM pick the SAME underlying physical entity?
    # Consistent if: (picks A in Trial 1 AND B in Trial 2) OR (picks B in Trial 1 AND A in Trial 2) OR (picks NEITHER in both)
    swap_consistent = (
        (res1["assessment"] == "REGION_A" and res2["assessment"] == "REGION_B") or
        (res1["assessment"] == "REGION_B" and res2["assessment"] == "REGION_A") or
        (res1["assessment"] == "NEITHER" and res2["assessment"] == "NEITHER")
    )

    # Position bias: Did the LLM always pick the first option (REGION_A) or always second (REGION_B)?
    position_bias = (res1["assessment"] == res2["assessment"] and res1["assessment"] in {"REGION_A", "REGION_B"})

    metrics = {
        "circuit": stem,
        "trojan_region_size": len(trojan_region),
        "clean_region_size": len(clean_region),
        "trial_1": {
            "assignment": {"REGION_A": "Trojan", "REGION_B": "Clean"},
            "assessment": res1["assessment"],
            "confidence": res1["confidence"],
            "correct": correct_trial_1,
        },
        "trial_2": {
            "assignment": {"REGION_A": "Clean", "REGION_B": "Trojan"},
            "assessment": res2["assessment"],
            "confidence": res2["confidence"],
            "correct": correct_trial_2,
        },
        "evaluation_metrics": {
            "correctness_trial_1": correct_trial_1,
            "correctness_trial_2": correct_trial_2,
            "overall_accuracy": 1.0 if (correct_trial_1 and correct_trial_2) else (0.5 if (correct_trial_1 or correct_trial_2) else 0.0),
            "swap_consistent": swap_consistent,
            "position_bias_detected": position_bias,
            "identifier_leakage_detected": False,
        },
    }

    result_file = output_dir / f"{stem}_ab_result.json"
    with result_file.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "=" * 60)
    print("A/B EVALUATION METRICS SUMMARY")
    print("=" * 60)
    print(f"Circuit             : {stem}")
    print(f"Trial 1 Correct     : {correct_trial_1} ({res1['assessment']})")
    print(f"Trial 2 Correct     : {correct_trial_2} ({res2['assessment']})")
    print(f"Swap Consistent     : {swap_consistent}")
    print(f"Position Bias       : {position_bias}")
    print(f"Result saved to     : {result_file.resolve()}")

    return metrics


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Controlled A/B Evaluation Framework with Swap Consistency."
    )
    parser.add_argument(
        "--circuit",
        type=Path,
        required=True,
        help="Path to a Verilog netlist containing known Trojan logic.",
    )
    parser.add_argument(
        "--hops",
        type=int,
        default=2,
        help="Region expansion hops (default: 2).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to save A/B evaluation results.",
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Generate prompts and evidence but skip LLM inference.",
    )

    args = parser.parse_args()

    run_controlled_ab_test(
        netlist_path=args.circuit,
        hops=args.hops,
        output_dir=args.output_dir,
        skip_llm=args.skip_llm,
    )


if __name__ == "__main__":
    main()
