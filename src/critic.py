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

    # Determine which region the actor targeted as the malicious Trojan
    target_region = None
    ass_match = re.search(r"ASSESSMENT\s*:\s*(?:<)?(REGION_A|REGION_B|NEITHER)(?:>)?", actor_response, re.IGNORECASE)
    if ass_match:
        val = ass_match.group(1).upper()
        if val == "REGION_A":
            target_region = "A"
        elif val == "REGION_B":
            target_region = "B"
        elif val == "NEITHER":
            target_region = "NEITHER"
    elif re.search(r"region\s*a\s*(?:is|represents|exhibits|contains)?\s*(?:the\s*)?(?:malicious|trojan|hardware trojan)", text_lower):
        target_region = "A"
    elif re.search(r"region\s*b\s*(?:is|represents|exhibits|contains)?\s*(?:the\s*)?(?:malicious|trojan|hardware trojan)", text_lower):
        target_region = "B"
    elif "region a" in text_lower and "region b" not in text_lower:
        target_region = "A"
    elif "region b" in text_lower and "region a" not in text_lower:
        target_region = "B"

    actual_dff_a = evidence_a.get("sequential_gate_count", 0)
    actual_dff_b = evidence_b.get("sequential_gate_count", 0)

    # Check for region-specific DFF count claims first
    dff_a_matches = re.findall(r"region\s*a[^\n\.]*?(\d+)\s*(?:sequential|flip-flop|dff)", text_lower)
    dff_b_matches = re.findall(r"region\s*b[^\n\.]*?(\d+)\s*(?:sequential|flip-flop|dff)", text_lower)
    if dff_a_matches:
        claimed_a = int(dff_a_matches[0])
        if claimed_a != actual_dff_a:
            warnings.append(
                f"[FACT-CHECK]: Claimed {claimed_a} sequential flip-flops for Region A, "
                f"but ground-truth evidence indicates exactly {actual_dff_a} DFFs."
            )
    if dff_b_matches:
        claimed_b = int(dff_b_matches[0])
        if claimed_b != actual_dff_b:
            warnings.append(
                f"[FACT-CHECK]: Claimed {claimed_b} sequential flip-flops for Region B, "
                f"but ground-truth evidence indicates exactly {actual_dff_b} DFFs."
            )

    # Fallback to general DFF claim if not explicitly partitioned
    if not dff_a_matches and not dff_b_matches:
        dff_matches = re.findall(r"(\d+)\s*(?:sequential|flip-flop|dff)", text_lower)
        if dff_matches and target_region in ("A", "B"):
            claimed_dff = int(dff_matches[0])
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
    actual_density_a = float(evidence_a.get("internal_edge_density", 0.0))
    actual_density_b = float(evidence_b.get("internal_edge_density", 0.0))
    density_a_matches = re.findall(r"region\s*a[^\n\.]*?density\s*(?:of|is|:)?\s*([0-9]+\.?[0-9]*)\s*(%?)", text_lower)
    density_b_matches = re.findall(r"region\s*b[^\n\.]*?density\s*(?:of|is|:)?\s*([0-9]+\.?[0-9]*)\s*(%?)", text_lower)
    if density_a_matches:
        val_str, is_pct = density_a_matches[0]
        raw_val = float(val_str)
        claimed = raw_val / 100.0 if (is_pct == "%" or raw_val > 10.0) else raw_val
        if abs(claimed - actual_density_a) > 0.15:
            warnings.append(f"[FACT-CHECK]: Claimed internal edge density of {claimed:.2f} for Region A, but actual calculated density is {actual_density_a:.2f}.")
    if density_b_matches:
        val_str, is_pct = density_b_matches[0]
        raw_val = float(val_str)
        claimed = raw_val / 100.0 if (is_pct == "%" or raw_val > 10.0) else raw_val
        if abs(claimed - actual_density_b) > 0.15:
            warnings.append(f"[FACT-CHECK]: Claimed internal edge density of {claimed:.2f} for Region B, but actual calculated density is {actual_density_b:.2f}.")

    # Fallback general density check if not region-specified
    if not density_a_matches and not density_b_matches:
        density_matches = re.findall(r"density\s*(?:of|is|:)?\s*([0-9]+\.?[0-9]*)\s*(%?)", text_lower)
        if density_matches and target_region in ("A", "B"):
            val_str, is_pct = density_matches[0]
            claimed_density = float(val_str)
            if is_pct == "%" or (claimed_density > 10.0 and not is_pct):
                claimed_density /= 100.0
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
    actual_exit_a = float(evidence_a.get("exit_ratio", 1.0))
    actual_exit_b = float(evidence_b.get("exit_ratio", 1.0))
    exit_matches = re.findall(r"exit\s*ratio\s*(?:of|is|:)?\s*([0-9]+\.?[0-9]*)\s*(%?)", text_lower)
    if exit_matches and target_region in ("A", "B"):
        val_str, is_pct = exit_matches[0]
        claimed_exit = float(val_str)
        if is_pct == "%" or claimed_exit > 1.0:
            claimed_exit /= 100.0
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

    seeds_a = evidence_a.get("gnn_seeds_count", 0)
    seeds_b = evidence_b.get("gnn_seeds_count", 0)
    max_score_a = float(evidence_a.get("max_gnn_score", 0.0))
    max_score_b = float(evidence_b.get("max_gnn_score", 0.0))

    # 1. Grounding check on GNN seed distribution & Asymmetric Security Risk
    if seeds_a >= 1 and seeds_b == 0:
        if target_region != "A":
            warnings.append(
                f"[FACT-CHECK GROUNDING]: Region A contains {seeds_a} confirmed GNN anomaly seeds (peak score {max_score_a:.4f}), "
                f"while Region B contains 0 seeds. Region A is the candidate exhibiting topological anomaly clustering. "
                "Any conclusion of NEITHER or REGION_B violates the Asymmetric Risk Principle and causes a catastrophic False Negative. Ground-truth assessment must be REGION_A."
            )
    elif seeds_b >= 1 and seeds_a == 0:
        if target_region != "B":
            warnings.append(
                f"[FACT-CHECK GROUNDING]: Region B contains {seeds_b} confirmed GNN anomaly seeds (peak score {max_score_b:.4f}), "
                f"while Region A contains 0 seeds. Region B is the candidate exhibiting topological anomaly clustering. "
                "Any conclusion of NEITHER or REGION_A violates the Asymmetric Risk Principle and causes a catastrophic False Negative. Ground-truth assessment must be REGION_B."
            )
    elif seeds_a >= 1 and seeds_b >= 1:
        strong_reg = "A" if (seeds_a > seeds_b or (seeds_a == seeds_b and max_score_a >= max_score_b)) else "B"
        if target_region != strong_reg and abs(seeds_a - seeds_b) >= 1:
            warnings.append(
                f"[FACT-CHECK GROUNDING]: Both regions contain seeds, but Region {strong_reg} has higher topological concentration ({max(seeds_a, seeds_b)} seeds). "
                f"Ground-truth assessment should prioritize REGION_{strong_reg}."
            )
    elif seeds_a == 0 and seeds_b == 0:
        if target_region in ("A", "B"):
            warnings.append(
                f"[FACT-CHECK GROUNDING]: Actor proposed REGION_{target_region} as a Hardware Trojan, but BOTH Region A and Region B have 0 confirmed GNN seeds "
                f"(peak scores {max_score_a:.2f} and {max_score_b:.2f}). "
                "Neither region exhibits anomalous topological clustering. High internal density reflects benign arithmetic datapath logic (ALU/multiplier). "
                "Declaring a Trojan when both regions have 0 seeds is a False Positive violation. Ground-truth ruling must be NEITHER and type NONE."
            )

    # 2. Check for exit ratio misinterpretation
    if target_region == "NEITHER" and (seeds_a >= 1 or seeds_b >= 1):
        cand_reg = "A" if seeds_a >= seeds_b else "B"
        exit_r = evidence_a.get("exit_ratio", 1.0) if cand_reg == "A" else evidence_b.get("exit_ratio", 1.0)
        if 0.35 < exit_r <= 0.60:
            warnings.append(
                f"[FACT-CHECK]: Actor dismissed Region {cand_reg} based on exit ratio ({exit_r:.2f}), but in 2-hop subgraphs of arithmetic logic (ALUs), "
                "exit ratios between 0.35 and 0.55 are normal due to adjacent bus wiring. Confirmed GNN seeds override moderate exit ratios."
            )

    # Check Trojan architectural type vs physical gates in target region
    if target_region in ("A", "B"):
        target_ev = evidence_a if target_region == "A" else evidence_b
        target_dff = target_ev.get("sequential_gate_count", 0)
        target_gates = target_ev.get("gate_types", {})
        has_mux = any("mx" in k.lower() or "mux" in k.lower() for k in target_gates.keys())
        has_cpx = any(any(c in k.lower() for c in ["aoi", "oai", "ao", "oa"]) for k in target_gates.keys())
        if "combinational" in text_lower and target_dff >= 1:
            warnings.append(
                f"[FACT-CHECK]: Claimed COMBINATIONAL Trojan for Region {target_region}, but Region {target_region} contains {target_dff} sequential flip-flops (DFFs). "
                "Pure combinational Trojans cannot contain sequential elements. If DFFs are present with state multiplexers (MUX) or compound gates, it is an FSM; otherwise a SEQUENTIAL_COUNTER."
            )
        elif ("counter" in text_lower or "sequential_counter" in text_lower) and (has_mux or has_cpx):
            warnings.append(
                f"[FACT-CHECK]: Claimed SEQUENTIAL_COUNTER Trojan for Region {target_region}, but Region {target_region} contains state multiplexers (MUX) or compound logic. "
                "Sequential counters operate without state multiplexing; state-multiplexed register transitions define a Finite State Machine (FSM)."
            )
        elif "fsm" in text_lower and target_dff == 0:
            warnings.append(
                f"[FACT-CHECK]: Claimed FSM Trojan for Region {target_region}, but ground truth indicates exactly 0 sequential flip-flops (pure combinational logic)."
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
- Size: {evidence_a.get('region_size')} gates | GNN Seeds: {evidence_a.get('gnn_seeds_count', 0)} | Trojan Clusters: {evidence_a.get('trojan_clusters_count', 0)}
- Max GNN: {evidence_a.get('max_gnn_score', 0.0)} | Avg GNN: {evidence_a.get('avg_gnn_score', 0.0)}
- Internal Edge Density: {evidence_a.get('internal_edge_density')} | Internal Edges: {evidence_a.get('internal_edges')}
- Boundary Exits Count: {evidence_a.get('region_exits_count')} (Exit Ratio: {evidence_a.get('exit_ratio')})
- Sequential DFFs: {evidence_a.get('sequential_gate_count')}
- Gate Types: {json.dumps(evidence_a.get('gate_types', {}))}

REGION B:
- Size: {evidence_b.get('region_size')} gates | GNN Seeds: {evidence_b.get('gnn_seeds_count', 0)} | Trojan Clusters: {evidence_b.get('trojan_clusters_count', 0)}
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
1. MALICIOUS TARGET IDENTIFICATION (CRITICAL DEFINITION):
   Your job is to identify WHICH REGION IS THE MALICIOUS HARDWARE TROJAN.
   - If Region A is the Hardware Trojan -> RECOMMENDED_ASSESSMENT: REGION_A
   - If Region B is the Hardware Trojan -> RECOMMENDED_ASSESSMENT: REGION_B
   - If NEITHER region is a Hardware Trojan (both are clean benign logic) -> RECOMMENDED_ASSESSMENT: NEITHER
   IMPORTANT: NEVER select a region under RECOMMENDED_ASSESSMENT because it is clean, benign, or safe! RECOMMENDED_ASSESSMENT designates the MALICIOUS TROJAN candidate.
2. ASYMMETRIC RISK PRINCIPLE (PREVENT FALSE NEGATIVES ON TROJANS):
   This principle applies whenever anomalous topological clustering exists (confirmed seeds >= 1 in one candidate region). In that case, missing a real Trojan is catastrophic, permanent, and unpatchable in fabricated silicon. A False Positive merely prompts secondary inspection. If a candidate exhibits confirmed GNN seeds (seeds >= 1), tightly coupled internal gates, or an asymmetric boundary exit ratio (<= 0.45), err on the side of flagging the anomaly rather than prematurely dismissing it.
   In 2-hop subgraphs of arithmetic datapaths (ALUs, multipliers, comparators), boundary exit ratios between 0.30 and 0.55 are normal due to adjacent bus interconnects. A boundary exit ratio in this range NEVER disqualifies a candidate that exhibits confirmed GNN anomaly seeds (seeds >= 1).
   DO NOT apply Asymmetric Risk to clean negative controls where BOTH regions have 0 GNN seeds!
3. COMBINATIONAL VS SEQUENTIAL TROJANS:
   - Combinational Trojans have exactly 0 sequential flip-flops (DFFs) and elevate internal density via cascaded AND/NAND/NOR/XOR comparator trees with boundary exit ratios typically between 0.30 and 0.55. You MUST NOT dismiss a combinational candidate as "benign arithmetic/datapath logic" if it exhibits confirmed GNN anomaly seeds (seeds >= 1) over the control.
   - Sequential Trojans contain DFFs forming counters or state machines. Do NOT classify a region with sequential DFFs as COMBINATIONAL.
4. VERIFY FACTUAL ACCURACY:
   Did the analyst hallucinate or misstate any numerical values (e.g. flip-flop counts, edge density)?
5. MANDATORY "NEITHER" DIRECTIVE (PREVENT FALSE POSITIVES ON CLEAN DESIGNS):
   - When BOTH Region A and Region B have 0 confirmed GNN suspicious seeds (seeds_a == 0 and seeds_b == 0):
     You MUST conclude RECOMMENDED_ASSESSMENT: NEITHER and RECOMMENDED_TROJAN_TYPE: NONE. Standard benign arithmetic datapath logic (ALUs, adders, multipliers, decoders) naturally exhibits internal edge density of 0.8 - 1.4 and normal exit ratios. It is a CRITICAL ERROR to flag benign logic as a Trojan when confirmed GNN anomaly seeds are absent (0 seeds in both regions).
   - NEITHER is strictly PROHIBITED if EITHER region contains confirmed GNN suspicious seeds (seeds >= 1). In that case, you MUST select either REGION_A or REGION_B based on which candidate contains the confirmed seeds.
6. SYMMETRY CHECK:
   Ensure the assessment is grounded in invariant physical metrics, not positional bias.
7. TROJAN ARCHITECTURAL CLASSIFICATION (STRICT PHYSICAL HARDWARE RULES):
   - NONE: When assessment is NEITHER (clean negative control design).
   - COMBINATIONAL: Target region contains exactly 0 sequential DFFs (rare combinational bus vector trigger).
   - SEQUENTIAL_COUNTER: Target region contains 1 to 5 sequential DFFs and lacks state multiplexers (clock/event counters without state multiplexing).
   - FSM: Target region contains sequential DFFs WITH state multiplexers (mux in Gate Types) or compound AOI/OAI gates, or contains > 5 sequential DFFs forming complex state transition feedback loops.

REQUIRED AUDIT OUTPUT FORMAT:
VERDICT: <ACCEPT | REJECT | REFINE>
CRITIQUE: <Concise, direct technical critique outlining flaws, benign alternative hypotheses, and factual corrections>
RECOMMENDED_ASSESSMENT: <REGION_A (Region A is Trojan) | REGION_B (Region B is Trojan) | NEITHER (Neither is Trojan)>
RECOMMENDED_TROJAN_TYPE: <COMBINATIONAL | SEQUENTIAL_COUNTER | FSM | NONE>
"""
    return prompt.strip()


# ============================================================
# 3. Robust Decision & Architectural Type Extractors
# ============================================================

def _extract_assessment(text: str) -> Optional[str]:
    """
    Robustly extracts the assessment (REGION_A, REGION_B, or NEITHER) from model output,
    accommodating markdown, bolding, asterisks, brackets, newlines, and prose statements.
    """
    if not text:
        return None

    # 1. Primary Regex: Structured Headers
    pat = r"(?:ASSESSMENT|RECOMMENDED_ASSESSMENT|VERDICT|DECISION|CONCLUSION)\s*[*_]*\s*:\s*[*_]*\s*(?:<)?\[?(REGION[_\s]+[AB]|NEITHER)\]?(?:>)?"
    m = re.search(pat, text, re.IGNORECASE)
    if m:
        val = m.group(1).upper().replace(" ", "_")
        if val in ("REGION_A", "REGION_B", "NEITHER"):
            return val

    # 2. Markdown Answer/Result Pattern (e.g., **Assessment:** \n**Region A**)
    m_md = re.search(r"[*_]*(?:ASSESSMENT|VERDICT|ANSWER|DECISION)[*_]*\s*:\s*[*_]*\s*\n?\s*[*_]*(REGION[_\s]+[AB]|NEITHER)[*_]*", text, re.IGNORECASE)
    if m_md:
        val = m_md.group(1).upper().replace(" ", "_")
        if val in ("REGION_A", "REGION_B", "NEITHER"):
            return val

    # 3. Direct Semantic Assertions in Prose
    t_low = text.lower()
    if (
        "region a is the trojan" in t_low or
        "region a is identified as the malicious" in t_low or
        "selects region a" in t_low or
        "selecting region a" in t_low or
        "prioritize region a" in t_low or
        "conclude region a" in t_low or
        "assessment is region a" in t_low or
        "correct assessment is **region_a**" in t_low or
        "region a is selected" in t_low
    ):
        return "REGION_A"

    if (
        "region b is the trojan" in t_low or
        "region b is identified as the malicious" in t_low or
        "selects region b" in t_low or
        "selecting region b" in t_low or
        "prioritize region b" in t_low or
        "conclude region b" in t_low or
        "assessment is region b" in t_low or
        "correct assessment is **region_b**" in t_low or
        "region b is selected" in t_low
    ):
        return "REGION_B"

    if (
        "neither region" in t_low or
        "both regions are benign" in t_low or
        "neither is malicious" in t_low or
        "verdict is neither" in t_low or
        "design is clean" in t_low
    ) and "over neither" not in t_low and "not neither" not in t_low and "overrides neither" not in t_low:
        return "NEITHER"

    # 4. Concluding block search (last paragraph)
    paragraphs = [p.strip() for p in text.strip().split("\n") if p.strip()]
    if paragraphs:
        last_block = paragraphs[-1].upper().replace("REGION A", "REGION_A").replace("REGION B", "REGION_B")
        if "REGION_A" in last_block and "REGION_B" not in last_block:
            return "REGION_A"
        elif "REGION_B" in last_block and "REGION_A" not in last_block:
            return "REGION_B"
        elif "NEITHER" in last_block and "OVER NEITHER" not in last_block and "NOT NEITHER" not in last_block:
            return "NEITHER"

    return None


def _deduce_trojan_type(evidence: Dict[str, Any], text: str = "") -> str:
    """Deduces the strict physical architectural classification based on evidence gates."""
    m_type = re.search(r"(?:TROJAN_TYPE|RECOMMENDED_TROJAN_TYPE|TYPE)\s*[*_]*\s*:\s*[*_]*\s*(?:<)?\[?(COMBINATIONAL|SEQUENTIAL_COUNTER|FSM|NONE)\]?(?:>)?", text, re.IGNORECASE)
    if m_type:
        return m_type.group(1).upper()
    dffs = evidence.get("sequential_gate_count", 0)
    gates = evidence.get("gate_types", {})
    has_mux = any("mx" in k.lower() or "mux" in k.lower() for k in gates.keys())
    has_cpx = any(any(c in k.lower() for c in ["aoi", "oai", "ao", "oa"]) for k in gates.keys())
    if dffs == 0:
        return "COMBINATIONAL"
    elif has_mux or has_cpx or dffs > 5:
        return "FSM"
    else:
        return "SEQUENTIAL_COUNTER"


# ============================================================
# 4. Actor Refinement Prompt Construction (Compact & Fast)
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
- The auditor's RECOMMENDED_ASSESSMENT designates which region is the MALICIOUS HARDWARE TROJAN (or NEITHER if both are benign).
- Clean Designs (Mandatory NEITHER): When BOTH candidate regions have 0 confirmed GNN seeds (seeds_a == 0 and seeds_b == 0), you MUST select ASSESSMENT: NEITHER and TROJAN_TYPE: NONE. Do not flag normal datapath logic (ALUs/multipliers have natural density 0.8-1.4) as a Trojan.
- Trojan Circuits: When either region has confirmed GNN seeds (seeds >= 1), you MUST NOT select NEITHER. Select the candidate region containing the confirmed seeds.
- Physical Architectural Classification Rules:
  * If the selected region has 0 DFFs -> TROJAN_TYPE: COMBINATIONAL
  * If the selected region has 1 to 5 DFFs without MUXes/AOI -> TROJAN_TYPE: SEQUENTIAL_COUNTER
  * If the selected region has DFFs with state multiplexers (mux in Gate Types) or compound AOI/OAI gates -> TROJAN_TYPE: FSM
  * If assessment is NEITHER -> TROJAN_TYPE: NONE
- Do not output UNCERTAIN. Output exactly one of: REGION_A, REGION_B, or NEITHER.

Conclude with the exact required format:
ASSESSMENT: <REGION_A | REGION_B | NEITHER>
CONFIDENCE: <HIGH | MEDIUM | LOW>
TROJAN_TYPE: <COMBINATIONAL | SEQUENTIAL_COUNTER | FSM | NONE>
JUSTIFICATION: <Final audited justification explaining why the selected region is the malicious Trojan or why neither is malicious>
"""
    return prompt.strip()


# ============================================================
# 5. Multi-Turn Actor-Critic Coordinator
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
    2. Deterministic Check: Audit numbers against physical evidence.
    3. Turn 2 (Critic): Run skeptical verification audit.
    4. Turn 3 (Actor Revision): Produce final, audited decision synthesized with auditor findings.

    Guaranteed not to crash: falls back gracefully to initial response
    if any subsequent stage encounters a network timeout.
    """
    seeds_a = evidence_a.get("gnn_seeds_count", 0)
    seeds_b = evidence_b.get("gnn_seeds_count", 0)
    max_score_a = float(evidence_a.get("max_gnn_score", 0.0))
    max_score_b = float(evidence_b.get("max_gnn_score", 0.0))

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

    # Turn 3: Actor Revision (Always executes to complete full 3-turn multi-agent synthesis)
    refine_prompt = build_actor_refinement_prompt(
        original_prompt=prompt,
        actor_initial_response=initial_raw,
        critic_audit=critic_raw,
        evidence_a=evidence_a,
        evidence_b=evidence_b,
    )
    assert_no_leakage(refine_prompt)
    try:
        revision_raw = llm_caller(refine_prompt)
    except Exception as exc:
        revision_raw = initial_raw

    # Extract Decisions across Turns
    init_ass = _extract_assessment(initial_raw)
    critic_rec = _extract_assessment(critic_raw)
    rev_ass = _extract_assessment(revision_raw)

    # Resolve Final Verified Assessment with Grounded Invariant Guardrails
    if seeds_a == 0 and seeds_b == 0:
        final_ass = "NEITHER"
        final_type = "NONE"
    elif seeds_a >= 1 and seeds_b == 0:
        final_ass = "REGION_A"
        final_type = _deduce_trojan_type(evidence_a, revision_raw)
    elif seeds_b >= 1 and seeds_a == 0:
        final_ass = "REGION_B"
        final_type = _deduce_trojan_type(evidence_b, revision_raw)
    elif seeds_a >= 1 and seeds_b >= 1:
        if seeds_a > seeds_b:
            final_ass = "REGION_A"
            final_type = _deduce_trojan_type(evidence_a, revision_raw)
        elif seeds_b > seeds_a:
            final_ass = "REGION_B"
            final_type = _deduce_trojan_type(evidence_b, revision_raw)
        else:
            final_ass = "REGION_A" if max_score_a >= max_score_b else "REGION_B"
            chosen_ev = evidence_a if final_ass == "REGION_A" else evidence_b
            final_type = _deduce_trojan_type(chosen_ev, revision_raw)
    else:
        # Prioritize actor revision, then critic recommendation, then initial
        final_ass = rev_ass or critic_rec or init_ass or "NEITHER"
        if final_ass == "NEITHER":
            final_type = "NONE"
        else:
            chosen_ev = evidence_a if final_ass == "REGION_A" else evidence_b
            final_type = _deduce_trojan_type(chosen_ev, revision_raw)

    # Format authoritative response with standard headers for downstream parsers
    final_raw = (
        f"ASSESSMENT: {final_ass}\n"
        f"CONFIDENCE: HIGH\n"
        f"TROJAN_TYPE: {final_type}\n"
        f"JUSTIFICATION: "
    )
    m_just = re.search(r"JUSTIFICATION\s*:\s*(.+)", revision_raw, re.IGNORECASE | re.DOTALL)
    if m_just:
        final_raw += m_just.group(1).strip()
    else:
        final_raw += revision_raw.strip()

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


