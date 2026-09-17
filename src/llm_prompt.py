"""
Hardware Trojan LLM reasoning stage.

Pipeline:

    evidence.json
        ↓
    compact evidence extraction
        ↓
    GNN-primary reasoning prompt
        ↓
    Qwen / other LLM

Important:
- GNN is the PRIMARY detector/localizer.
- LLM is a downstream structural reasoning + explanation component.
- Heuristic output is NOT provided to the LLM.
- Node names are anonymized.
- The full circuit graph is NOT sent to the LLM.
- Only the suspicious region and decision-relevant structural evidence
  are provided.
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


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ============================================================
# GNN seed compression
# ============================================================

def compact_seed(node: dict) -> dict:
    """
    Keep only the information needed to communicate the
    authoritative GNN ranking.
    """

    return {
        "gate": node.get("gate"),
        "type": node.get("type"),
        "gnn_score": round(
            safe_float(node.get("gnn_score")),
            4,
        ),
    }


def build_seed_summary(evidence: dict) -> list[dict]:

    seeds = evidence.get("suspicious_seeds", [])

    seeds = sorted(
        seeds,
        key=lambda x: safe_float(
            x.get("gnn_score")
        ),
        reverse=True,
    )

    return [
        compact_seed(seed)
        for seed in seeds
    ]


# ============================================================
# Region node compression
# ============================================================

def compact_region_node(node: dict) -> dict:
    """
    Compact representation of one suspicious-region node.

    We retain topology and GNN information but remove
    redundant metadata.
    """

    result = {
        "gate": node.get("gate"),
        "type": node.get("type"),
        "gnn": round(
            safe_float(node.get("gnn_score")),
            4,
        ),
        "fanin": safe_int(
            node.get("fanin"),
            0,
        ),
        "fanout": safe_int(
            node.get("fanout"),
            0,
        ),
    }

    # Keep positional information if available.
    if "depth_from_input" in node:
        result["depth"] = node["depth_from_input"]

    if "distance_to_output" in node:
        result["dist_to_output"] = node[
            "distance_to_output"
        ]

    # Primary input/output status is useful.
    if node.get("primary_input"):
        result["primary_input"] = True

    if node.get("primary_output"):
        result["primary_output"] = True

    # IMPORTANT:
    # Keep local topology because this is what the LLM
    # actually needs for structural reasoning.
    if "inputs" in node:
        result["inputs"] = node["inputs"]

    if "outputs" in node:
        result["outputs"] = node["outputs"]

    # Region boundary information.
    if node.get("region_exit"):
        result["region_exit"] = True

    if "external_outputs" in node:
        result["external_outputs"] = node[
            "external_outputs"
        ]

    return result


def build_region_nodes(evidence: dict) -> list[dict]:

    nodes = evidence.get("nodes", [])

    compact = [
        compact_region_node(node)
        for node in nodes
    ]

    # Keep the most suspicious nodes first.
    compact.sort(
        key=lambda x: safe_float(
            x.get("gnn")
        ),
        reverse=True,
    )

    return compact


# ============================================================
# Structural evidence compression
# ============================================================

def build_structural_summary(
    evidence: dict,
) -> dict:

    region = evidence.get(
        "region",
        {},
    )

    structural = evidence.get(
        "structural_evidence",
        {},
    )

    result = {
        "internal_edges": structural.get(
            "internal_edges",
            region.get(
                "internal_edges",
                0,
            ),
        ),
        "boundary_edges": structural.get(
            "boundary_edges",
            region.get(
                "boundary_edges",
                0,
            ),
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

    return result


# ============================================================
# GNN summary
# ============================================================

def build_gnn_summary(
    evidence: dict,
) -> dict:

    gnn = evidence.get(
        "gnn",
        {},
    )

    region = evidence.get(
        "region",
        {},
    )

    result = {}

    # Preserve relevant GNN statistics.
    important_fields = [
        "threshold",
        "max_score",
        "mean_score",
        "median_score",
        "num_suspicious_nodes",
        "suspicious_node_count",
    ]

    for field in important_fields:

        if field in gnn:
            result[field] = gnn[field]

    # Region-level values are useful if not already
    # present in the GNN section.
    if "size" in region:
        result["region_size"] = region["size"]

    if "region_size" in region:
        result["region_size"] = region[
            "region_size"
        ]

    return result


# ============================================================
# Region summary
# ============================================================

def build_region_summary(
    evidence: dict,
) -> dict:

    region = evidence.get(
        "region",
        {},
    )

    result = {}

    # Only retain compact, high-value region information.
    fields = [
        "region_size",
        "size",
        "seed_count",
        "suspicious_seed_count",
        "internal_edges",
        "boundary_edges",
        "gate_types",
        "sequential_like_gates",
    ]

    for field in fields:

        if field in region:
            result[field] = region[field]

    return result


# ============================================================
# Main prompt builder
# ============================================================

def build_prompt(evidence: dict) -> str:

    gnn_summary = build_gnn_summary(
        evidence
    )

    seeds = build_seed_summary(
        evidence
    )

    region_summary = build_region_summary(
        evidence
    )

    structural = build_structural_summary(
        evidence
    )

    region_nodes = build_region_nodes(
        evidence
    )

    graph_info = evidence.get(
        "graph",
        {},
    )

    # Only retain basic graph statistics.
    compact_graph = {}

    for field in [
        "nodes",
        "edges",
        "num_nodes",
        "num_edges",
    ]:

        if field in graph_info:
            compact_graph[field] = graph_info[
                field
            ]

    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    prompt = f"""
You are analyzing a suspicious hardware region identified
by a trained Graph Neural Network (GNN).

Your task is to interpret the GNN detection using the
provided structural evidence and produce a clear explanation.

============================================================
IMPORTANT SYSTEM DESIGN
============================================================

The GNN is the PRIMARY DETECTOR and LOCALIZER.

The GNN has already analyzed the complete circuit and
identified suspicious nodes.

The LLM is a DOWNSTREAM REASONING AND EXPLANATION COMPONENT.

Therefore:

1. Start from the GNN result.
2. Evaluate whether the suspicious region is coherent.
3. Use structural evidence to explain and validate the GNN result.
4. Do not require mathematical proof of a Trojan.
5. Do not independently search the entire circuit for another
   suspicious region.
6. Do not ignore a strong GNN result merely because the exact
   Trojan trigger or payload cannot be proven from the supplied
   evidence.

The purpose of your reasoning is:

    GNN detection
        +
    structural interpretation
        =
    explainable Trojan assessment

============================================================
STRICT RULES
============================================================

1. NODE NAMES ARE NOT EVIDENCE.

All identifiers such as NODE_0001 or NODE_0042 are anonymized.

Never infer malicious behavior from a node name.

2. DO NOT INVENT FUNCTIONALITY.

Do not claim a signal is a reset, security signal, trigger,
payload, backdoor, or critical control signal unless the
provided structural evidence supports that interpretation.

3. GNN SCORES ARE THE PRIMARY DETECTION SIGNAL.

A high GNN score means the trained detector considers that
node suspicious.

Multiple high-scoring nodes forming a coherent region provide
stronger evidence than isolated high-scoring nodes.

4. STRUCTURAL EVIDENCE IS USED TO INTERPRET THE GNN RESULT.

Look for:

- concentration of suspicious nodes
- connected suspicious logic
- unusual reconvergence
- multiple inputs converging into logic
- sequential elements
- region exits
- logic feeding external circuit regions
- trigger-like structures
- possible trigger-to-payload relationships

5. DO NOT REQUIRE COMPLETE FUNCTIONAL PROOF.

If the GNN strongly identifies a coherent suspicious region,
lack of an explicitly proven trigger/payload mechanism alone
is NOT sufficient reason to mark the result UNCERTAIN.

6. COUNTER-EVIDENCE MATTERS.

If the region appears structurally ordinary or the suspicious
nodes are isolated and weakly connected, explain that.

7. USE ONLY THE PROVIDED EVIDENCE.

Do not invent missing circuit behavior.

============================================================
CIRCUIT SUMMARY
============================================================

{json.dumps(compact_graph, indent=2)}

============================================================
GNN PRIMARY RESULT
============================================================

The following is the primary detection signal produced by
the trained GNN:

{json.dumps(gnn_summary, indent=2)}

============================================================
TOP GNN SUSPICIOUS NODES
============================================================

These nodes are ranked by the GNN.

{json.dumps(seeds, indent=2)}

Treat this ranking as authoritative.

============================================================
SUSPICIOUS REGION SUMMARY
============================================================

{json.dumps(region_summary, indent=2)}

============================================================
STRUCTURAL EVIDENCE
============================================================

{json.dumps(structural, indent=2)}

============================================================
SUSPICIOUS REGION LOCAL TOPOLOGY
============================================================

The following contains the local topology of the suspicious
region only.

Use it to understand relationships between suspicious nodes.

Do NOT use it to search for a completely different detection.

{json.dumps(region_nodes, indent=2)}

============================================================
REASONING PROCEDURE
============================================================

Follow these steps.

STEP 1 — ASSESS THE GNN SIGNAL

Determine:

- how many suspicious seeds were identified
- how high their GNN scores are
- whether suspicious scores are concentrated
- how large the resulting suspicious region is

STEP 2 — ASSESS REGION COHERENCE

Determine whether the high-scoring nodes form a connected
or structurally meaningful region.

STEP 3 — INTERPRET THE STRUCTURE

Use:

- gate types
- fan-in
- fan-out
- local connectivity
- internal edges
- boundary edges
- region exits
- sequential elements

to explain the structure.

STEP 4 — LOOK FOR TROJAN-LIKE STRUCTURE

Check whether the region contains evidence consistent with:

- trigger/control logic
- unusual reconvergence
- state-dependent logic
- payload-like logic
- reconnection to the surrounding circuit

Do not claim these mechanisms exist unless the topology
supports the interpretation.

STEP 5 — CONSIDER COUNTER-EVIDENCE

Identify any evidence suggesting that the region could instead
be ordinary circuit logic.

STEP 6 — FINAL DECISION

Use the following guidance:

STRONG GNN SIGNAL:
If many nodes have high GNN scores and form a coherent
suspicious region, this strongly supports SUSPICIOUS.

MODERATE GNN SIGNAL:
If several nodes are suspicious but the structural coherence
is weaker, use the structural evidence to determine whether
the evidence supports SUSPICIOUS or whether UNCERTAIN is
appropriate.

WEAK GNN SIGNAL:
If only a few isolated nodes have elevated scores and there
is little structural support, NORMAL or UNCERTAIN may be
appropriate.

Do NOT convert "I cannot prove the exact Trojan mechanism"
into UNCERTAIN when the GNN signal and structural evidence
strongly support the suspicious region.

============================================================
REQUIRED FINAL OUTPUT
============================================================

Return exactly this structure:

DECISION: SUSPICIOUS | NORMAL | UNCERTAIN

CONFIDENCE: LOW | MEDIUM | HIGH

OBSERVED_EVIDENCE:
- concise factual observations from the GNN
- concise factual observations from the region
- concise structural observations

STRUCTURAL_INTERPRETATION:
- explain what the suspicious structure indicates
- explain how the structure supports or weakens the GNN result

COUNTER_EVIDENCE:
- mention relevant evidence against the detection
- write "None identified" if there is no meaningful
  counter-evidence in the supplied data

REASONING:
Give a concise explanation connecting the GNN result,
the suspicious region, and the structural evidence.

Do not use node names as evidence.

Do not invent circuit functionality.

Do not output another decision after the final DECISION line.
"""

    return prompt


# ============================================================
# Load evidence
# ============================================================

def load_evidence(
    path: Path,
) -> dict:

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


# ============================================================
# Main
# ============================================================

def main():

    if len(sys.argv) != 2:

        print(
            "Usage:\n"
            "  python src/llm_prompt.py <evidence.json>"
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

    evidence = load_evidence(
        evidence_path
    )

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
        "========== LLM PROMPT =========="
    )

    print(
        "Evidence:",
        evidence_path,
    )

    print(
        "Prompt:",
        output_path,
    )

    print(
        "Prompt length:",
        len(prompt),
        "characters",
    )

    print(
        "Approx tokens:",
        round(len(prompt) / 4),
    )


if __name__ == "__main__":
    main()