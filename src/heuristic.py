"""
Independent Heuristic Baseline Detector for Hardware Trojan Detection.

Design Principles:
- Completely independent from the GNN and the LLM.
- Analyzes the circuit graph using structural, topological, and connectivity heuristics.
- Deterministic and configurable.
- Output MUST NOT be fed to the LLM.
- Produces its own independent verdict, continuous anomaly score, and structural rationale.

Structural signals evaluated:
1. Abnormal fan-in / fan-out (e.g. wide comparator/trigger trees with low observability).
2. Rare / dense gate clustering (atypical localized concentrations of logic).
3. Suspicious sequential-combinational patterns (flip-flop state registers/counters
   isolated from main functional datapath or driving single-point gates).
4. Boundary exit ratio (stealthy triggers with high internal depth and low external exits).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx
import numpy as np

# Make sure src is importable
SRC_DIR = Path(__file__).resolve().parent
ROOT = SRC_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from parser import parse_netlist

DEFAULT_OUTPUT_DIR = ROOT / "results" / "heuristic"
DEFAULT_THRESHOLD = 0.65

SEQUENTIAL_TYPES = {
    "dff",
    "dffs",
    "dffles",
    "dffr",
    "dffrs",
    "dffe",
    "latch",
}


# ============================================================
# Heuristic Feature and Anomaly Extraction
# ============================================================

def is_sequential(gate_type: str) -> bool:
    gt = (gate_type or "").lower()
    return any(st in gt for st in SEQUENTIAL_TYPES)


def compute_node_fanin_fanout_anomalies(
    graph: nx.DiGraph,
) -> Dict[str, Dict[str, float]]:
    """
    Detect gates with abnormal fan-in to fan-out ratios.
    Trojan triggers frequently exhibit high fan-in (multi-condition comparators)
    with low fan-out (often 1 exit point to next stage).
    """
    anomalies: Dict[str, Dict[str, float]] = {}
    nodes = list(graph.nodes())
    if not nodes:
        return anomalies

    in_degrees = [graph.in_degree(n) for n in nodes]
    out_degrees = [graph.out_degree(n) for n in nodes]

    mean_in = float(np.mean(in_degrees))
    std_in = float(np.std(in_degrees)) or 1.0

    mean_out = float(np.mean(out_degrees))
    std_out = float(np.std(out_degrees)) or 1.0

    for node in nodes:
        in_d = graph.in_degree(node)
        out_d = graph.out_degree(node)

        z_in = (in_d - mean_in) / std_in
        z_out = (out_d - mean_out) / std_out

        # Trigger signature: high fanin, single or low fanout
        trigger_signature = 0.0
        if in_d >= 3 and out_d <= 2:
            trigger_signature = min(1.0, 0.25 * (in_d - 2))

        # Output hub anomaly: extraordinarily high fanout
        hub_signature = max(0.0, z_out) / 5.0

        anomalies[node] = {
            "in_degree": in_d,
            "out_degree": out_d,
            "z_in": round(z_in, 4),
            "z_out": round(z_out, 4),
            "trigger_signature": round(min(1.0, trigger_signature), 4),
            "hub_signature": round(min(1.0, hub_signature), 4),
        }

    return anomalies


def compute_sequential_clustering(
    graph: nx.DiGraph,
) -> Tuple[float, List[Set[str]]]:
    """
    Detect clusters of sequential elements (flip-flops) interacting closely.
    Trojan counters/state machines often consist of 2-8 flip-flops in a tight feedback loop
    with minimal interaction with the rest of the circuit.
    """
    seq_nodes = {
        n for n in graph.nodes()
        if is_sequential(graph.nodes[n].get("gate_type", ""))
    }

    if not seq_nodes:
        return 0.0, []

    # Build sequential-reachability subgraph (connected within 2 hops through combinational gates)
    seq_adj: Dict[str, Set[str]] = {n: set() for n in seq_nodes}

    for n in seq_nodes:
        # Check downstream 2 hops
        for succ in graph.successors(n):
            if succ in seq_nodes:
                seq_adj[n].add(succ)
            else:
                for succ2 in graph.successors(succ):
                    if succ2 in seq_nodes:
                        seq_adj[n].add(succ2)

    # Find connected components of sequential nodes
    undirected_seq = nx.Graph()
    undirected_seq.add_nodes_from(seq_nodes)
    for u, neighbors in seq_adj.items():
        for v in neighbors:
            undirected_seq.add_edge(u, v)

    components = [
        c for c in nx.connected_components(undirected_seq)
        if len(c) >= 2
    ]

    # Score components based on counter-like isolation
    cluster_scores = []
    suspicious_clusters = []

    for comp in components:
        # Measure external boundary of this sequential component
        comp_size = len(comp)
        external_out = 0
        for n in comp:
            for s in graph.successors(n):
                if s not in comp:
                    external_out += 1

        # A tight sequential cluster with 2-16 FFs and very few outputs to the main circuit
        # is a characteristic counter-based trigger
        isolation_ratio = 1.0 / (1.0 + external_out / max(1, comp_size))
        if 2 <= comp_size <= 16:
            score = min(1.0, 0.4 + 0.6 * isolation_ratio)
            cluster_scores.append(score)
            suspicious_clusters.append(comp)

    max_seq_score = max(cluster_scores) if cluster_scores else 0.0
    return max_seq_score, suspicious_clusters


def compute_connectivity_stealthiness(
    graph: nx.DiGraph,
) -> float:
    """
    Trojan insertion points typically have low switching activity and low observability.
    Structurally, this manifests as subgraphs having high internal depth but very few PO connections.
    """
    total_nodes = graph.number_of_nodes()
    if total_nodes == 0:
        return 0.0

    po_count = sum(
        1 for n in graph.nodes()
        if graph.nodes[n].get("gate_type") == "PO" or graph.out_degree(n) == 0
    )

    # PO ratio relative to circuit size
    po_ratio = po_count / max(1, total_nodes)
    return round(float(po_ratio), 6)


# ============================================================
# Main Heuristic Detector
# ============================================================

def detect_trojan_heuristic(
    graph: nx.DiGraph,
    circuit_name: str = "circuit",
    threshold: float = DEFAULT_THRESHOLD,
) -> Dict[str, Any]:
    """
    Run independent heuristic Trojan detection on a circuit graph.

    Returns deterministic verdict, continuous score, anomalous node list,
    and structural evidence.
    """
    total_nodes = graph.number_of_nodes()
    total_edges = graph.number_of_edges()

    if total_nodes == 0:
        return {
            "circuit": circuit_name,
            "method": "heuristic_detector",
            "score": 0.0,
            "threshold": threshold,
            "decision": "NORMAL",
            "anomalous_node_count": 0,
            "top_anomalous_nodes": [],
            "structural_evidence": {},
            "verdict_explanation": "Empty graph.",
        }

    # 1. Fan-in / Fan-out analysis
    fan_anomalies = compute_node_fanin_fanout_anomalies(graph)

    # 2. Sequential cluster analysis
    seq_score, suspicious_clusters = compute_sequential_clustering(graph)

    # 3. Gate type distribution
    gate_counts: Dict[str, int] = {}
    for n in graph.nodes():
        gt = str(graph.nodes[n].get("gate_type", "unknown")).lower()
        gate_counts[gt] = gate_counts.get(gt, 0) + 1

    # Count high-fanin trigger gates
    trigger_nodes = [
        n for n, stats in fan_anomalies.items()
        if stats["trigger_signature"] >= 0.5
    ]

    # Node anomaly scoring
    node_scores: Dict[str, float] = {}
    node_reasons: Dict[str, List[str]] = {}

    for n in graph.nodes():
        stats = fan_anomalies[n]
        reasons = []
        score = 0.0

        if stats["trigger_signature"] > 0:
            score += 0.45 * stats["trigger_signature"]
            reasons.append(f"high_fanin_tree(in={stats['in_degree']},out={stats['out_degree']})")

        if is_sequential(graph.nodes[n].get("gate_type", "")):
            # Check if part of a suspicious cluster
            in_cluster = any(n in comp for comp in suspicious_clusters)
            if in_cluster:
                score += 0.40
                reasons.append("isolated_sequential_cluster")

        if stats["hub_signature"] > 0.6:
            score += 0.20 * stats["hub_signature"]
            reasons.append(f"abnormal_fanout_hub(out={stats['out_degree']})")

        node_scores[n] = min(1.0, score)
        if reasons:
            node_reasons[n] = reasons

    # Overall circuit score aggregation
    # Top node anomaly contributions
    sorted_nodes = sorted(node_scores.keys(), key=lambda n: node_scores[n], reverse=True)
    top_k_scores = [node_scores[n] for n in sorted_nodes[:15]]
    mean_top_k = float(np.mean(top_k_scores)) if top_k_scores else 0.0

    # Composite circuit score
    composite_score = (
        0.45 * mean_top_k +
        0.35 * seq_score +
        0.20 * min(1.0, len(trigger_nodes) / 10.0)
    )
    composite_score = round(float(min(1.0, composite_score)), 6)

    # Decision logic
    if composite_score >= threshold:
        decision = "SUSPICIOUS"
    elif composite_score >= threshold * 0.75:
        decision = "UNCERTAIN"
    else:
        decision = "NORMAL"

    # Top anomalous node details (anonymized in evidence if needed, but here identified locally)
    top_anomalous_nodes = []
    for n in sorted_nodes[:20]:
        if node_scores[n] >= 0.3:
            top_anomalous_nodes.append({
                "node": str(n),
                "gate_type": graph.nodes[n].get("gate_type", ""),
                "score": round(node_scores[n], 4),
                "reasons": node_reasons.get(n, []),
            })

    explanation_parts = []
    if trigger_nodes:
        explanation_parts.append(
            f"Detected {len(trigger_nodes)} high-fan-in trigger-like gate(s)."
        )
    if suspicious_clusters:
        explanation_parts.append(
            f"Detected {len(suspicious_clusters)} isolated sequential cluster(s)."
        )
    if not explanation_parts:
        explanation_parts.append("No significant structural anomalies detected.")

    verdict_explanation = " ".join(explanation_parts)

    return {
        "circuit": circuit_name,
        "method": "heuristic_detector",
        "score": composite_score,
        "threshold": threshold,
        "decision": decision,
        "anomalous_node_count": len(top_anomalous_nodes),
        "top_anomalous_nodes": top_anomalous_nodes,
        "structural_evidence": {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "trigger_node_count": len(trigger_nodes),
            "suspicious_sequential_clusters": len(suspicious_clusters),
            "sequential_cluster_score": round(seq_score, 4),
            "top_k_mean_anomaly": round(mean_top_k, 4),
            "gate_counts": gate_counts,
        },
        "verdict_explanation": verdict_explanation,
        "node_scores": node_scores,
    }


# ============================================================
# GNN Candidate Region Structural Evaluator & Filter (GNN -> Heuristic)
# ============================================================

def evaluate_gnn_candidate_region(
    graph: nx.DiGraph,
    suspicious_seeds: List[str] | Set[str],
    region_nodes: List[str] | Set[str],
    gnn_probs: Optional[Dict[str, float]] = None,
    stealth_threshold: float = 0.40,
) -> Dict[str, Any]:
    """
    Evaluates a GNN-detected candidate region and suspicious seeds using structural heuristics.

    Acts as a verification filter:
    - Analyzes internal edge density among GNN seeds.
    - Evaluates stealthiness: ratio of internal connectivity to external boundary exits.
    - Audits presence of sequential trigger registers / counter loops.
    - Prunes likely false-alarm seeds that lack structural anomaly characteristics.
    """
    seeds = set(suspicious_seeds)
    region = set(region_nodes)
    if not seeds:
        return {
            "verdict": "FILTERED_OUT_CLEAN",
            "score": 0.0,
            "confirmed_seeds": [],
            "filtered_seeds": [],
            "seed_reduction_rate": 0.0,
            "metrics": {
                "seed_count": 0,
                "region_size": len(region),
                "internal_edges": 0,
                "sequential_connections": 0,
                "exit_ratio": 0.0,
            },
            "explanation": "No suspicious seeds provided by GNN.",
        }

    # 1. Internal connectivity among seeds
    seed_subgraph = graph.subgraph(seeds)
    internal_seed_edges = seed_subgraph.number_of_edges()

    # 2. Region-level internal vs boundary edges
    internal_region_edges = 0
    boundary_exits = set()
    for n in region:
        for succ in graph.successors(n):
            if succ in region:
                internal_region_edges += 1
            else:
                boundary_exits.add(n)

    exit_count = len(boundary_exits)
    exit_ratio = exit_count / max(1, len(region))

    # 3. Connections to sequential elements (DFFs)
    seq_nodes_in_region = [n for n in region if is_sequential(graph.nodes[n].get("gate_type", ""))]
    seed_to_seq_edges = 0
    for s in seeds:
        for nbr in list(graph.successors(s)) + list(graph.predecessors(s)):
            if nbr in seq_nodes_in_region:
                seed_to_seq_edges += 1

    # 4. Filter individual seeds
    confirmed_seeds = []
    filtered_seeds = []

    for s in seeds:
        in_deg = graph.in_degree(s)
        out_deg = graph.out_degree(s)
        nbrs = set(graph.predecessors(s)) | set(graph.successors(s))
        local_seed_nbrs = len(nbrs & seeds)

        # Anomaly scoring for seed:
        # High score if connected to other seeds, has trigger fanin, or connects to sequential gate
        has_internal_link = local_seed_nbrs > 0
        has_seq_link = any(nbr in seq_nodes_in_region for nbr in nbrs)
        is_trigger_like = in_deg >= 2 and out_deg <= 2

        if has_internal_link or has_seq_link or is_trigger_like:
            confirmed_seeds.append(s)
        else:
            # Isolated seed without structural anomaly
            filtered_seeds.append(s)

    # 5. Composite Heuristic Verification Score
    # Factor A: Seed clustering density (up to 0.40)
    density_score = min(0.40, (internal_seed_edges / max(1, len(seeds))) * 0.40)

    # Factor B: Sequential trigger coupling (up to 0.35)
    seq_score = 0.35 if len(seq_nodes_in_region) > 0 and seed_to_seq_edges > 0 else (0.15 if len(seq_nodes_in_region) > 0 else 0.0)

    # Factor C: Boundary stealthiness (up to 0.25)
    # Low exit ratio (concentrated payload) is more suspicious than high exit ratio (diffuse clock tree)
    stealth_score = 0.25 if (0.0 < exit_ratio <= 0.35 and len(region) >= 5) else 0.10

    composite_score = round(min(1.0, density_score + seq_score + stealth_score), 4)

    # Decision logic
    if composite_score >= stealth_threshold and len(confirmed_seeds) >= 1:
        verdict = "SUSPICIOUS_CONFIRMED"
    elif composite_score < 0.25 or len(confirmed_seeds) == 0:
        verdict = "FILTERED_OUT_CLEAN"
    else:
        verdict = "UNCERTAIN"

    reduction_rate = round(len(filtered_seeds) / max(1, len(seeds)), 4)

    explanation = (
        f"Heuristic verified GNN candidate region ({len(region)} gates, {len(seeds)} seeds). "
        f"Found {internal_seed_edges} internal seed edges, {len(seq_nodes_in_region)} sequential elements "
        f"({seed_to_seq_edges} seed-to-sequential links), and {exit_count} region exits. "
        f"Confirmed {len(confirmed_seeds)}/{len(seeds)} seeds (pruned {len(filtered_seeds)} false positives)."
    )

    return {
        "verdict": verdict,
        "score": composite_score,
        "threshold": stealth_threshold,
        "confirmed_seeds": confirmed_seeds,
        "filtered_seeds": filtered_seeds,
        "seed_reduction_rate": reduction_rate,
        "metrics": {
            "initial_seed_count": len(seeds),
            "confirmed_seed_count": len(confirmed_seeds),
            "filtered_seed_count": len(filtered_seeds),
            "region_size": len(region),
            "internal_seed_edges": internal_seed_edges,
            "internal_region_edges": internal_region_edges,
            "sequential_elements_in_region": len(seq_nodes_in_region),
            "seed_to_sequential_links": seed_to_seq_edges,
            "region_exits": exit_count,
            "exit_ratio": round(exit_ratio, 4),
        },
        "explanation": explanation,
    }


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Independent Heuristic Baseline Detector for Hardware Trojans."
    )
    parser.add_argument(
        "netlist",
        type=Path,
        help="Path to a Verilog netlist file.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Suspicious threshold (default: {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to save heuristic results.",
    )

    args = parser.parse_args()

    if not args.netlist.exists():
        print(f"Error: Netlist not found at {args.netlist}")
        sys.exit(1)

    print("=" * 60)
    print("INDEPENDENT HEURISTIC BASELINE DETECTOR")
    print("=" * 60)
    print("Netlist  :", args.netlist.resolve())
    print("Threshold:", args.threshold)

    # 1. Parse netlist
    print("\n[1/2] Parsing netlist into graph...")
    graph = parse_netlist(args.netlist)
    print(f"       Nodes = {graph.number_of_nodes()}, Edges = {graph.number_of_edges()}")

    # 2. Run heuristic detection
    print("\n[2/2] Running heuristic structural evaluation...")
    result = detect_trojan_heuristic(
        graph=graph,
        circuit_name=args.netlist.stem,
        threshold=args.threshold,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_file = args.output_dir / f"{args.netlist.stem}_heuristic.json"

    with out_file.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 60)
    print("HEURISTIC VERDICT COMPLETE")
    print("=" * 60)
    print("Decision   :", result["decision"])
    print("Score      :", result["score"])
    print("Threshold  :", result["threshold"])
    print("Anomalies  :", result["anomalous_node_count"], "nodes")
    print("Explanation:", result["verdict_explanation"])
    print("Saved to   :", out_file.resolve())


if __name__ == "__main__":
    main()
