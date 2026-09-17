"""
LLM reasoning stage for Hardware Trojan detection.

Architecture:

    Netlist
       ↓
      GNN
       ↓
 Suspicious nodes
       ↓
 Suspicious region
       ↓
 Structured evidence
       ↓
 Anonymizer
       ↓
      LLM
       ↓
 SUSPICIOUS / NORMAL / UNCERTAIN
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


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
    Preserve the complete structural information already generated
    by the evidence stage.

    We are intentionally NOT removing inputs/outputs because they
    may be useful for LLM reasoning.
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

    for field in [
        "depth_from_input",
        "distance_to_output",
        "primary_input",
        "primary_output",
        "inputs",
        "outputs",
        "region_exit",
        "external_outputs",
    ]:
        if field in node:
            result[field] = node[field]

    return result


# ============================================================
# Prompt
# ============================================================

def build_prompt(evidence: dict) -> str:

    graph = evidence.get("graph", {})
    gnn = evidence.get("gnn", {})
    region = evidence.get("region", {})
    structural = evidence.get(
        "structural_evidence",
        {},
    )

    seeds = evidence.get(
        "suspicious_seeds",
        [],
    )

    nodes = evidence.get(
        "nodes",
        [],
    )

    # --------------------------------------------------------
    # Sort GNN seeds by score
    # --------------------------------------------------------

    seeds = sorted(
        seeds,
        key=lambda x: safe_float(
            x.get("gnn_score")
        ),
        reverse=True,
    )

    compact_seeds = [
        {
            "gate": node.get("gate"),
            "type": node.get("type"),
            "gnn_score": round(
                safe_float(
                    node.get("gnn_score")
                ),
                6,
            ),
        }
        for node in seeds
    ]

    # --------------------------------------------------------
    # Compact all region nodes
    # --------------------------------------------------------

    compact_nodes = [
        compact_node(node)
        for node in nodes
    ]

    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    prompt = f"""
You are the final reasoning component of a Hardware Trojan
detection system.

The GNN has already analyzed the complete gate-level circuit.

Your job is to interpret the GNN's detection result and determine
whether the GNN-identified region is consistent with a Hardware
Trojan.

============================================================
MOST IMPORTANT RULE
============================================================

THE GNN DETECTION IS THE PRIMARY DETECTION SIGNAL.

You MUST use the GNN output as the starting point for your decision.

The LLM is NOT replacing the GNN.

The LLM is interpreting and explaining the GNN result.

Think of the system as:

    GNN  = detector/localizer
    LLM  = structural reasoning + explanation

Therefore:

- A strong concentration of high GNN scores is strong evidence.
- A coherent region containing many high-scoring nodes is stronger
  evidence than one isolated high-scoring node.
- Structural evidence should be used to explain and validate the
  GNN finding.
- Do NOT reject a suspicious GNN result merely because the exact
  functional purpose of the circuit is unknown.
- Do NOT require mathematical proof of a trigger/payload.
- Hardware Trojan detection from gate-level structure is inherently
  an evidence-based classification problem.

============================================================
STRICT RULES
============================================================

1. NEVER use node names as evidence.

Names such as NODE_0003 or NODE_0042 are anonymized identifiers.

2. NEVER infer maliciousness from a name.

3. Do not invent circuit functionality.

If the evidence does not explicitly establish that a signal is a
reset, trigger, payload, etc., describe the structure cautiously.

4. GNN SCORES ARE IMPORTANT.

The GNN has been trained specifically to identify suspicious
hardware structures.

Use:
- number of high-scoring nodes
- score magnitude
- score concentration
- suspicious-region size
- relationship between suspicious nodes

as primary detection evidence.

5. STRUCTURAL EVIDENCE EXPLAINS THE GNN RESULT.

Use:
- connectivity
- gate types
- fan-in
- fan-out
- internal edges
- boundary edges
- sequential elements
- region exits
- input/output connectivity

to determine whether the GNN finding is structurally coherent.

6. Do not require complete circuit functionality.

The original circuit functionality is not provided.

That is expected.

7. UNCERTAIN should NOT be used simply because:

- the exact trigger condition is unknown
- the exact payload function is unknown
- external signals are unnamed
- the complete circuit specification is unavailable

Those are normal limitations of structural analysis.

Use UNCERTAIN only when the GNN evidence itself is weak,
contradictory, isolated, or insufficient.

8. Do not use heuristic-detector output.

The heuristic detector is an independent competing method.

9. Do not use ground-truth labels.

10. Do not assume every high-scoring node is malicious individually.

Evaluate the overall suspicious region.

============================================================
DECISION RULE
============================================================

Use the following reasoning hierarchy.

STRONG GNN SIGNAL:

If many nodes have very high GNN scores and they form a coherent
region, this strongly supports SUSPICIOUS.

MODERATE GNN SIGNAL:

If several nodes are suspicious but the region is less coherent,
use the structural evidence to determine whether the finding is
Trojan-consistent.

WEAK GNN SIGNAL:

If only a few isolated nodes have elevated scores and there is
little structural support, NORMAL or UNCERTAIN may be appropriate.

IMPORTANT:

Do NOT turn "I cannot prove a Trojan" into UNCERTAIN.

The question is:

"Does the GNN evidence, together with the supplied structural
evidence, support a Trojan-consistent interpretation?"

============================================================
GRAPH
============================================================

{json.dumps(graph, indent=2)}


============================================================
GNN OUTPUT — PRIMARY EVIDENCE
============================================================

{json.dumps(gnn, indent=2)}


============================================================
TOP GNN SUSPICIOUS NODES
============================================================

These are the nodes ranked most suspicious by the trained GNN.

They are sorted from highest to lowest GNN score.

{json.dumps(compact_seeds, indent=2)}


============================================================
SUSPICIOUS REGION
============================================================

{json.dumps(region, indent=2)}


============================================================
STRUCTURAL EVIDENCE
============================================================

{json.dumps(structural, indent=2)}


============================================================
REGION NODE DETAILS
============================================================

The following information describes the structure around the
GNN-identified suspicious region.

Use it to interpret the GNN result.

{json.dumps(compact_nodes, indent=2)}


============================================================
REASONING TASK
============================================================

Perform these steps.

STEP 1 — GNN EVIDENCE

Determine:

- How many suspicious seed nodes exist?
- How high are their scores?
- Is suspicion concentrated?
- How large is the suspicious region?

STEP 2 — GNN COHERENCE

Determine whether the high-scoring nodes form a coherent
structural region.

STEP 3 — STRUCTURAL INTERPRETATION

Examine:

- gate-type composition
- combinational logic
- sequential-like logic
- fan-in
- fan-out
- internal connectivity
- boundary connectivity
- region exits

STEP 4 — TROJAN CONSISTENCY

Determine whether the structural characteristics provide
additional support for the GNN's Trojan suspicion.

You do NOT need to prove malicious intent.

STEP 5 — COUNTER-EVIDENCE

Identify genuine evidence that contradicts the GNN finding.

Do not treat "unknown functionality" as counter-evidence.

STEP 6 — FINAL DECISION

Select exactly one:

SUSPICIOUS
NORMAL
UNCERTAIN

============================================================
OUTPUT FORMAT
============================================================

Return exactly:

DECISION: <SUSPICIOUS | NORMAL | UNCERTAIN>

CONFIDENCE: <LOW | MEDIUM | HIGH>

GNN_ASSESSMENT:
<2 concise sentences describing what the GNN found>

STRUCTURAL_EVIDENCE:
- <fact>
- <fact>
- <fact>

INTERPRETATION:
- <structural interpretation>
- <structural interpretation>

COUNTER_EVIDENCE:
- <fact>
- <fact>

REASONING:
<maximum 5 sentences connecting the GNN result and structural
evidence to the final decision>

Do not add another final classification.
"""

    return prompt.strip()


# ============================================================
# Main
# ============================================================

def main():

    if len(sys.argv) != 2:

        print(
            "Usage:"
        )
        print(
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
        "Saved to:",
        output_path.resolve(),
    )


if __name__ == "__main__":
    main()