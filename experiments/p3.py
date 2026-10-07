"""
LLM prompt builder for Hardware Trojan detection.

Pipeline:

    evidence.json
        ↓
    compact evidence extraction
        ↓
    strict reasoning prompt
        ↓
    Qwen / other LLM

Design:
- GNN is the primary detector/localizer.
- LLM performs structural interpretation and explanation.
- Heuristic output is NOT provided to the LLM.
- Node names are anonymized and never used as evidence.
- GNN suspicious seeds are explicitly separated from the
  expanded suspicious region.
- Only compact structural information is sent to the LLM.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_OUTPUT_DIR = (
    ROOT / "results" / "llm"
)

# Maximum number of region nodes shown to the LLM.
# They are selected by GNN score.
MAX_REGION_NODES = 20

# Maximum number of region exits shown.
MAX_REGION_EXITS = 15

# Maximum number of sequential-like gates shown.
MAX_SEQUENTIAL_GATES = 15


# ============================================================
# Helpers
# ============================================================

def safe_float(value, default=0.0):
    """Safely convert a value to float."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def compact_seed(node: dict) -> dict:
    """
    Compact representation of an actual GNN suspicious seed.

    These are nodes that crossed the GNN threshold.
    """

    return {
        "type": node.get("type"),
        "gnn_score": round(
            safe_float(node.get("gnn_score")),
            4,
        ),
        "fanin": node.get("fanin", 0),
        "fanout": node.get("fanout", 0),
    }


def compact_region_node(node: dict) -> dict:
    """
    Compact representation of a region node.

    Only structural information useful for reasoning is retained.

    Deliberately removed:
    - gate/node identifier
    - complete input lists
    - complete output lists
    - external output lists

    These fields add many tokens but provide little value for
    high-level structural reasoning.
    """

    result = {
        "type": node.get("type"),
        "gnn_score": round(
            safe_float(node.get("gnn_score")),
            4,
        ),
        "fanin": node.get("fanin", 0),
        "fanout": node.get("fanout", 0),
    }

    if "depth_from_input" in node:
        result["depth"] = node["depth_from_input"]

    if "distance_to_output" in node:
        result["output_distance"] = node[
            "distance_to_output"
        ]

    if node.get("primary_input"):
        result["primary_input"] = True

    if node.get("primary_output"):
        result["primary_output"] = True

    if node.get("region_exit"):
        result["region_exit"] = True

    return result


def compact_graph(graph: dict) -> dict:
    """
    Keep only aggregate graph statistics.

    Never send the complete circuit graph to the LLM.
    """

    return {
        "nodes": graph.get("nodes", 0),
        "edges": graph.get("edges", 0),
    }


def compact_gnn(gnn: dict, seed_count: int) -> dict:
    """
    Keep only GNN statistics useful for reasoning.
    """

    allowed_fields = [
        "threshold",
        "max_score",
        "mean_score",
        "median_score",
        "min_score",
        "positive_count",
    ]

    result = {}

    for field in allowed_fields:
        if field in gnn:
            result[field] = gnn[field]

    # Explicitly calculate/override the actual seed count.
    result["suspicious_seed_count"] = seed_count

    return result


def compact_structural(
    structural: dict,
    region: dict,
) -> dict:
    """
    Keep compact structural evidence.
    """

    internal_edges = structural.get(
        "internal_edges",
        region.get("internal_edges", 0),
    )

    boundary_edges = structural.get(
        "boundary_edges",
        region.get("boundary_edges", 0),
    )

    region_exits = structural.get(
        "region_exits",
        [],
    )

    sequential_like = structural.get(
        "sequential_like_gates",
        [],
    )

    return {
        "internal_edges": internal_edges,
        "boundary_edges": boundary_edges,
        "region_exit_count": len(region_exits),
        "region_exits": region_exits[
            :MAX_REGION_EXITS
        ],
        "sequential_like_gate_count": len(
            sequential_like
        ),
        "sequential_like_gates": sequential_like[
            :MAX_SEQUENTIAL_GATES
        ],
    }


# ============================================================
# Prompt Builder
# ============================================================

def build_prompt(evidence: dict) -> str:

    graph = evidence.get(
        "graph",
        {},
    )

    gnn = evidence.get(
        "gnn",
        {},
    )

    region = evidence.get(
        "region",
        {},
    )

    structural = evidence.get(
        "structural_evidence",
        {},
    )

    # --------------------------------------------------------
    # GNN suspicious seeds
    # --------------------------------------------------------

    seeds = evidence.get(
        "suspicious_seeds",
        [],
    )

    seeds = sorted(
        seeds,
        key=lambda x: safe_float(
            x.get("gnn_score")
        ),
        reverse=True,
    )

    seed_count = len(seeds)

    compact_seeds = [
        compact_seed(seed)
        for seed in seeds
    ]

    # --------------------------------------------------------
    # Expanded region
    # --------------------------------------------------------

    raw_nodes = evidence.get(
        "nodes",
        [],
    )

    region_size = region.get(
        "size",
        len(raw_nodes),
    )

    # Select only the highest-scoring region nodes.
    #
    # IMPORTANT:
    # These are representative region nodes, NOT necessarily
    # GNN-positive nodes.
    representative_nodes = sorted(
        raw_nodes,
        key=lambda x: safe_float(
            x.get("gnn_score")
        ),
        reverse=True,
    )[:MAX_REGION_NODES]

    compact_nodes = [
        compact_region_node(node)
        for node in representative_nodes
    ]

    # --------------------------------------------------------
    # Gate types
    # --------------------------------------------------------

    gate_types = region.get(
        "gate_types",
        {},
    )

    # --------------------------------------------------------
    # Compact summaries
    # --------------------------------------------------------

    graph_summary = compact_graph(
        graph
    )

    gnn_summary = compact_gnn(
        gnn,
        seed_count,
    )

    structural_summary = compact_structural(
        structural,
        region,
    )

    region_summary = {
        "expanded_region_size": region_size,
        "gate_types": gate_types,
        "representative_nodes_shown": len(
            compact_nodes
        ),
    }

    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    prompt = f"""
You are analyzing gate-level structural evidence for
Hardware Trojan detection.

The system has already used a trained GNN as the
PRIMARY detector and localizer.

Your job is NOT to replace the GNN.

Your job is to interpret the structural evidence produced
around the GNN's suspicious region and explain whether the
observed structure is consistent with Hardware Trojan
behavior.

============================================================
IMPORTANT: SEED COUNT VS REGION SIZE
============================================================

There are two different quantities.

1. GNN SUSPICIOUS SEEDS

These are nodes whose GNN score crossed the suspicious
threshold.

2. EXPANDED SUSPICIOUS REGION

This is a larger structural neighborhood extracted around
the suspicious seeds.

These quantities MUST NOT be confused.

For example:

    18 GNN suspicious seeds
    47-node expanded region

means:

    18 nodes crossed the GNN threshold.

    The structural region contains 47 nodes.

It does NOT mean that all 47 nodes crossed the threshold.

============================================================
STRICT RULES
============================================================

1. NODE IDENTIFIERS HAVE NO SEMANTIC MEANING

Identifiers are anonymized.

Never use node names as evidence.

------------------------------------------------------------

2. DO NOT INVENT CIRCUIT FUNCTIONALITY

The supplied evidence may show gate types and connectivity.

That does NOT automatically establish:

- trigger
- payload
- reset
- backdoor
- state machine
- safety mechanism
- control signal
- malicious intent

Do not claim any of these as facts unless the supplied
evidence explicitly establishes them.

------------------------------------------------------------

3. DISTINGUISH FACT FROM INTERPRETATION

OBSERVED FACT:

Something explicitly present in the supplied evidence.

Example:

"The region contains sequential-like gates."

INTERPRETATION:

A cautious explanation of what that structure could indicate.

Example:

"The sequential structure could be relevant to
state-dependent behavior."

Never present interpretation as an observed fact.

------------------------------------------------------------

4. GNN SCORES ARE LEARNED DETECTOR OUTPUTS

A high GNN score means the trained GNN considers a node
suspicious.

It is strong detection evidence, but it is not proof of
malicious functionality.

------------------------------------------------------------

5. THE SUSPICIOUS SEED LIST IS AUTHORITATIVE

The suspicious seed list contains the nodes that crossed
the GNN threshold.

Do not search the representative region nodes to redefine
the GNN-positive set.

------------------------------------------------------------

6. THE EXPANDED REGION IS NOT ENTIRELY TROJAN LOGIC

The expanded region contains structural neighbors around
the GNN seeds.

Therefore:

    expanded region != confirmed Trojan region

------------------------------------------------------------

7. STRUCTURAL COHERENCE

Look for observable properties such as:

- concentration of suspicious nodes
- connected suspicious logic
- internal connectivity
- boundary connections
- reconvergence
- fan-in/fan-out patterns
- interaction between combinational and sequential logic
- region exits

Describe these as structural properties.

------------------------------------------------------------

8. SEQUENTIAL LOGIC

If DFFs or other sequential-like gates appear:

You may say:

"The region contains sequential logic."

You may say:

"This could be relevant to state-dependent behavior."

Do NOT automatically say:

"This is a state machine."

"This is a Trojan payload."

"This stores malicious state."

unless explicitly supported.

------------------------------------------------------------

9. TRIGGER-LIKE STRUCTURE

You may identify topology that could be consistent with a
hidden trigger.

Use cautious language:

- "consistent with"
- "could indicate"
- "may represent"
- "provides structural evidence for"

Never claim that an exact Trojan trigger has been proven.

------------------------------------------------------------

10. REGION EXITS

If the suspicious region connects to external logic,
describe the observed reconnection.

For example:

"The region has boundary connections to logic outside
the region."

Do not automatically call these connections a payload
output.

------------------------------------------------------------

11. COUNTER-EVIDENCE

Look for evidence that weakens the Trojan interpretation.

Examples:

- isolated suspicious seeds
- weak connectivity
- little interaction between suspicious nodes
- no meaningful region exits
- broad low-level suspicion
- structure that appears ordinary based on the supplied
  evidence

Do not invent counter-evidence.

============================================================
GRAPH SUMMARY
============================================================

{json.dumps(
    graph_summary,
    indent=2
)}

============================================================
GNN SUMMARY
============================================================

{json.dumps(
    gnn_summary,
    indent=2
)}

The GNN suspicious seed count is:

{seed_count}

The expanded region size is:

{region_size}

These are different quantities.

============================================================
GNN SUSPICIOUS SEEDS
============================================================

These are the actual nodes that crossed the GNN threshold.

They are sorted by GNN score.

{json.dumps(
    compact_seeds,
    indent=2
)}

============================================================
EXPANDED REGION SUMMARY
============================================================

{json.dumps(
    region_summary,
    indent=2
)}

The region contains structural neighbors around the GNN
seeds.

Do not assume that every region node is GNN-positive.

============================================================
STRUCTURAL EVIDENCE
============================================================

{json.dumps(
    structural_summary,
    indent=2
)}

============================================================
REPRESENTATIVE REGION NODES
============================================================

Only the highest-scoring representative region nodes are
shown below.

They are provided for local structural context.

IMPORTANT:

These are representative nodes from the expanded region.

They are NOT necessarily all GNN-positive.

Do not use this list to redefine the GNN suspicious seed set.

{json.dumps(
    compact_nodes,
    indent=2
)}

============================================================
REASONING PROCEDURE
============================================================

STEP 1 — GNN SIGNAL

Report accurately:

- suspicious seed count
- expanded region size
- maximum GNN score
- available score statistics

Never equate seed count with region size.

------------------------------------------------------------

STEP 2 — SUSPICIOUS NODE CONCENTRATION

Determine whether the GNN-positive seeds appear concentrated
within a coherent structural region.

------------------------------------------------------------

STEP 3 — CONNECTIVITY

Examine:

- internal edges
- boundary edges
- fan-in
- fan-out
- region exits

Describe the observable topology.

------------------------------------------------------------

STEP 4 — LOGIC STRUCTURE

Describe combinations of:

- combinational gates
- sequential-like gates
- reconvergence
- fan-in/fan-out
- connections to surrounding circuitry

Do not invent functionality.

------------------------------------------------------------

STEP 5 — POSSIBLE TRIGGER-LIKE STRUCTURE

Ask whether the observed topology contains characteristics
that could be consistent with a hidden trigger.

Do not claim an exact trigger exists unless directly
supported.

------------------------------------------------------------

STEP 6 — POSSIBLE DOWNSTREAM EFFECT

Check whether suspicious-region logic connects to external
logic.

Describe this as topology.

Do not automatically label it a payload.

------------------------------------------------------------

STEP 7 — COUNTER-EVIDENCE

Identify observations that weaken the Trojan interpretation.

If none are visible, explicitly state that no significant
counter-evidence is visible in the supplied evidence.

------------------------------------------------------------

STEP 8 — FINAL ASSESSMENT

Choose exactly one:

SUSPICIOUS
NORMAL
UNCERTAIN

The assessment should consider:

- GNN signal
- suspicious seed concentration
- structural coherence
- connectivity
- observable logic structure
- counter-evidence

A strong and concentrated GNN signal combined with coherent
structural evidence supports a SUSPICIOUS assessment.

The LLM does not need to prove exact trigger functionality,
payload functionality, or malicious intent.

============================================================
REASONING HIERARCHY
============================================================

Follow this hierarchy:

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

Do NOT reverse this hierarchy.

Do not invent a Trojan story first and then use it to justify
the GNN result.

============================================================
REQUIRED OUTPUT FORMAT
============================================================

DECISION: <SUSPICIOUS | NORMAL | UNCERTAIN>

CONFIDENCE: <LOW | MEDIUM | HIGH>

OBSERVED_EVIDENCE:
- 3 to 5 concrete observations
- distinguish GNN seed count from region size

STRUCTURAL_INTERPRETATION:
- 2 to 4 cautious interpretations
- use "consistent with", "could indicate", or similar wording
- do not invent trigger/payload functionality

COUNTER_EVIDENCE:
- 1 to 3 observations that weaken the interpretation

If none are visible, write:

"No significant counter-evidence is visible in the supplied
evidence."

REASONING:
A short paragraph connecting the GNN signal and structural
evidence to the final assessment.

Do not add another classification elsewhere.

NUMERICAL ACCURACY RULE:

Only report numerical values that are explicitly present in the
supplied evidence.

Do not calculate, estimate, or infer:
- score cutoffs
- percentages
- score distributions
- counts
- ratios

unless the required values are explicitly provided.

When describing GNN scores, use the supplied max/mean/median
statistics and the actual suspicious seed count.

For example - 
Never say "18 seeds above 0.99" unless the evidence explicitly
states that all 18 scores are above 0.99.

Do not call the suspicious region a "payload".

You may say:

"The structure is consistent with suspicious or Trojan-like
logic."

Only use the term "payload" if the supplied evidence explicitly
identifies payload functionality.
"""

    return prompt.strip()


# ============================================================
# Main
# ============================================================

def main():

    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "  python src/llm_prompt.py "
            "<evidence_anonymized.json>"
        )
        sys.exit(1)

    evidence_path = Path(
        sys.argv[1]
    )

    if not evidence_path.exists():
        raise FileNotFoundError(
            f"Evidence file not found: "
            f"{evidence_path}"
        )

    with evidence_path.open(
        "r",
        encoding="utf-8",
    ) as f:
        evidence = json.load(f)

    prompt = build_prompt(
        evidence
    )

    DEFAULT_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_name = (
        evidence_path.stem
        + "_prompt.txt"
    )

    output_path = (
        DEFAULT_OUTPUT_DIR
        / output_name
    )

    output_path.write_text(
        prompt,
        encoding="utf-8",
    )

    print(
        "========== HARDWARE TROJAN LLM PROMPT =========="
    )

    print(
        "Evidence:",
        evidence_path,
    )

    print()
    print(
        "Prompt generated successfully."
    )

    print(
        "Prompt length:",
        len(prompt),
        "characters",
    )

    print(
        "Approx. tokens:",
        len(prompt) // 4,
    )

    print(
        "Saved to:",
        output_path.resolve(),
    )


if __name__ == "__main__":
    main()