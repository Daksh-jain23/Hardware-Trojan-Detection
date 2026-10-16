"""
Actor-Critic Verification Engine for Hardware Trojan Detection.

This module implements a multi-turn neuro-symbolic verification loop:
1. Deterministic Pre-Audit: Compares Actor's natural language claims
   against ground-truth structural evidence (detects hallucinated DFFs,
   exaggerated density, or fabricated boundary exits).
2. Critic Audit Agent: Acts as a skeptical Senior ASIC Verification Auditor,
   challenging the initial classification against benign functional hypotheses
   (e.g., standard FSMs, arithmetic adders, carry trees, memory decoders).
3. Actor Revision: Revises the assessment in light of the auditor's critique,
   producing a finalized, verified decision (REGION_A, REGION_B, or NEITHER).

Supports both Ollama and Gemini with offline resilience.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple


# ============================================================
# 1. Deterministic Pre-Audit (Rule-Based Fact Checker)
# ============================================================

def audit_actor_factual_claims(
    actor_response: str,
    evidence_a: Dict[str, Any],
    evidence_b: Dict[str, Any],
) -> List[str]:
    """
    Rigorously verifies factual numbers and claims made by the Actor
    against the actual mathematical evidence dictionaries.
    Returns a list of warning flags for any hallucinations detected.
    """
    warnings = []
    text_lower = actor_response.lower()

    # Determine which region the actor targeted
    target_region = None
    if "region a" in text_lower and "region b" not in text_lower:
        target_region = "A"
    elif "region b" in text_lower and "region a" not in text_lower:
        target_region = "B"

    # Check for DFF count discrepancies
    dff_matches = re.findall(r"(\d+)\s*(?:sequential|flip-flop|dff)", text_lower)
    if dff_matches:
        claimed_dff = int(dff_matches[0])
        actual_dff_a = evidence_a.get("sequential_gate_count", 0)
        actual_dff_b = evidence_b.get("sequential_gate_count", 0)
        if target_region == "A" and claimed_dff != actual_dff_a:
            warnings.append(
                f"[FACT-CHECK]: Claimed {claimed_dff} sequential flip-flops for Region A, "
                f"but ground-truth evidence indicates exactly {actual_dff_a} DFFs."
            )
        elif target_region == "B" and claimed_dff != actual_dff_b:
            warnings.append(
                f"[FACT-CHECK]: Claimed {claimed_dff} sequential flip-flops for Region B, "
                f"but ground-truth evidence indicates exactly {actual_dff_b} DFFs."
            )

    # Check internal edge density claims
    density_matches = re.findall(r"density\s*(?:of|is|:)?\s*([0-9]+\.?[0-9]*)\s*(%?)", text_lower)
    if density_matches:
        val_str, is_pct = density_matches[0]
        claimed_density = float(val_str)
        # Normalize percentage claims (e.g. 78% -> 0.78), but keep raw ratios (e.g. 1.38)
        if is_pct == "%" or (claimed_density > 10.0 and not is_pct):
            claimed_density /= 100.0

        actual_density_a = float(evidence_a.get("internal_edge_density", 0.0))
        actual_density_b = float(evidence_b.get("internal_edge_density", 0.0))
        if target_region == "A" and abs(claimed_density - actual_density_a) > 0.15:
            warnings.append(
                f"[FACT-CHECK]: Claimed internal edge density of {claimed_density:.2f} for Region A, "
                f"but actual calculated density is {actual_density_a:.2f}."
            )
        elif target_region == "B" and abs(claimed_density - actual_density_b) > 0.15:
            warnings.append(
                f"[FACT-CHECK]: Claimed internal edge density of {claimed_density:.2f} for Region B, "
                f"but actual calculated density is {actual_density_b:.2f}."
            )

    # Check for boundary exit ratio claims
    exit_matches = re.findall(r"exit\s*ratio\s*(?:of|is|:)?\s*([0-9]+\.?[0-9]*)\s*(%?)", text_lower)
    if exit_matches:
        val_str, is_pct = exit_matches[0]
        claimed_exit = float(val_str)
        if is_pct == "%" or claimed_exit > 1.0:
            claimed_exit /= 100.0

        actual_exit_a = float(evidence_a.get("exit_ratio", 1.0))
        actual_exit_b = float(evidence_b.get("exit_ratio", 1.0))
        if target_region == "A" and abs(claimed_exit - actual_exit_a) > 0.15:
            warnings.append(
                f"[FACT-CHECK]: Claimed exit ratio {claimed_exit:.2f} for Region A, "
                f"but actual exit ratio is {actual_exit_a:.2f}."
            )
        elif target_region == "B" and abs(claimed_exit - actual_exit_b) > 0.15:
            warnings.append(
                f"[FACT-CHECK]: Claimed exit ratio {claimed_exit:.2f} for Region B, "
                f"but actual exit ratio is {actual_exit_b:.2f}."
            )

    # Check for sequential / FSM hallucination on combinational logic
    if "fsm" in text_lower or "counter" in text_lower:
        actual_dff_a = evidence_a.get("sequential_gate_count", 0)
        actual_dff_b = evidence_b.get("sequential_gate_count", 0)
        target_dff = actual_dff_a if target_region == "A" else (actual_dff_b if target_region == "B" else min(actual_dff_a, actual_dff_b))
        if target_dff == 0:
            warnings.append(
                f"[FACT-CHECK]: Claimed sequential state counter/FSM Trojan for Region {target_region or 'candidate'}, "
                f"but ground-truth evidence indicates exactly 0 sequential flip-flops (pure combinational logic)."
            )

    # Check for invalid NEITHER claim when strong GNN seeds exist
    if "neither" in text_lower:
        max_seeds = max(evidence_a.get("gnn_seeds_count", 0), evidence_b.get("gnn_seeds_count", 0))
        max_score = max(evidence_a.get("max_gnn_score", 0.0), evidence_b.get("max_gnn_score", 0.0))
        if max_seeds >= 3 and max_score >= 0.65:
            strong_reg = "A" if evidence_a.get("gnn_seeds_count", 0) >= evidence_b.get("gnn_seeds_count", 0) else "B"
            warnings.append(
                f"[FACT-CHECK]: Actor concluded NEITHER, but Region {strong_reg} contains {max_seeds} confirmed GNN suspicious seeds "
                f"with peak score {max_score:.4f}. NEITHER is strictly forbidden when high-confidence GNN seeds are localized."
            )

    return warnings


# ============================================================
# 2. Critic Prompt Construction
# ============================================================

def build_critic_audit_prompt(
    evidence_a: Dict[str, Any],
    evidence_b: Dict[str, Any],
    actor_response: str,
    fact_check_warnings: List[str],
) -> str:
    """
    Constructs the prompt for the Critic agent to audit the Actor's report.
    """
    warning_block = ""
    if fact_check_warnings:
        warning_block = "AUTOMATED PRE-AUDIT WARNINGS DETECTED:\n" + "\n".join(
            f"- {w}" for w in fact_check_warnings
        ) + "\n\n"

    prompt = f"""You are a Senior ASIC Verification Engineer and Hardware Security Auditor.
Your primary mission is to RIGOROUSLY AUDIT a junior analyst's Hardware Trojan detection report, PREVENT FALSE POSITIVES, and ENSURE STRICT FACTUAL GROUNDING.

{warning_block}------------------------------------------------------------
ANONYMIZED STRUCTURAL EVIDENCE PROVIDED TO ANALYST:
------------------------------------------------------------
REGION A:
- Size: {evidence_a.get('region_size')} gates | GNN Seeds: {evidence_a.get('gnn_seeds_count', 0)}
- Max GNN: {evidence_a.get('max_gnn_score', 0.0)} | Avg GNN: {evidence_a.get('avg_gnn_score', 0.0)}
- Internal Edge Density: {evidence_a.get('internal_edge_density')} | Internal Edges: {evidence_a.get('internal_edges')}
- Boundary Exits Count: {evidence_a.get('region_exits_count')} (Exit Ratio: {evidence_a.get('exit_ratio')})
- Sequential DFFs: {evidence_a.get('sequential_gate_count')}
- Gate Types: {json.dumps(evidence_a.get('gate_types', {}))}

REGION B:
- Size: {evidence_b.get('region_size')} gates | GNN Seeds: {evidence_b.get('gnn_seeds_count', 0)}
- Max GNN: {evidence_b.get('max_gnn_score', 0.0)} | Avg GNN: {evidence_b.get('avg_gnn_score', 0.0)}
- Internal Edge Density: {evidence_b.get('internal_edge_density')} | Internal Edges: {evidence_b.get('internal_edges')}
- Boundary Exits Count: {evidence_b.get('region_exits_count')} (Exit Ratio: {evidence_b.get('exit_ratio')})
- Sequential DFFs: {evidence_b.get('sequential_gate_count')}
- Gate Types: {json.dumps(evidence_b.get('gate_types', {}))}

------------------------------------------------------------
ANALYST'S PROPOSED REPORT:
------------------------------------------------------------
{actor_response.strip()}

------------------------------------------------------------
CRITIC AUDITING DIRECTIVES:
------------------------------------------------------------
1. ASYMMETRIC RISK PRINCIPLE (PREVENT FALSE NEGATIVES):
   In mission-critical hardware, a False Negative (missing a real Trojan) is catastrophic, permanent, and unpatchable in fabricated silicon. A False Positive merely prompts secondary inspection. If a candidate exhibits concentrated GNN seeds, tightly coupled internal gates, or an asymmetric boundary exit ratio (<= 0.35), err on the side of flagging the anomaly rather than prematurely dismissing it.
2. DO NOT DISMISS COMBINATIONAL TROJANS:
   Trojans do NOT necessarily require sequential flip-flops (DFFs)! Combinational comparator trees (cascaded AND/NAND/NOR/XOR gates monitoring rare bus vectors) have 0 DFFs. If sequential count is 0 but internal density is elevated, this is a classic stealthy combinational Trojan trigger.
3. VERIFY FACTUAL ACCURACY:
   Did the analyst hallucinate or misstate any numerical values (e.g. flip-flop counts, edge density)?
4. STRICT "NEITHER" CRITERION (NEGATIVE CONTROLS ONLY):
   - NEITHER is strictly PROHIBITED if EITHER region contains GNN suspicious seeds (seeds >= 1) with max GNN score >= 0.65 or avg GNN >= 0.35. In that case, you MUST select either REGION_A or REGION_B based on which has stronger anomalous indicators.
   - NEITHER is permissible ONLY on clean negative controls where BOTH Region A and Region B have 0 GNN seeds and peak GNN score < 0.40.
   - A moderate or high exit ratio (e.g. 0.45-0.70) does NOT justify NEITHER if strong GNN seeds are present! Trojan trigger comparators frequently tap multiple payload and bus lines.
5. SYMMETRY CHECK:
   Ensure the assessment is grounded in invariant physical metrics, not positional bias.

REQUIRED AUDIT OUTPUT FORMAT:
VERDICT: <ACCEPT | REJECT | REFINE>
CRITIQUE: <Concise, direct technical critique outlining flaws, benign alternative hypotheses, and factual corrections>
RECOMMENDED_ASSESSMENT: <REGION_A | REGION_B | NEITHER>
"""
    return prompt.strip()


# ============================================================
# 3. Actor Refinement Prompt Construction (Compact & Fast)
# ============================================================

def build_actor_refinement_prompt(
    original_prompt: str,
    actor_initial_response: str,
    critic_audit: str,
    evidence_a: Dict[str, Any] | None = None,
    evidence_b: Dict[str, Any] | None = None,
) -> str:
    """
    Constructs a streamlined revision prompt for the Actor to synthesize the Critic's objections.
    Uses compact factual evidence rather than duplicating the entire multi-thousand-word initial prompt.
    """
    if evidence_a and evidence_b:
        evidence_summary = f"""------------------------------------------------------------
GROUND-TRUTH STRUCTURAL EVIDENCE SUMMARY:
------------------------------------------------------------
REGION A: Size={evidence_a.get('region_size')}, GNN Seeds={evidence_a.get('gnn_seeds_count', 0)}, Max GNN={evidence_a.get('max_gnn_score', 0.0)}, Density={evidence_a.get('internal_edge_density')}, Exits={evidence_a.get('region_exits_count')}, DFFs={evidence_a.get('sequential_gate_count')}
REGION B: Size={evidence_b.get('region_size')}, GNN Seeds={evidence_b.get('gnn_seeds_count', 0)}, Max GNN={evidence_b.get('max_gnn_score', 0.0)}, Density={evidence_b.get('internal_edge_density')}, Exits={evidence_b.get('region_exits_count')}, DFFs={evidence_b.get('sequential_gate_count')}"""
    else:
        # Fallback to truncated original prompt if evidence dicts not passed
        evidence_summary = original_prompt[:1200]

    prompt = f"""You are revising your Hardware Trojan assessment in light of an audit critique.

{evidence_summary}

------------------------------------------------------------
YOUR INITIAL HYPOTHESIS:
------------------------------------------------------------
{actor_initial_response.strip()}

------------------------------------------------------------
SENIOR HARDWARE AUDITOR CRITIQUE:
------------------------------------------------------------
{critic_audit.strip()}

------------------------------------------------------------
REVISION TASK:
------------------------------------------------------------
Carefully review the auditor's critique and factual corrections.
- Guard against False Negatives: Remember that combinational comparator trees (AND/NAND/NOR cascades) operate with 0 DFFs.
- Hard Constraint: If either candidate region exhibits confirmed GNN seeds (seeds >= 1) and elevated GNN score (>= 0.65), you MUST NOT select NEITHER. Select the region with the higher GNN seed concentration and anomalous internal density.
- NEITHER is valid ONLY when BOTH candidate regions have 0 GNN seeds and low GNN scores (< 0.40).
- Do not output UNCERTAIN. Output exactly one of: REGION_A, REGION_B, or NEITHER.

Conclude with the exact required format:
ASSESSMENT: <REGION_A | REGION_B | NEITHER>
CONFIDENCE: <HIGH | MEDIUM | LOW>
JUSTIFICATION: <Final audited justification incorporating the auditor's findings>
"""
    return prompt.strip()


# ============================================================
# 4. Multi-Turn Actor-Critic Coordinator
# ============================================================

def run_actor_critic_loop(
    prompt: str,
    evidence_a: Dict[str, Any],
    evidence_b: Dict[str, Any],
    llm_caller,
    max_turns: int = 1,
) -> Dict[str, Any]:
    """
    Coordinates the multi-turn Actor-Critic verification loop:
    1. Turn 1 (Actor): Generate initial hypothesis.
    2. Deterministic Check: Audit numbers against evidence.
    3. Turn 2 (Critic): Run skeptical audit.
    4. Turn 3 (Actor Revision): Produce final, audited decision.

    Guaranteed not to crash: falls back gracefully to initial response
    if any subsequent stage encounters a network timeout.
    """
    # Turn 1: Actor Initial Hypothesis
    initial_raw = llm_caller(prompt)

    # Deterministic Pre-Audit
    warnings = audit_actor_factual_claims(initial_raw, evidence_a, evidence_b)

    from anonymizer import assert_no_leakage

    # Turn 2: Critic Audit
    critic_prompt = build_critic_audit_prompt(evidence_a, evidence_b, initial_raw, warnings)
    assert_no_leakage(critic_prompt)
    try:
        critic_raw = llm_caller(critic_prompt)
    except Exception as exc:
        # Graceful fallback: return initial response if critic call fails
        return {
            "initial_response": initial_raw,
            "critic_feedback": f"Critic skipped due to offline status ({exc})",
            "final_response": initial_raw,
            "turns_completed": 1,
        }

    # Turn 3: Actor Revision
    refine_prompt = build_actor_refinement_prompt(
        original_prompt=prompt,
        actor_initial_response=initial_raw,
        critic_audit=critic_raw,
        evidence_a=evidence_a,
        evidence_b=evidence_b,
    )
    assert_no_leakage(refine_prompt)
    try:
        final_raw = llm_caller(refine_prompt)
    except Exception as exc:
        final_raw = initial_raw

    return {
        "initial_response": initial_raw,
        "critic_feedback": critic_raw,
        "final_response": final_raw,
        "turns_completed": 3,
        "fact_check_warnings": warnings,
    }


# ============================================================
# 5. Single-Circuit Pipeline Critic Loop
# ============================================================

def _normalize_evidence(ev: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes evidence from build_evidence into a standard flat format."""
    if "structural_evidence" in ev or "region" in ev:
        reg = ev.get("region", {})
        struct = ev.get("structural_evidence", {})
        seeds = ev.get("suspicious_seeds", [])
        return {
            "region_size": reg.get("size", len(ev.get("nodes", []))),
            "gnn_seeds_count": len(seeds),
            "max_gnn_score": max([float(s.get("gnn_score", 0.0)) for s in seeds], default=0.0),
            "avg_gnn_score": (sum([float(s.get("gnn_score", 0.0)) for s in seeds]) / max(1, len(seeds))) if seeds else 0.0,
            "internal_edge_density": struct.get("internal_edge_density", 0.0),
            "internal_edges": struct.get("internal_edges", reg.get("internal_edges", 0)),
            "region_exits_count": len(struct.get("region_exits", [])),
            "exit_ratio": struct.get("exit_ratio", 1.0),
            "sequential_gate_count": len(struct.get("sequential_like_gates", [])),
            "gate_types": reg.get("gate_types", {}),
        }
    return ev


def build_single_circuit_critic_prompt(
    evidence: Dict[str, Any],
    actor_response: str,
    fact_check_warnings: List[str],
) -> str:
    """Constructs a skeptical audit prompt for a single circuit candidate region."""
    norm_ev = _normalize_evidence(evidence)
    warning_block = ""
    if fact_check_warnings:
        warning_block = "AUTOMATED PRE-AUDIT WARNINGS DETECTED:\n" + "\n".join(
            f"- {w}" for w in fact_check_warnings
        ) + "\n\n"

    prompt = f"""You are a Senior ASIC Verification Engineer and Hardware Security Auditor.
Your mission is to RIGOROUSLY AUDIT a junior analyst's single-circuit Hardware Trojan detection report, PREVENT FALSE ALARMS, and ENSURE STRICT FACTUAL GROUNDING.

{warning_block}------------------------------------------------------------
ANONYMIZED STRUCTURAL EVIDENCE OF SUSPICIOUS CANDIDATE REGION:
------------------------------------------------------------
- Region Size: {norm_ev.get('region_size')} gates | GNN Suspicious Seeds: {norm_ev.get('gnn_seeds_count', 0)}
- Max GNN: {norm_ev.get('max_gnn_score', 0.0):.4f} | Avg GNN: {norm_ev.get('avg_gnn_score', 0.0):.4f}
- Internal Edge Density: {norm_ev.get('internal_edge_density')} | Internal Edges: {norm_ev.get('internal_edges')}
- Boundary Exits Count: {norm_ev.get('region_exits_count')} (Exit Ratio: {norm_ev.get('exit_ratio')})
- Sequential DFFs: {norm_ev.get('sequential_gate_count')}
- Gate Types: {json.dumps(norm_ev.get('gate_types', {}))}

------------------------------------------------------------
ANALYST'S PROPOSED REPORT:
------------------------------------------------------------
{actor_response.strip()}

------------------------------------------------------------
CRITIC AUDITING DIRECTIVES:
------------------------------------------------------------
1. VERIFY FACTUAL ACCURACY: Did the analyst hallucinate or misstate any numerical values?
2. BENIGN DESIGN CHECK: Can the flagged subnetwork be legitimately explained as standard functional logic (e.g., standard ALU datapath, counter, carry chain, bus multiplexers, or clock domain synchronizers)?
3. THE "NORMAL" CRITERION: If the candidate region shows typical functional dissipation (high exit ratio > 0.40, lack of tight state counters, or low internal density), challenge whether "NORMAL" is the correct verdict.

REQUIRED AUDIT OUTPUT FORMAT:
VERDICT: <ACCEPT | REJECT | REFINE>
CRITIQUE: <Concise technical critique outlining flaws, benign alternative hypotheses, and factual corrections>
RECOMMENDED_DECISION: <SUSPICIOUS | NORMAL>
"""
    return prompt.strip()


def build_single_circuit_actor_refinement_prompt(
    original_prompt: str,
    actor_initial_response: str,
    critic_audit: str,
    evidence: Dict[str, Any] | None = None,
) -> str:
    """Prompt for Actor to refine single-circuit assessment based on Critic review."""
    if evidence:
        norm_ev = _normalize_evidence(evidence)
        ev_summary = (
            f"Factual Evidence: Region Size={norm_ev.get('region_size')}, "
            f"GNN Seeds={norm_ev.get('gnn_seeds_count')}, Density={norm_ev.get('internal_edge_density')}, "
            f"Exits={norm_ev.get('region_exits_count')}, DFFs={norm_ev.get('sequential_gate_count')}"
        )
    else:
        ev_summary = original_prompt[:800]

    prompt = f"""You are revising your single-circuit Hardware Trojan assessment in light of an auditor critique.

{ev_summary}

------------------------------------------------------------
YOUR INITIAL PROPOSAL:
------------------------------------------------------------
{actor_initial_response.strip()}

------------------------------------------------------------
SENIOR HARDWARE AUDITOR CRITIQUE:
------------------------------------------------------------
{critic_audit.strip()}

------------------------------------------------------------
REVISION TASK:
------------------------------------------------------------
Carefully review the auditor's critique and factual corrections.
If the auditor demonstrated that the flagged logic can be explained by benign datapath functionality, or if the candidate region lacks genuine stealth, revise your decision to NORMAL. Otherwise, if the structural evidence confirms a localized stealthy trigger/payload, maintain SUSPICIOUS.

Conclude with the exact required format:
DECISION: <SUSPICIOUS | NORMAL>
TROJAN_TYPE: <COMBINATIONAL | SEQUENTIAL_COUNTER | FSM | NONE>
CONFIDENCE: <HIGH | MEDIUM | LOW>
REASONING: <Final audited justification incorporating the auditor's findings>
"""
    return prompt.strip()


def run_single_circuit_critic_loop(
    prompt: str,
    evidence: Dict[str, Any],
    llm_caller,
) -> Dict[str, Any]:
    """Runs the Actor-Critic verification loop for a single netlist in pipeline.py."""
    norm_ev = _normalize_evidence(evidence)
    initial_raw = llm_caller(prompt)

    # Pre-audit claims
    warnings = []
    text_lower = initial_raw.lower()
    dff_matches = re.findall(r"(\d+)\s*(?:sequential|flip-flop|dff)", text_lower)
    if dff_matches:
        claimed_dff = int(dff_matches[0])
        actual_dff = norm_ev.get("sequential_gate_count", 0)
        if claimed_dff != actual_dff:
            warnings.append(
                f"[FACT-CHECK]: Claimed {claimed_dff} sequential flip-flops, but ground-truth evidence indicates {actual_dff} DFFs."
            )

    density_matches = re.findall(r"density\s*(?:of|is|:)?\s*([0-9]+\.?[0-9]*)", text_lower)
    if density_matches:
        claimed_density = float(density_matches[0])
        actual_density = float(norm_ev.get("internal_edge_density", 0.0))
        if abs(claimed_density - actual_density) > 0.15:
            warnings.append(
                f"[FACT-CHECK]: Claimed internal edge density of {claimed_density}, but actual is {actual_density}."
            )

    from anonymizer import assert_no_leakage
    critic_prompt = build_single_circuit_critic_prompt(norm_ev, initial_raw, warnings)
    assert_no_leakage(critic_prompt)
    try:
        critic_raw = llm_caller(critic_prompt)
    except Exception as exc:
        return {
            "initial_response": initial_raw,
            "critic_feedback": f"Critic skipped ({exc})",
            "final_response": initial_raw,
            "turns_completed": 1,
            "fact_check_warnings": warnings,
        }

    refine_prompt = build_single_circuit_actor_refinement_prompt(prompt, initial_raw, critic_raw)
    assert_no_leakage(refine_prompt)
    try:
        final_raw = llm_caller(refine_prompt)
    except Exception as exc:
        final_raw = initial_raw

    return {
        "initial_response": initial_raw,
        "critic_feedback": critic_raw,
        "final_response": final_raw,
        "turns_completed": 3,
        "fact_check_warnings": warnings,
    }


