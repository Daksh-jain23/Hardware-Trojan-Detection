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
    density_matches = re.findall(r"density\s*(?:of|is|:)?\s*([0-9]+\.?[0-9]*)", text_lower)
    if density_matches:
        claimed_density = float(density_matches[0])
        actual_density_a = float(evidence_a.get("internal_edge_density", 0.0))
        actual_density_b = float(evidence_b.get("internal_edge_density", 0.0))
        if target_region == "A" and abs(claimed_density - actual_density_a) > 0.15:
            warnings.append(
                f"[FACT-CHECK]: Claimed internal edge density of {claimed_density} for Region A, "
                f"but actual calculated density is {actual_density_a}."
            )
        elif target_region == "B" and abs(claimed_density - actual_density_b) > 0.15:
            warnings.append(
                f"[FACT-CHECK]: Claimed internal edge density of {claimed_density} for Region B, "
                f"but actual calculated density is {actual_density_b}."
            )

    # Check for boundary exit ratio claims
    exit_matches = re.findall(r"exit\s*ratio\s*(?:of|is|:)?\s*([0-9]+\.?[0-9]*)", text_lower)
    if exit_matches:
        claimed_exit = float(exit_matches[0])
        actual_exit_a = float(evidence_a.get("exit_ratio", 1.0))
        actual_exit_b = float(evidence_b.get("exit_ratio", 1.0))
        if target_region == "A" and abs(claimed_exit - actual_exit_a) > 0.15:
            warnings.append(
                f"[FACT-CHECK]: Claimed exit ratio {claimed_exit} for Region A, "
                f"but actual exit ratio is {actual_exit_a}."
            )
        elif target_region == "B" and abs(claimed_exit - actual_exit_b) > 0.15:
            warnings.append(
                f"[FACT-CHECK]: Claimed exit ratio {claimed_exit} for Region B, "
                f"but actual exit ratio is {actual_exit_b}."
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
1. VERIFY FACTUAL ACCURACY: Did the analyst hallucinate or misstate any numerical values (e.g., flip-flop counts, edge density)?
2. BENIGN DESIGN CHECK: Can the flagged subnetwork be legitimately explained as standard functional logic (e.g., standard ALU datapath, carry chain, bus multiplexers, or clock domain synchronizers)?
3. THE "NEITHER" CRITERION: If both candidate regions show typical functional dissipation (high exit ratios > 0.40, lack of tight state counters, or low internal density), challenge whether "NEITHER" is the correct verdict.
4. SYMMETRY CHECK: Ensure the analyst is not biased simply because Region A was presented first.

REQUIRED AUDIT OUTPUT FORMAT:
VERDICT: <ACCEPT | REJECT | REFINE>
CRITIQUE: <Concise, direct technical critique outlining flaws, benign alternative hypotheses, and factual corrections>
RECOMMENDED_ASSESSMENT: <REGION_A | REGION_B | NEITHER>
"""
    return prompt.strip()


# ============================================================
# 3. Actor Refinement Prompt Construction
# ============================================================

def build_actor_refinement_prompt(
    original_prompt: str,
    actor_initial_response: str,
    critic_audit: str,
) -> str:
    """
    Constructs the revision prompt for the Actor to synthesize the Critic's objections.
    """
    prompt = f"""{original_prompt}

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
Carefully review the auditor's critique and factual corrections.
If the auditor showed that the logic can be explained by benign datapath functionality, or if both candidate regions lack genuine stealth, update your assessment to NEITHER or the appropriate region.

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
    refine_prompt = build_actor_refinement_prompt(prompt, initial_raw, critic_raw)
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
) -> str:
    """Prompt for Actor to refine single-circuit assessment based on Critic review."""
    prompt = f"""{original_prompt.strip()}

============================================================
MULTI-TURN VERIFICATION AUDIT REVIEW
============================================================
Your initial proposed report was audited by a Senior Hardware Verification Engineer.

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
Carefully review the auditor's critique and factual corrections.
If the auditor demonstrated that the flagged logic can be explained by benign datapath functionality, or if the candidate region lacks genuine stealth, revise your decision to NORMAL. Otherwise, if the structural evidence confirms a localized stealthy trigger/payload, maintain SUSPICIOUS.

Conclude with the exact required format:
DECISION: <SUSPICIOUS | NORMAL>
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


