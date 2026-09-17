"""
LLM prompt builder for Hardware Trojan detection.

Pipeline:
    evidence.json
        ↓
    deterministic evidence extraction
        ↓
    strict reasoning prompt
        ↓
    Qwen / other LLM

Design:
- GNN is the primary detector/localizer.
- LLM performs structural interpretation and explanation.
- Heuristic output is NOT provided to the LLM.
- Node names are anonymized and never used as evidence.
- GNN suspicious seeds are explicitly separated from the expanded region.
- Numerical facts used by the LLM are computed deterministically here.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / "results" / "llm"

MAX_REGION_NODES = 20
MAX_REGION_EXITS = 15
MAX_SEQUENTIAL_GATES = 15


# ============================================================
# Helpers
# ============================================================

def safe_float(value, default=0.0) -> float:
    """Safely convert a value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def compact_seed(node: dict) -> dict:
    """Compact representation of an actual GNN suspicious seed."""
    return {
        "type": node.get("type"),
        "gnn_score": round(safe_float(node.get("gnn_score")), 6),
        "fanin": node.get("fanin", 0),
        "fanout": node.get("fanout", 0),
    }


def compact_region_node(node: dict) -> dict:
    """
    Compact representation of a representative expanded-region node.

    Node identifiers and full connectivity lists are intentionally
    omitted because they are not needed for high-level reasoning.
    """
    result = {
        "type": node.get("type"),
        "gnn_score": round(safe_float(node.get("gnn_score")), 6),
        "fanin": node.get("fanin", 0),
        "fanout": node.get("fanout", 0),
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
        "nodes": graph.get("nodes", 0),
        "edges": graph.get("edges", 0),
    }


def deterministic_gnn_facts(gnn: dict, seeds: list[dict]) -> dict:
    """
    Compute numerical facts in Python so the LLM never has to count
    or infer threshold statistics itself.
    """
    scores = [
        safe_float(seed.get("gnn_score"))
        for seed in seeds
        if seed.get("gnn_score") is not None
    ]

    threshold = safe_float(gnn.get("threshold"))

    facts = {
        "threshold": threshold,
        "suspicious_seed_count": len(seeds),
        "seed_score_max": round(max(scores), 6) if scores else None,
        "seed_score_min": round(min(scores), 6) if scores else None,
        "seed_score_mean": round(sum(scores) / len(scores), 6)
        if scores else None,
        "seed_count_at_or_above_threshold": sum(
            score >= threshold for score in scores
        ),
        "seed_count_at_or_above_0_99": sum(
            score >= 0.99 for score in scores
        ),
    }

    # Keep the evidence-file GNN statistics as separate reference values.
    # They are not recomputed here because they may describe all graph nodes.
    if "max_score" in gnn:
        facts["graph_score_max"] = gnn["max_score"]
    if "mean_score" in gnn:
        facts["graph_score_mean"] = gnn["mean_score"]
    if "median_score" in gnn:
        facts["graph_score_median"] = gnn["median_score"]
    if "min_score" in gnn:
        facts["graph_score_min"] = gnn["min_score"]

    return facts


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
# Prompt Builder
# ============================================================

def build_prompt(evidence: dict) -> str:
    graph = evidence.get("graph", {})
    gnn = evidence.get("gnn", {})
    region = evidence.get("region", {})
    structural = evidence.get("structural_evidence", {})

    # --------------------------------------------------------
    # GNN suspicious seeds
    # --------------------------------------------------------

    seeds = evidence.get("suspicious_seeds", [])

    seeds = sorted(
        seeds,
        key=lambda x: safe_float(x.get("gnn_score")),
        reverse=True,
    )

    seed_count = len(seeds)

    compact_seeds = [compact_seed(seed) for seed in seeds]

    # Deterministic facts: Python calculates these before the LLM sees them.
    gnn_facts = deterministic_gnn_facts(gnn, seeds)

    # --------------------------------------------------------
    # Expanded region
    # --------------------------------------------------------

    raw_nodes = evidence.get("nodes", [])

    region_size = region.get("size", len(raw_nodes))

    representative_nodes = sorted(
        raw_nodes,
        key=lambda x: safe_float(x.get("gnn_score")),
        reverse=True,
    )[:MAX_REGION_NODES]

    compact_nodes = [
        compact_region_node(node)
        for node in representative_nodes
    ]

    # --------------------------------------------------------
    # Gate types
    # --------------------------------------------------------

    gate_types = region.get("gate_types", {})

    # --------------------------------------------------------
    # Compact summaries
    # --------------------------------------------------------

    graph_summary = compact_graph(graph)

    structural_summary = compact_structural(
        structural,
        region,
    )

    region_summary = {
        "expanded_region_size": region_size,
        "gate_types": gate_types,
        "representative_nodes_shown": len(compact_nodes),
    }

    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

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

------------------------------------------------------------

2. OBSERVED FACT VS INTERPRETATION

Observed fact:
Something explicitly present in the supplied evidence.

Interpretation:
A cautious explanation of what the observed structure could indicate.

Never present an interpretation as an observed fact.

------------------------------------------------------------

3. GNN SCORES

A high GNN score means the trained GNN considers that node suspicious.

This is detection evidence, not proof of malicious functionality.

------------------------------------------------------------

4. DO NOT INVENT FUNCTIONALITY

The evidence does NOT automatically establish:
- a trigger
- a payload
- a backdoor
- a reset mechanism
- a state machine
- a safety mechanism
- a control signal
- malicious intent

Do not claim any of these as facts unless explicitly supported.

------------------------------------------------------------

5. EXPANDED REGION

The expanded region contains structural neighbors around suspicious seeds.

Therefore:

    GNN suspicious seeds != expanded region

Do not call the entire expanded region Trojan logic.

------------------------------------------------------------

6. SEQUENTIAL LOGIC

If DFFs or other sequential-like gates appear, you may say:

"The region contains sequential logic."

You may also say:

"This could be relevant to state-dependent behavior."

Do NOT automatically conclude:
- "this is a state machine"
- "this stores malicious state"
- "this is a Trojan payload"

unless explicitly supported.

------------------------------------------------------------

7. TRIGGER-LIKE STRUCTURE

You may describe topology as potentially consistent with a hidden trigger.

Use cautious wording such as:
- "consistent with"
- "could indicate"
- "may represent"
- "provides structural evidence for"

Do not claim an exact trigger has been proven.

------------------------------------------------------------

8. REGION EXITS

Region exits are structural connections from the suspicious region to
logic outside the region.

Describe them as topology.

Do not automatically call them payload outputs.

------------------------------------------------------------

9. COUNTER-EVIDENCE

Only report counter-evidence that is actually visible in the supplied evidence.

Examples include:
- isolated suspicious seeds
- weak connectivity
- little interaction among suspicious nodes
- broad low-confidence suspicion
- ordinary-looking structure

If no meaningful counter-evidence is visible, say so explicitly.

============================================================
GRAPH SUMMARY
============================================================

{json.dumps(graph_summary, indent=2)}

============================================================
GNN SUSPICIOUS SEEDS
============================================================

The following are the actual GNN suspicious seeds. They crossed the
GNN threshold in the evidence-generation step.

They are sorted by GNN score.

{json.dumps(compact_seeds, indent=2)}

IMPORTANT:
This list is authoritative for the GNN-positive seed set.

Do not redefine that set using the representative region nodes.

============================================================
EXPANDED REGION SUMMARY
============================================================

{json.dumps(region_summary, indent=2)}

The representative nodes below are selected from the expanded region.
They are NOT necessarily GNN-positive.

============================================================
STRUCTURAL EVIDENCE
============================================================

{json.dumps(structural_summary, indent=2)}

============================================================
REPRESENTATIVE REGION NODES
============================================================

Only a subset of region nodes is shown for local structural context.

{json.dumps(compact_nodes, indent=2)}

============================================================
REASONING PROCEDURE
============================================================

STEP 1 — GNN SIGNAL
Use the AUTHORITATIVE NUMERICAL FACTS.
Report the suspicious seed count, score statistics, and threshold facts
accurately.

STEP 2 — SEED CONCENTRATION
Discuss whether the suspicious seeds appear localized within the
expanded structural region.

STEP 3 — CONNECTIVITY
Use internal edges, boundary edges, fan-in, fan-out, and region exits
to describe observable topology.

STEP 4 — LOGIC STRUCTURE
Discuss the supplied gate types and sequential/combinational structure.
Do not invent functionality.

STEP 5 — POSSIBLE TRIGGER-LIKE STRUCTURE
If the topology supports it, explain cautiously why some structure could
be consistent with trigger-like behavior.

STEP 6 — EXTERNAL CONNECTIONS
Describe connections from the suspicious region to surrounding circuitry.
Do not automatically label them as a payload.

STEP 7 — COUNTER-EVIDENCE
Report only evidence actually present in the supplied data.

STEP 8 — FINAL ASSESSMENT
Choose exactly one:

SUSPICIOUS
NORMAL
UNCERTAIN

Base the assessment on:
- GNN signal
- seed concentration
- structural coherence
- connectivity
- observable logic structure
- counter-evidence

Do not invent a Trojan narrative and then use it to justify the GNN result.

============================================================
REASONING HIERARCHY
============================================================

    GNN detection signal
            ↓
    suspicious seed concentration
            ↓
    structural coherence
            ↓
    observable topology
            ↓
    cautious interpretation
            ↓
    explanation / assessment

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

Do not add another classification elsewhere.

FINAL LANGUAGE CONSTRAINTS
===========================

- Do not call the suspicious region a "payload".
- Do not claim malicious intent.
- Do not claim an exact trigger unless explicitly supported.
- Do not claim sequential logic proves a Trojan.
- Do not invent numerical values.
- Do not report "X seeds above Y" unless that exact count is present in
  AUTHORITATIVE NUMERICAL FACTS.
- Prefer precise phrases such as:
  "The GNN identified N suspicious seeds."
  "The expanded region contains M nodes."
  "The region contains sequential logic."
  "The structure is consistent with suspicious or Trojan-like logic."
    Do not connect a structural feature to a Trojan mechanism unless the
    supplied evidence contains the specific topology required to support
    that connection.

    For example:
    - sequential gates → may indicate sequential/state-dependent structure
    - region exits → indicate connectivity to surrounding logic

    Do NOT infer:
    - trigger mechanism
    - payload mechanism
    - exploitability
    - malicious state
    from these features alone.
""".strip()

    return prompt


# ============================================================
# Main
# ============================================================

def main():
    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "  python src/llm_prompt.py <evidence_anonymized.json>"
        )
        sys.exit(1)

    evidence_path = Path(sys.argv[1])

    if not evidence_path.exists():
        raise FileNotFoundError(
            f"Evidence file not found: {evidence_path}"
        )

    with evidence_path.open("r", encoding="utf-8") as f:
        evidence = json.load(f)

    prompt = build_prompt(evidence)

    DEFAULT_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_name = evidence_path.stem + "_prompt.txt"
    output_path = DEFAULT_OUTPUT_DIR / output_name

    output_path.write_text(
        prompt,
        encoding="utf-8",
    )

    print("========== HARDWARE TROJAN LLM PROMPT ==========")
    print("Evidence:", evidence_path)
    print()
    print("Prompt generated successfully.")
    print("Prompt length:", len(prompt), "characters")
    print("Approx. tokens:", len(prompt) // 4)
    print("Saved to:", output_path.resolve())


if __name__ == "__main__":
    main()
