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

Important:
- GNN is the primary detector/localizer.
- LLM performs structural interpretation and explanation.
- The LLM does NOT receive heuristic output.
- Node names are anonymized and must never be used as evidence.
- GNN seeds and expanded region are explicitly distinguished.
- Observed facts must be separated from interpretation.
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


# ============================================================
# Helpers
# ============================================================

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def compact_node(node: dict) -> dict:
    """
    Keep only information useful for local structural reasoning.

    Do not include unnecessary metadata that may encourage
    the LLM to invent circuit functionality.
    """

    result = {
        "gate": node.get("gate"),
        "type": node.get("type"),
        "gnn_score": round(
            safe_float(node.get("gnn_score")),
            6,
        ),
        "fanin": node.get("fanin", 0),
        "fanout": node.get("fanout", 0),
    }

    optional_fields = [
        "depth_from_input",
        "distance_to_output",
        "primary_input",
        "primary_output",
        "inputs",
        "outputs",
        "region_exit",
        "external_outputs",
    ]

    for field in optional_fields:
        if field in node:
            result[field] = node[field]

    return result


def compact_seed(node: dict) -> dict:
    """
    Compact representation of a GNN suspicious seed.

    These are actual nodes above the GNN threshold.
    """

    return {
        "gate": node.get("gate"),
        "type": node.get("type"),
        "gnn_score": round(
            safe_float(node.get("gnn_score")),
            6,
        ),
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

    compact_seeds = [
        compact_seed(node)
        for node in seeds
    ]

    # --------------------------------------------------------
    # Region nodes
    # --------------------------------------------------------

    raw_nodes = evidence.get("nodes", [])

    compact_nodes = [
        compact_node(node)
        for node in raw_nodes
    ]

    # --------------------------------------------------------
    # Explicit counts
    # --------------------------------------------------------

    seed_count = len(seeds)

    region_size = region.get(
        "size",
        len(raw_nodes),
    )

    max_gnn_score = gnn.get(
        "max_score",
        max(
            [
                safe_float(x.get("gnn_score"))
                for x in seeds
            ],
            default=0.0,
        ),
    )

    # --------------------------------------------------------
    # Structural evidence
    # --------------------------------------------------------

    compact_structural = {
        "internal_edges": structural.get(
            "internal_edges",
            region.get("internal_edges", 0),
        ),
        "boundary_edges": structural.get(
            "boundary_edges",
            region.get("boundary_edges", 0),
        ),
        "region_exits": structural.get(
            "region_exits",
            [],
        ),
        "sequential_like_gates": structural.get(
            "sequential_like_gates",
            [],
        ),
    }

    gate_types = region.get(
        "gate_types",
        {},
    )

    # --------------------------------------------------------
    # Compact graph summary
    #
    # Do NOT provide the full graph. The LLM only needs
    # aggregate graph information for this task.
    # --------------------------------------------------------

    compact_graph = {
        "nodes": graph.get("nodes"),
        "edges": graph.get("edges"),
    }

    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    prompt = f"""
You are analyzing structural evidence from a gate-level circuit
for Hardware Trojan detection.

The system has already used a trained GNN as the PRIMARY
detector/localizer.

Your role is NOT to replace the GNN.

Your role is to:
1. interpret the suspicious region structurally,
2. distinguish observed facts from possible interpretations,
3. identify evidence that is consistent or inconsistent with
   Hardware Trojan structure,
4. provide a concise explanation of the final assessment.

============================================================
CRITICAL DISTINCTION
============================================================

There are TWO different concepts:

A. GNN SUSPICIOUS SEEDS
   These are nodes whose GNN score crossed the suspicious
   threshold.

B. EXPANDED SUSPICIOUS REGION
   This is a larger structural neighborhood around those seeds.

The number of GNN suspicious seeds MUST NOT be confused with
the size of the expanded region.

For example:

    18 suspicious seeds
    47-node expanded region

means:

    18 nodes crossed the GNN threshold,
    while structural region extraction produced a 47-node region.

Do NOT say that all 47 nodes were above the GNN threshold.

============================================================
STRICT RULES
============================================================

1. NODE NAMES ARE NOT EVIDENCE

Identifiers such as:

    NODE_0001
    NODE_0042

are anonymized identifiers.

Never use their names to infer meaning.

------------------------------------------------------------

2. DO NOT INVENT CIRCUIT FUNCTIONALITY

Do NOT claim that a signal is:

- a trigger
- a payload
- a reset
- a backdoor
- a safety mechanism
- a control signal
- a state machine
- malicious logic

unless the supplied evidence directly establishes that property.

Gate type alone does NOT establish functionality.

For example:

    DFF + combinational gates

only establishes the presence of sequential and combinational
logic.

It does NOT prove that the logic is a Trojan payload or a
state machine.

------------------------------------------------------------

3. SEPARATE FACT FROM INTERPRETATION

OBSERVED FACT:

Something explicitly present in the supplied evidence.

Example:

"The region contains 5 sequential-like gates."

INTERPRETATION:

A cautious explanation of what that structure could mean.

Example:

"The sequential structure could be relevant to state-dependent
behavior, but the supplied evidence does not establish its
functional purpose."

Never present an interpretation as a fact.

------------------------------------------------------------

4. GNN SCORES ARE NOT PROOF

A high GNN score means that the trained detector considers
that node suspicious.

It does NOT mathematically prove that the node is Trojan logic.

Use GNN results as strong detection evidence, but describe
their meaning accurately.

------------------------------------------------------------

5. SUSPICIOUS SEEDS ARE AUTHORITATIVE

The SUSPICIOUS SEEDS section contains the actual nodes that
crossed the GNN threshold.

Use this section when discussing GNN-positive nodes.

Do NOT search the expanded region for another interpretation
of the GNN threshold.

------------------------------------------------------------

6. DO NOT ASSUME EVERY REGION NODE IS TROJAN

The expanded region contains both:

- GNN-positive seed nodes
- neighboring nodes included because of structural connectivity

Therefore:

    suspicious region != confirmed Trojan region

------------------------------------------------------------

7. STRUCTURAL COHERENCE MATTERS

Look for observable structural properties such as:

- connected suspicious nodes
- dense local connectivity
- reconvergence
- fan-in/fan-out patterns
- combinational/sequential interaction
- region exits
- suspicious logic connected to surrounding circuitry
- possible trigger-like structure

These are structural observations.

Do not automatically assign malicious functionality to them.

------------------------------------------------------------

8. SEQUENTIAL LOGIC

If DFFs or other sequential-like gates are present:

Describe them as sequential logic.

You MAY say:

"The region contains sequential logic."

You MAY say:

"This could indicate state-dependent behavior."

You MUST NOT automatically say:

"This is a state machine."

"This is a payload."

"This stores the malicious state."

unless the evidence explicitly establishes those properties.

------------------------------------------------------------

9. TRIGGER-LIKE STRUCTURE

You may identify structural characteristics that COULD be
consistent with a trigger.

Use cautious language:

- "consistent with"
- "could indicate"
- "may represent"
- "provides structural evidence for"

Do NOT state:

"A Trojan trigger definitely exists."

------------------------------------------------------------

10. REGION EXITS

If suspicious-region nodes connect to external circuit logic,
describe this as observed reconnection/topology.

For example:

"The region has boundary connections to logic outside the
region."

Do NOT automatically call those connections a payload output.

------------------------------------------------------------

11. COUNTER-EVIDENCE

Actively identify evidence that weakens the Trojan interpretation.

Examples:

- very few suspicious seeds
- isolated suspicious nodes
- weak connectivity
- no meaningful region exits
- no interaction between suspicious nodes
- suspicious scores spread broadly rather than concentrated
- structure that appears ordinary based only on supplied evidence

Do not invent counter-evidence if none is observable.

============================================================
GRAPH SUMMARY
============================================================

{json.dumps(compact_graph, indent=2)}

============================================================
GNN SUMMARY
============================================================

The following describes the detector output.

{json.dumps(gnn, indent=2)}

IMPORTANT:

GNN suspicious seed count:
{seed_count}

Expanded suspicious region size:
{region_size}

Maximum GNN seed score:
{round(safe_float(max_gnn_score), 6)}

Remember:

seed count and region size are different quantities.

============================================================
GNN SUSPICIOUS SEEDS
============================================================

These are the actual GNN-positive nodes, sorted by GNN score.

{json.dumps(compact_seeds, indent=2)}

============================================================
EXPANDED SUSPICIOUS REGION
============================================================

The region contains:

{region_size} nodes

This region is NOT equivalent to the number of GNN-positive
seeds.

Region summary:

{json.dumps({
    "size": region_size,
    "gate_types": gate_types,
}, indent=2)}

============================================================
STRUCTURAL EVIDENCE
============================================================

{json.dumps(compact_structural, indent=2)}

============================================================
REGION NODE DETAILS
============================================================

These nodes provide local topology around the suspicious region.

Use them only to describe observable structure.

Do NOT reinterpret the GNN threshold from this section.

Do NOT treat every node in this section as GNN-positive.

{json.dumps(compact_nodes, indent=2)}

============================================================
REASONING PROCEDURE
============================================================

STEP 1 — REPORT THE GNN SIGNAL

State accurately:

- number of GNN suspicious seeds
- expanded region size
- maximum GNN score
- available score statistics

Important:

Do not say the entire expanded region crossed the GNN threshold.

------------------------------------------------------------

STEP 2 — ASSESS STRUCTURAL COHERENCE

Determine whether the GNN-positive nodes appear to form a
structurally connected or concentrated region.

Use:

- internal edges
- boundary edges
- node inputs
- node outputs
- fan-in
- fan-out
- distances/depth where provided

------------------------------------------------------------

STEP 3 — DESCRIBE LOGIC STRUCTURE

Describe what is actually visible.

Examples:

- combinational gates
- sequential-like gates
- reconvergent paths
- high fan-in nodes
- high fan-out nodes
- region exits

Do not assign functionality that is not established.

------------------------------------------------------------

STEP 4 — ASSESS POSSIBLE TRIGGER-LIKE STRUCTURE

Ask:

"Does the topology contain characteristics that could be
consistent with a hidden trigger?"

Do not require the evidence to prove an exact trigger mechanism.

But also do not claim a trigger exists without evidence.

------------------------------------------------------------

STEP 5 — ASSESS POSSIBLE DOWNSTREAM/RECONNECTION STRUCTURE

Determine whether suspicious logic connects to logic outside
the region.

Describe the topology.

Do not automatically label these connections as a payload.

------------------------------------------------------------

STEP 6 — COUNTER-EVIDENCE

Identify observable properties that weaken the interpretation.

If none are present, say:

"No significant counter-evidence is visible in the supplied
structural evidence."

------------------------------------------------------------

STEP 7 — FINAL ASSESSMENT

Choose exactly ONE:

SUSPICIOUS
NORMAL
UNCERTAIN

The assessment should consider:

- GNN signal
- concentration of suspicious seeds
- structural coherence
- connectivity
- observable logic structure
- counter-evidence

A strong, concentrated GNN signal together with a coherent
connected region is meaningful evidence for SUSPICIOUS.

Do not require the LLM to prove the exact Trojan trigger,
payload functionality, or malicious intent from structural
evidence alone.

============================================================
IMPORTANT REASONING HIERARCHY
============================================================

Use this hierarchy:

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
    final explanation

Do NOT reverse this hierarchy.

The LLM should explain the GNN-localized evidence rather than
invent a Trojan story and then use that story as justification.

============================================================
REQUIRED OUTPUT
============================================================

Return exactly this structure:

DECISION: <SUSPICIOUS | NORMAL | UNCERTAIN>

CONFIDENCE: <LOW | MEDIUM | HIGH>

OBSERVED_EVIDENCE:
- 3 to 5 concrete observations from the supplied evidence
- explicitly distinguish GNN seed count from region size

STRUCTURAL_INTERPRETATION:
- 2 to 4 cautious interpretations
- use "consistent with", "could indicate", or similar language
- do not invent trigger/payload functionality

COUNTER_EVIDENCE:
- 1 to 3 observations that weaken the interpretation
- or:
  "No significant counter-evidence is visible in the supplied evidence."

REASONING:
A short paragraph connecting the GNN signal and structural
evidence to the final decision.

Do not add another classification elsewhere in the response.
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

    evidence_path = Path(sys.argv[1])

    if not evidence_path.exists():
        raise FileNotFoundError(
            f"Evidence file not found: {evidence_path}"
        )

    with evidence_path.open(
        "r",
        encoding="utf-8",
    ) as f:
        evidence = json.load(f)

    prompt = build_prompt(evidence)

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
    print("Prompt generated successfully.")

    print(
        "Prompt length:",
        len(prompt),
        "characters",
    )

    print(
        "Saved to:",
        output_path.resolve(),
    )


if __name__ == "__main__":
    main()