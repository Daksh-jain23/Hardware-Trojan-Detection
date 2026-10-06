"""
LLM prompt builder for Hardware Trojan detection.

Pipeline:
    evidence.json (or evidence_anonymized.json)
        ↓
    Heuristic Feature Extraction & Attribution (src/heuristic.py)
        ↓
    Region Refinement Metrics (src/region.py)
        ↓
    Deterministic numerical extraction & contradiction formatting
        ↓
    Strict reasoning prompt (Hybrid or Baseline mode)
        ↓
    Downstream LLM (Gemini / Ollama / Qwen)

Modes:
- "hybrid" (Phase 4, default):
    Integrates GNN probabilistic facts, Heuristic layer composite score and
    factor attributions, Refined region compression metrics, Contradiction
    Analysis guidance (arbitration when GNN and Heuristic disagree), and a
    strict structured JSON output schema.
- "baseline" (Experiment 2):
    Preserves pure GNN evidence presentation without heuristic or refinement
    facts, guaranteeing an unaltered baseline for ablation studies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup path resolution for modular imports
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

for p in [str(ROOT), str(SRC)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from src.heuristic import (
        DEFAULT_WEIGHTS,
        DEFAULT_HEURISTIC_THRESHOLD,
        load_optimized_weights,
        extract_heuristic_features,
        calculate_heuristic_score,
        classify_heuristic,
        explain_heuristic_decision,
        rank_suspicious_nodes,
    )
except ImportError:
    from heuristic import (
        DEFAULT_WEIGHTS,
        DEFAULT_HEURISTIC_THRESHOLD,
        load_optimized_weights,
        extract_heuristic_features,
        calculate_heuristic_score,
        classify_heuristic,
        explain_heuristic_decision,
        rank_suspicious_nodes,
    )


# ============================================================
# Configuration
# ============================================================

DEFAULT_OUTPUT_DIR = ROOT / "results" / "llm"

MAX_REGION_NODES = 20
MAX_REGION_EXITS = 15
MAX_SEQUENTIAL_GATES = 15
MAX_RANKED_NODES = 10


# ============================================================
# Helpers
# ============================================================

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def compact_seed(node: dict, nodes_by_gate: Optional[Dict[str, dict]] = None) -> dict:
    """
    Compact representation of an actual GNN suspicious seed.

    Populates missing fanin and fanout from matching `nodes` entries or omits them
    instead of defaulting to 0, ensuring prompts do not present fabricated connectivity
    values as authoritative.
    """
    gate_name = node.get("gate")
    matching_node = (nodes_by_gate.get(gate_name) or {}) if (nodes_by_gate and gate_name) else {}

    result: Dict[str, Any] = {
        "type": node.get("type", matching_node.get("type")),
        "gnn_score": round(safe_float(node.get("gnn_score", matching_node.get("gnn_score"))), 6),
    }

    raw_fanin = node.get("fanin")
    if raw_fanin is None:
        raw_fanin = matching_node.get("fanin")
    if raw_fanin is not None:
        result["fanin"] = int(safe_float(raw_fanin))

    raw_fanout = node.get("fanout")
    if raw_fanout is None:
        raw_fanout = matching_node.get("fanout")
    if raw_fanout is not None:
        result["fanout"] = int(safe_float(raw_fanout))

    return result


def compact_ranked_node(node: dict, rank: int) -> dict:
    """
    Compact representation of a node prioritized by the heuristic layer.
    Combines GNN score with structural indicators (sequential state, connectivity, output proximity).
    """
    return {
        "priority_rank": rank,
        "type": node.get("type"),
        "gnn_score": round(safe_float(node.get("gnn_score")), 4),
        "is_sequential": bool(node.get("is_sequential", False)),
        "fanin": int(safe_float(node.get("fanin"), 0)),
        "fanout": int(safe_float(node.get("fanout"), 0)),
        "distance_to_output": round(safe_float(node.get("po_distance", 999.0)), 2),
        "composite_priority": round(safe_float(node.get("composite_priority")), 4),
    }


def compact_region_node(node: dict) -> dict:
    """
    Compact representation of a representative expanded-region node.
    Node identifiers are omitted in prompts to strictly enforce anonymized reasoning.
    """
    result: Dict[str, Any] = {
        "type": node.get("type"),
        "gnn_score": round(safe_float(node.get("gnn_score")), 6),
        "fanin": int(safe_float(node.get("fanin"), 0)),
        "fanout": int(safe_float(node.get("fanout"), 0)),
    }

    if "depth_from_input" in node:
        result["depth"] = node["depth_from_input"]

    if "distance_to_output" in node:
        result["output_distance"] = node["distance_to_output"]

    if node.get("primary_input"):
        result["primary_input"] = True

    if node.get("primary_output"):
        result["primary_output"] = True

    if node.get("region_exit"):
        result["region_exit"] = True

    return result


def compact_graph(graph: dict) -> dict:
    """Keep only aggregate graph statistics."""
    return {
        "nodes": graph.get("nodes", graph.get("total_nodes", 0)),
        "edges": graph.get("edges", graph.get("total_edges", 0)),
    }


def deterministic_gnn_facts(gnn: dict, seeds: list[dict]) -> dict:
    """
    Compute numerical GNN facts deterministically in Python so the LLM
    never has to count or infer threshold statistics itself.
    """
    scores = [
        safe_float(seed.get("gnn_score"))
        for seed in seeds
        if seed.get("gnn_score") is not None
    ]

    threshold = safe_float(gnn.get("threshold"), 0.95)

    facts = {
        "threshold": threshold,
        "suspicious_seed_count": len(seeds),
        "seed_score_max": round(max(scores), 6) if scores else None,
        "seed_score_min": round(min(scores), 6) if scores else None,
        "seed_score_mean": round(sum(scores) / len(scores), 6) if scores else None,
        "seed_count_at_or_above_threshold": sum(score >= threshold for score in scores),
        "seed_count_at_or_above_0_99": sum(score >= 0.99 for score in scores),
    }

    if "max_score" in gnn:
        facts["graph_score_max"] = gnn["max_score"]
    elif "suspicion" in gnn and "max" in gnn["suspicion"]:
        facts["graph_score_max"] = gnn["suspicion"]["max"]

    if "mean_score" in gnn:
        facts["graph_score_mean"] = gnn["mean_score"]
    elif "suspicion" in gnn and "mean" in gnn["suspicion"]:
        facts["graph_score_mean"] = gnn["suspicion"]["mean"]

    if "median_score" in gnn:
        facts["graph_score_median"] = gnn["median_score"]
    elif "suspicion" in gnn and "median" in gnn["suspicion"]:
        facts["graph_score_median"] = gnn["suspicion"]["median"]

    if "min_score" in gnn:
        facts["graph_score_min"] = gnn["min_score"]
    elif "suspicion" in gnn and "min" in gnn["suspicion"]:
        facts["graph_score_min"] = gnn["suspicion"]["min"]

    return facts


def deterministic_heuristic_facts(
    evidence: dict,
    weights: Optional[Dict[str, float]] = None,
    heuristic_threshold: Optional[float] = None,
) -> dict:
    """
    Compute authoritative heuristic facts, composite score, and factor attributions.
    """
    if weights is None or heuristic_threshold is None:
        loaded_weights, loaded_threshold = load_optimized_weights()
        if weights is None:
            weights = loaded_weights
        if heuristic_threshold is None:
            heuristic_threshold = loaded_threshold

    features = extract_heuristic_features(evidence)
    score = calculate_heuristic_score(features, weights)
    decision = classify_heuristic(score, threshold=heuristic_threshold)
    attributions = explain_heuristic_decision(features, weights, top_n=5)

    return {
        "composite_heuristic_score": round(score, 6),
        "optimal_heuristic_threshold": round(heuristic_threshold, 6),
        "heuristic_decision": decision,
        "margin_to_threshold": round(score - heuristic_threshold, 6),
        "key_structural_metrics": {
            "max_gnn_score": round(features.get("max_gnn_score", 0.0), 6),
            "mean_gnn_score": round(features.get("mean_gnn_score", 0.0), 6),
            "high_confidence_ratio": round(features.get("high_confidence_ratio", 0.0), 6),
            "confidence_margin": round(features.get("confidence_margin", 0.0), 6),
            "connectivity_ratio": round(features.get("connectivity", 0.0), 6),
            "sequential_ratio": round(features.get("sequential_ratio", 0.0), 6),
            "exit_ratio": round(features.get("exit_ratio", 0.0), 6),
            "structural_density": round(features.get("structural_density", 0.0), 6),
            "po_proximity": round(features.get("po_proximity", 0.0), 6),
            "trigger_concentration": round(features.get("trigger_concentration", 0.0), 6),
        },
        "top_contributing_factors": attributions,
    }


def deterministic_refinement_facts(
    evidence: dict,
    refined_region: Any = None,
) -> Optional[dict]:
    """
    Extract or format region refinement metrics (compression ratio, pruned leaves, anchor preservation).
    """
    if refined_region is not None:
        if hasattr(refined_region, "nodes") and hasattr(refined_region, "pruned_nodes"):
            orig_size = len(refined_region.nodes) + len(refined_region.pruned_nodes)
            ref_size = len(refined_region.nodes)
            pruned_count = len(refined_region.pruned_nodes)
            retention = getattr(
                refined_region,
                "retention_ratio",
                (ref_size / orig_size if orig_size else 1.0),
            )
            return {
                "original_region_size": orig_size,
                "refined_region_size": ref_size,
                "pruned_peripheral_leaves": pruned_count,
                "retention_ratio": round(retention, 4),
                "noise_reduction_ratio": round(1.0 - retention, 4),
                "core_anchors_preserved": True,
                "sequential_anchors_preserved": True,
            }
        elif isinstance(refined_region, dict):
            return refined_region

    if "refined_region" in evidence and isinstance(evidence["refined_region"], dict):
        return evidence["refined_region"]

    return None


def compact_structural(structural: dict, region: dict) -> dict:
    """Keep compact structural evidence."""
    internal_edges = structural.get(
        "internal_edges",
        region.get("internal_edges", 0),
    )

    boundary_edges = structural.get(
        "boundary_edges",
        region.get("boundary_edges", 0),
    )

    region_exits = structural.get("region_exits", [])
    sequential_like = structural.get("sequential_like_gates", [])

    return {
        "internal_edges": internal_edges,
        "boundary_edges": boundary_edges,
        "region_exit_count": len(region_exits),
        "region_exits": region_exits[:MAX_REGION_EXITS],
        "sequential_like_gate_count": len(sequential_like),
        "sequential_like_gates": sequential_like[:MAX_SEQUENTIAL_GATES],
    }


# ============================================================
# Hybrid Prompt Builder (Phase 4)
# ============================================================

def build_hybrid_prompt(
    evidence: dict,
    refined_region: Any = None,
    weights: Optional[Dict[str, float]] = None,
    heuristic_threshold: Optional[float] = None,
) -> str:
    """
    Construct a Heuristic-Guided reasoning prompt for the LLM.

    Includes:
    1. GNN authoritative facts
    2. Heuristic authoritative facts (composite score, threshold, factor attributions)
    3. Refined region compression metrics (if available)
    4. Heuristic-guided node priority ranking
    5. Contradiction analysis guidance (arbitration when GNN & Heuristic conflict)
    6. Structured JSON output format specification
    """
    graph = evidence.get("graph", {})
    gnn = evidence.get("gnn", {})
    region = evidence.get("region", {})
    structural = evidence.get("structural_evidence", {})

    # Nodes lookup for authentic fanin/fanout resolution
    raw_nodes = evidence.get("nodes", [])
    nodes_by_gate = {n.get("gate"): n for n in raw_nodes if n.get("gate")}

    # Seeds & GNN facts
    seeds = evidence.get("suspicious_seeds", [])
    seeds = sorted(seeds, key=lambda x: safe_float(x.get("gnn_score")), reverse=True)
    compact_seeds = [compact_seed(seed, nodes_by_gate=nodes_by_gate) for seed in seeds]
    gnn_facts = deterministic_gnn_facts(gnn, seeds)

    # Heuristic facts & factor attribution
    heuristic_facts = deterministic_heuristic_facts(
        evidence,
        weights=weights,
        heuristic_threshold=heuristic_threshold,
    )

    # Heuristic-guided node priority ranking
    ranked_nodes_raw = rank_suspicious_nodes(evidence, top_k=MAX_RANKED_NODES)
    compact_ranked_nodes = [
        compact_ranked_node(node, idx + 1)
        for idx, node in enumerate(ranked_nodes_raw)
    ]

    # Region refinement metrics
    refinement_facts = deterministic_refinement_facts(evidence, refined_region)

    # Region nodes
    raw_nodes = evidence.get("nodes", [])
    region_size = region.get("size", len(raw_nodes))
    representative_nodes = sorted(
        raw_nodes,
        key=lambda x: safe_float(x.get("gnn_score")),
        reverse=True,
    )[:MAX_REGION_NODES]
    compact_nodes = [compact_region_node(node) for node in representative_nodes]

    # Gate types and summaries
    gate_types = region.get("gate_types", {})
    graph_summary = compact_graph(graph)
    structural_summary = compact_structural(structural, region)

    region_summary = {
        "expanded_region_size": region_size,
        "gate_types": gate_types,
        "representative_nodes_shown": len(compact_nodes),
    }

    # Modality comparison note
    gnn_seed_count = gnn_facts["suspicious_seed_count"]
    h_decision = heuristic_facts["heuristic_decision"]
    gnn_indicates_suspicious = gnn_seed_count > 0 and (
        gnn_facts.get("seed_count_at_or_above_threshold", 0) > 0
    )

    if gnn_indicates_suspicious and h_decision == "SUSPICIOUS":
        concordance_status = "AGREEMENT_SUSPICIOUS (Both GNN and Heuristic indicate suspicious behavior)"
    elif (not gnn_indicates_suspicious) and h_decision == "NORMAL":
        concordance_status = "AGREEMENT_NORMAL (Both GNN and Heuristic indicate normal circuit logic)"
    else:
        concordance_status = f"DIVERGENCE_DETECTED (GNN Suspicious Seeds={gnn_seed_count}, Heuristic Decision={h_decision})"

    refinement_section = ""
    if refinement_facts is not None:
        refinement_section = f"""
============================================================
REGION REFINEMENT METRICS (GRAPH-THEORETIC PRUNING)
============================================================

The initial candidate neighborhood underwent graph-theoretic leaf pruning
to remove peripheral non-suspicious logic while guaranteeing the preservation
of core trigger anchors, sequential state elements, and seed-to-exit paths:

{json.dumps(refinement_facts, indent=2)}
"""

    prompt = f"""
You are the expert reasoning arbitrator of a Hybrid Hardware Trojan Detection Framework.

The system combines three specialized analytical layers:
1. GNN (Statistical Detector): Primary localizer identifying anomalous gates from learned graph embeddings.
2. HEURISTIC LAYER (Structural Analyzer & Calibrator): Quantifies circuit topology (connectivity, sequential loops, trigger concentration) and computes calibrated composite scores and factor attributions.
3. LLM (Intelligent Arbitrator & Explainer): Synthesizes statistical and structural evidence, conducts contradiction analysis, and delivers the final hardware security determination.

============================================================
CRITICAL NUMERICAL RULE
============================================================

All numerical facts in this prompt were computed deterministically by the Python pipeline.
Treat the sections "GNN AUTHORITATIVE NUMERICAL FACTS", "HEURISTIC AUTHORITATIVE NUMERICAL FACTS",
and "REGION REFINEMENT METRICS" as ground truth.

DO NOT:
- recount nodes, edges, or scores yourself
- recalculate percentages, ratios, or differences
- invent or extrapolate unlisted numbers
- treat node identifiers as semantic evidence (they are anonymized)

============================================================
MODALITY CONCORDANCE STATUS
============================================================

{concordance_status}

============================================================
GNN AUTHORITATIVE NUMERICAL FACTS
============================================================

{json.dumps(gnn_facts, indent=2)}

============================================================
HEURISTIC AUTHORITATIVE NUMERICAL FACTS
============================================================

{json.dumps(heuristic_facts, indent=2)}

Explanation of Key Heuristic Factors:
- composite_heuristic_score: Linearly weighted index in [0, 1] derived from 10 calibrated features.
- optimal_heuristic_threshold: Validated decision boundary separating normal from suspicious circuits.
- top_contributing_factors: Normalized feature values multiplied by learned weights (Contribution = w_i * F_i).
{refinement_section}
============================================================
TOP SUSPICIOUS NODES (HEURISTIC-GUIDED PRIORITY)
============================================================

The following nodes are ranked by composite structural priority, which combines
GNN suspicion with sequential element types, fanin/fanout, and proximity to primary outputs:

{json.dumps(compact_ranked_nodes, indent=2)}

============================================================
GNN SUSPICIOUS SEEDS (THRESHOLD CROSSINGS)
============================================================

Authoritative GNN-positive seed gates sorted by raw GNN probability:

{json.dumps(compact_seeds, indent=2)}

============================================================
CIRCUIT GRAPH & STRUCTURAL TOPOLOGY
============================================================

Graph Summary:
{json.dumps(graph_summary, indent=2)}

Structural Neighborhood Summary:
{json.dumps(structural_summary, indent=2)}

Region Logic Distribution:
{json.dumps(region_summary, indent=2)}

Representative Region Nodes:
{json.dumps(compact_nodes, indent=2)}

============================================================
CONTRADICTION ANALYSIS & ARBITRATION GUIDELINES
============================================================

When synthesizing the GNN and Heuristic signals, apply the following arbitration rules:

1. WHEN MODALITIES AGREE (Both SUSPICIOUS):
   - Strong structural anomaly detected across both statistical and topological dimensions.
   - Investigate the top contributing heuristic factors (e.g., high sequential ratio, trigger concentration).
   - Evaluate whether sequential registers form an internal activation trigger driving payload exits.

2. WHEN MODALITIES AGREE (Both NORMAL):
   - High confidence clean circuit.
   - Verify that observed logic represents standard control or datapath circuitry without stealthy state loops.

3. WHEN GNN IS SUSPICIOUS, BUT HEURISTIC IS NORMAL OR UNCERTAIN:
   - Investigate potential GNN false positives:
     * High-fanout clock/reset distribution or wide arithmetic structures.
     * Isolated gates lacking internal interconnectivity or sequential loops.
   - If the structural heuristic factors indicate low density and high boundary dispersion,
     exercise caution and consider downgrading the assessment to UNCERTAIN or NORMAL.

4. WHEN GNN IS MARGINAL/NORMAL, BUT HEURISTIC IS SUSPICIOUS:
   - Investigate potential stealthy or distributed Trojan mechanisms:
     * Multi-stage counter or distributed finite state machine whose individual gates have subdued GNN scores.
     * Strong localized clustering and high sequential ratio despite moderate peak GNN probability.
   - If structural clustering and sequential loop concentration are anomalous, explain why the heuristic
     elevates suspicion despite lower individual gate probabilities.

============================================================
STRICT REASONING CONSTRAINTS
============================================================

- Do not call the suspicious region a "payload"; distinguish between trigger logic and payload exits.
- Do not claim malicious intent or state machines unless supported by observable sequential topology.
- Do not use node identifiers as evidence.
- Cautiously interpret structural topology using phrases like:
  "consistent with", "suggests localized state-dependent logic", "topologically aligned with".

============================================================
REQUIRED OUTPUT FORMAT
============================================================

You MUST provide your response in TWO parts:

PART 1: STRICT JSON BLOCK
Enclose a valid JSON object in a ```json ``` block conforming exactly to this schema:

```json
{{
  "decision": "SUSPICIOUS" | "NORMAL" | "UNCERTAIN",
  "confidence": "LOW" | "MEDIUM" | "HIGH",
  "gnn_heuristic_agreement": true | false,
  "arbitration_rationale": "<Concise rationale synthesizing GNN scores and structural heuristic factors>",
  "trojan_structure_type": "combinational_trigger" | "sequential_counter" | "stealthy_trigger" | "none" | "unknown",
  "suspicious_gate_classes": ["<e.g. sequential flip-flops>", "<logic trigger gates>"],
  "payload_exit_analysis": "<Description of how the suspicious region couples to external circuitry>",
  "counter_evidence": "<Counter-evidence observed or 'No significant counter-evidence visible'>",
  "false_positive_risk": "LOW" | "MEDIUM" | "HIGH"
}}
```

PART 2: STRUCTURED TEXT REPORT

DECISION: <SUSPICIOUS | NORMAL | UNCERTAIN>
CONFIDENCE: <LOW | MEDIUM | HIGH>

OBSERVED_EVIDENCE:
- 3 to 5 concrete observations using AUTHORITATIVE NUMERICAL FACTS (seed count, composite score, threshold)

STRUCTURAL_INTERPRETATION:
- 2 to 4 cautious interpretations of circuit topology and heuristic attributions

CONTRADICTION_ANALYSIS:
- Explicit arbitration analysis comparing GNN and Heuristic signals

COUNTER_EVIDENCE:
- Observations that weaken suspicion (or: "No significant counter-evidence is visible in the supplied evidence.")

REASONING:
- Synthesis paragraph connecting GNN scores, structural heuristic factors, and circuit topology to the final decision.
""".strip()

    return prompt


# ============================================================
# Baseline Prompt Builder (Experiment 2 Preservation)
# ============================================================

def build_baseline_prompt(evidence: dict) -> str:
    """
    Construct the baseline prompt without heuristic or refinement facts.
    Preserves exact historical behavior for Experiment 2 (pure GNN-LLM baseline).
    """
    graph = evidence.get("graph", {})
    gnn = evidence.get("gnn", {})
    region = evidence.get("region", {})
    structural = evidence.get("structural_evidence", {})

    raw_nodes = evidence.get("nodes", [])
    nodes_by_gate = {n.get("gate"): n for n in raw_nodes if n.get("gate")}

    seeds = evidence.get("suspicious_seeds", [])
    seeds = sorted(seeds, key=lambda x: safe_float(x.get("gnn_score")), reverse=True)
    compact_seeds = [compact_seed(seed, nodes_by_gate=nodes_by_gate) for seed in seeds]
    gnn_facts = deterministic_gnn_facts(gnn, seeds)
    region_size = region.get("size", len(raw_nodes))
    representative_nodes = sorted(
        raw_nodes,
        key=lambda x: safe_float(x.get("gnn_score")),
        reverse=True,
    )[:MAX_REGION_NODES]
    compact_nodes = [compact_region_node(node) for node in representative_nodes]

    gate_types = region.get("gate_types", {})
    graph_summary = compact_graph(graph)
    structural_summary = compact_structural(structural, region)

    region_summary = {
        "expanded_region_size": region_size,
        "gate_types": gate_types,
        "representative_nodes_shown": len(compact_nodes),
    }

    prompt = f"""
You are analyzing gate-level structural evidence for Hardware Trojan detection.

The system has already used a trained GNN as the PRIMARY detector and localizer.

Your role is NOT to replace the GNN and NOT to perform numerical computation.
Your role is to interpret the supplied structural evidence and explain whether
the observed structure is consistent with Hardware Trojan behavior.

============================================================
CRITICAL NUMERICAL RULE
============================================================

All numerical facts in this prompt were computed or copied by the Python
pipeline before you received them.

Treat the section "AUTHORITATIVE NUMERICAL FACTS" as ground truth.

DO NOT:
- recount nodes or scores yourself
- calculate percentages or ratios
- change a count
- infer a threshold count from the displayed seed list
- substitute one GNN statistic for another

If a number is not explicitly supplied, do not invent it.

In particular, distinguish:
- suspicious_seed_count = actual GNN-positive seed count
- expanded_region_size = structural neighborhood size

These are different quantities.

============================================================
SYSTEM ROLES
============================================================

1. GNN
   Primary detector and localizer.

2. Structural evidence
   Provides observable graph/topology information around the GNN seeds.

3. LLM
   Interprets the supplied evidence and produces a concise explanation.

4. Heuristic
   The heuristic is an independent comparison method.
   Its output is NOT provided here and MUST NOT be inferred.

============================================================
AUTHORITATIVE NUMERICAL FACTS
============================================================

{json.dumps(gnn_facts, indent=2)}

The expanded suspicious region size is:

{region_size}

IMPORTANT:
The expanded region is a structural neighborhood around the GNN seeds.
It is NOT equivalent to the GNN-positive set.

============================================================
STRICT EVIDENCE RULES
============================================================

1. NODE IDENTIFIERS
Node identifiers are anonymized and have no semantic meaning.
Never use node names as evidence.

2. OBSERVED FACT VS INTERPRETATION
Observed fact: Something explicitly present in the supplied evidence.
Interpretation: A cautious explanation of what the observed structure could indicate.
Never present an interpretation as an observed fact.

3. GNN SCORES
A high GNN score means the trained GNN considers that node suspicious.
This is detection evidence, not proof of malicious functionality.

4. DO NOT INVENT FUNCTIONALITY
The evidence does NOT automatically establish: a trigger, a payload, a backdoor,
a reset mechanism, a state machine, or malicious intent.

5. EXPANDED REGION
GNN suspicious seeds != expanded region. Do not call the entire expanded region Trojan logic.

6. SEQUENTIAL LOGIC
If DFFs or other sequential-like gates appear, describe them as sequential logic.
Do not conclude they store malicious state unless explicitly supported.

7. TRIGGER-LIKE STRUCTURE
Use cautious wording: "consistent with", "could indicate", "may represent".

8. REGION EXITS
Region exits are structural connections to outside logic; do not automatically call them payload outputs.

9. COUNTER-EVIDENCE
Report only evidence actually present in the supplied data.

============================================================
GRAPH SUMMARY
============================================================

{json.dumps(graph_summary, indent=2)}

============================================================
GNN SUSPICIOUS SEEDS
============================================================

The following are the actual GNN suspicious seeds. They crossed the
GNN threshold in the evidence-generation step.

{json.dumps(compact_seeds, indent=2)}

============================================================
EXPANDED REGION SUMMARY
============================================================

{json.dumps(region_summary, indent=2)}

============================================================
STRUCTURAL EVIDENCE
============================================================

{json.dumps(structural_summary, indent=2)}

============================================================
REPRESENTATIVE REGION NODES
============================================================

{json.dumps(compact_nodes, indent=2)}

============================================================
REASONING PROCEDURE
============================================================

STEP 1 — GNN SIGNAL: Use AUTHORITATIVE NUMERICAL FACTS.
STEP 2 — SEED CONCENTRATION: Discuss localization within expanded region.
STEP 3 — CONNECTIVITY: Use internal/boundary edges, fanin, fanout, exits.
STEP 4 — LOGIC STRUCTURE: Discuss gate types and sequential/combinational structure.
STEP 5 — POSSIBLE TRIGGER-LIKE STRUCTURE: Explain cautiously if topology supports it.
STEP 6 — EXTERNAL CONNECTIONS: Describe connections from region to surrounding circuit.
STEP 7 — COUNTER-EVIDENCE: Report only visible counter-evidence.
STEP 8 — FINAL ASSESSMENT: Choose SUSPICIOUS, NORMAL, or UNCERTAIN.

============================================================
REQUIRED OUTPUT FORMAT
============================================================

DECISION: <SUSPICIOUS | NORMAL | UNCERTAIN>

CONFIDENCE: <LOW | MEDIUM | HIGH>

OBSERVED_EVIDENCE:
- 3 to 5 concrete observations
- include the authoritative seed count and region size when relevant
- do not perform new calculations

STRUCTURAL_INTERPRETATION:
- 2 to 4 cautious interpretations
- use "consistent with", "could indicate", or similar wording
- do not invent trigger/payload functionality

COUNTER_EVIDENCE:
- 1 to 3 observations that weaken the interpretation
If none are visible, write exactly:
No significant counter-evidence is visible in the supplied evidence.

REASONING:
A short paragraph connecting the GNN signal and structural evidence to
the final assessment.
""".strip()

    return prompt


# ============================================================
# Main Prompt Interface
# ============================================================

def build_prompt(
    evidence: dict,
    mode: str = "hybrid",
    refined_region: Any = None,
    weights: Optional[Dict[str, float]] = None,
    heuristic_threshold: Optional[float] = None,
) -> str:
    """
    Unified entry point to build an LLM prompt.

    Parameters:
    -----------
    evidence: dict
        Structured evidence dictionary (e.g. from evidence.json or anonymized)
    mode: str
        "hybrid" (Phase 4, default) or "baseline" (Experiment 2 pure GNN)
    refined_region: Any
        Optional RefinedRegion object or metrics dict from Phase 3
    weights: dict | None
        Optional override for heuristic weights
    heuristic_threshold: float | None
        Optional override for heuristic decision threshold
    """
    if mode.lower() == "baseline":
        return build_baseline_prompt(evidence)
    elif mode.lower() == "hybrid":
        return build_hybrid_prompt(
            evidence,
            refined_region=refined_region,
            weights=weights,
            heuristic_threshold=heuristic_threshold,
        )
    else:
        raise ValueError(
            f"Unknown prompt mode: '{mode}'. Expected 'hybrid' or 'baseline'."
        )


# ============================================================
# CLI Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Hardware Trojan LLM Prompt Builder (Hybrid and Baseline)."
    )
    parser.add_argument(
        "evidence",
        type=str,
        help="Path to evidence JSON file (e.g. evidence_anonymized.json)",
    )
    parser.add_argument(
        "--mode",
        choices=["hybrid", "baseline"],
        default="hybrid",
        help="Prompt mode: 'hybrid' (GNN + Heuristic layer, default) or 'baseline' (pure GNN).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Custom output file path for the prompt.",
    )
    parser.add_argument(
        "--weights",
        type=str,
        default=None,
        help="Optional path to custom optimized weights JSON file.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Optional override for heuristic threshold.",
    )

    args = parser.parse_args()

    evidence_path = Path(args.evidence)
    if not evidence_path.exists():
        raise FileNotFoundError(f"Evidence file not found: {evidence_path}")

    with evidence_path.open("r", encoding="utf-8") as f:
        evidence = json.load(f)

    # Load custom weights if provided
    weights = None
    threshold = args.threshold
    if args.weights:
        weights_path = Path(args.weights)
        if weights_path.exists():
            w, t = load_optimized_weights(weights_path)
            weights = w
            if threshold is None:
                threshold = t

    prompt = build_prompt(
        evidence,
        mode=args.mode,
        weights=weights,
        heuristic_threshold=threshold,
    )

    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.output:
        output_path = Path(args.output)
    else:
        suffix = "_hybrid_prompt.txt" if args.mode == "hybrid" else "_prompt.txt"
        output_name = evidence_path.stem.replace("_prompt", "") + suffix
        output_path = DEFAULT_OUTPUT_DIR / output_name

    output_path.write_text(prompt, encoding="utf-8")

    # Only write legacy _prompt.txt for baseline mode
    if args.mode == "baseline":
        legacy_output_path = DEFAULT_OUTPUT_DIR / (evidence_path.stem.replace("_prompt", "") + "_prompt.txt")
        if legacy_output_path != output_path:
            legacy_output_path.write_text(prompt, encoding="utf-8")

    print("========== HARDWARE TROJAN LLM PROMPT ==========")
    print("Evidence :", evidence_path)
    print("Mode     :", args.mode)
    print("Saved to :", output_path.resolve())
    print("Length   :", len(prompt), "characters (~", len(prompt) // 4, "tokens)")


if __name__ == "__main__":
    main()
