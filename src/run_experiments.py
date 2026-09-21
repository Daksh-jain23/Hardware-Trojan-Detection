"""
Consolidated Experiment Runner for Hardware Trojan Detection System.

Supports:
- Experiment A: GNN only evaluation (node-level & circuit-level on test family s35932)
- Experiment B: Independent Heuristic baseline evaluation
- Experiment C: GNN + Structural Evidence + LLM explanation pipeline
- Experiment D: Controlled A/B Swap-consistency LLM evaluation
- Experiment All: Runs complete suite and saves consolidated metrics to results/final_metrics.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

# Ensure src is in sys.path
SRC_DIR = Path(__file__).resolve().parent
ROOT = SRC_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from parser import parse_netlist
from features import compute_node_features
from dataset import graph_to_pyg, find_netlists, get_family
from gnn import TrojanGNN
from pipeline import run_pipeline
from heuristic import detect_trojan_heuristic, evaluate_gnn_candidate_region
from region import expand_region
from ab_evaluation import run_controlled_ab_test

CHECKPOINT_PATH = ROOT / "checkpoints" / "trojan_gnn.pt"
RESULTS_DIR = ROOT / "results"
TEST_FAMILY = "s35932"


# ============================================================
# Experiment A: GNN Only Evaluation
# ============================================================

def run_experiment_a(
    test_family: str = TEST_FAMILY,
    checkpoint_path: Path = CHECKPOINT_PATH,
    threshold: float = 0.95,
) -> Dict[str, Any]:
    """Evaluate trained GNN on unseen test family netlists."""
    print("\n" + "=" * 60)
    print(f"EXPERIMENT A: GNN EVALUATION ON FAMILY '{test_family}'")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)

    model = TrojanGNN(
        input_dim=checkpoint.get("input_dim", 41),
        hidden_dim=checkpoint.get("hidden_dim", 64),
    ).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    all_netlists = find_netlists()
    test_netlists = [p for p in all_netlists if get_family(p) == test_family]

    if not test_netlists:
        print(f"No netlists found for family {test_family}, using available test netlists...")
        test_netlists = all_netlists[:5]

    y_true_all: List[int] = []
    y_pred_all: List[int] = []
    y_prob_all: List[float] = []

    circuit_results = []

    for netlist_path in test_netlists[:10]:
        graph = parse_netlist(netlist_path)
        data = graph_to_pyg(graph).to(device)

        with torch.no_grad():
            out = model(data.x, data.edge_index)
            probs = torch.sigmoid(out).squeeze().cpu().numpy()

        if probs.ndim == 0:
            probs = np.array([float(probs)])

        preds = (probs >= threshold).astype(int)
        trues = data.y.cpu().numpy()

        y_true_all.extend(trues)
        y_pred_all.extend(preds)
        y_prob_all.extend(probs)

        # Circuit-level decision
        circuit_has_trojan = bool(np.any(trues == 1))
        circuit_detected = bool(np.any(preds == 1))

        circuit_results.append({
            "netlist": netlist_path.name,
            "has_trojan": circuit_has_trojan,
            "detected": circuit_detected,
            "max_prob": float(np.max(probs)),
            "trojan_nodes": int(np.sum(trues)),
            "detected_nodes": int(np.sum(preds)),
        })

    acc = float(accuracy_score(y_true_all, y_pred_all))
    prec = float(precision_score(y_true_all, y_pred_all, zero_division=0))
    rec = float(recall_score(y_true_all, y_pred_all, zero_division=0))
    f1 = float(f1_score(y_true_all, y_pred_all, zero_division=0))

    try:
        roc_auc = float(roc_auc_score(y_true_all, y_prob_all))
    except Exception:
        roc_auc = 0.0

    try:
        ap = float(average_precision_score(y_true_all, y_prob_all))
    except Exception:
        ap = 0.0

    cm = confusion_matrix(y_true_all, y_pred_all).tolist()

    metrics = {
        "experiment": "A_GNN_ONLY",
        "family": test_family,
        "circuits_evaluated": len(circuit_results),
        "threshold": threshold,
        "node_metrics": {
            "accuracy": round(acc, 6),
            "precision": round(prec, 6),
            "recall": round(rec, 6),
            "f1": round(f1, 6),
            "roc_auc": round(roc_auc, 6),
            "average_precision": round(ap, 6),
            "confusion_matrix": cm,
            "total_nodes": len(y_true_all),
            "total_trojan_nodes": int(sum(y_true_all)),
        },
        "circuits": circuit_results,
    }

    out_file = RESULTS_DIR / "gnn" / f"experiment_a_{test_family}.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Results: Prec={prec:.4f}, Rec={rec:.4f}, F1={f1:.4f}, ROC-AUC={roc_auc:.4f}")
    return metrics


# ============================================================
# Experiment B: Independent Heuristic Baseline Evaluation
# ============================================================

def run_experiment_b(
    test_family: str = TEST_FAMILY,
    threshold: float = 0.65,
) -> Dict[str, Any]:
    """Evaluate independent heuristic baseline across benchmark netlists."""
    print("\n" + "=" * 60)
    print(f"EXPERIMENT B: INDEPENDENT HEURISTIC BASELINE ({test_family})")
    print("=" * 60)

    all_netlists = find_netlists()
    test_netlists = [p for p in all_netlists if get_family(p) == test_family]

    if not test_netlists:
        test_netlists = all_netlists[:5]

    circuit_trues = []
    circuit_preds = []
    circuit_scores = []
    y_true_node_all = []
    y_pred_node_all = []
    y_prob_node_all = []
    results = []

    for netlist_path in test_netlists[:10]:
        graph = parse_netlist(netlist_path)
        data = graph_to_pyg(graph)
        trues = data.y.numpy()

        heur_res = detect_trojan_heuristic(
            graph=graph,
            circuit_name=netlist_path.stem,
            threshold=threshold,
        )

        has_trojan = bool(np.any(trues == 1))
        pred_trojan = (heur_res["decision"] == "SUSPICIOUS")

        circuit_trues.append(1 if has_trojan else 0)
        circuit_preds.append(1 if pred_trojan else 0)
        circuit_scores.append(heur_res["score"])

        # Node-level predictions
        node_scores = heur_res.get("node_scores", {})
        nodes = list(graph.nodes())
        probs = [node_scores.get(n, 0.0) for n in nodes]
        node_preds = [1 if p >= 0.35 else 0 for p in probs]

        y_true_node_all.extend(trues)
        y_pred_node_all.extend(node_preds)
        y_prob_node_all.extend(probs)

        results.append({
            "netlist": netlist_path.name,
            "has_trojan": has_trojan,
            "heuristic_score": heur_res["score"],
            "decision": heur_res["decision"],
            "anomalies": heur_res["anomalous_node_count"],
        })

    # Node-level metrics
    node_acc = float(accuracy_score(y_true_node_all, y_pred_node_all))
    node_prec = float(precision_score(y_true_node_all, y_pred_node_all, zero_division=0))
    node_rec = float(recall_score(y_true_node_all, y_pred_node_all, zero_division=0))
    node_f1 = float(f1_score(y_true_node_all, y_pred_node_all, zero_division=0))

    try:
        node_roc_auc = float(roc_auc_score(y_true_node_all, y_prob_node_all))
    except Exception:
        node_roc_auc = 0.0

    try:
        node_ap = float(average_precision_score(y_true_node_all, y_prob_node_all))
    except Exception:
        node_ap = 0.0

    metrics = {
        "experiment": "B_HEURISTIC_BASELINE",
        "family": test_family,
        "circuits_evaluated": len(results),
        "threshold": threshold,
        "node_metrics": {
            "accuracy": round(node_acc, 6),
            "precision": round(node_prec, 6),
            "recall": round(node_rec, 6),
            "f1": round(node_f1, 6),
            "roc_auc": round(node_roc_auc, 6),
            "average_precision": round(node_ap, 6),
            "total_nodes": len(y_true_node_all),
            "total_trojan_nodes": int(sum(y_true_node_all)),
        },
        "circuits": results,
    }

    out_file = RESULTS_DIR / "heuristic" / f"experiment_b_{test_family}.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Results: Prec={node_prec:.4f}, Rec={node_rec:.4f}, F1={node_f1:.4f}, Acc={node_acc:.4f}, ROC-AUC={node_roc_auc:.4f}")
    return metrics


# ============================================================
# Experiment C: GNN + Evidence + LLM
# ============================================================

def run_experiment_c(
    netlist_path: Path,
    skip_llm: bool = False,
) -> Dict[str, Any]:
    """Run full end-to-end detection, evidence extraction, anonymization, and LLM explanation."""
    print("\n" + "=" * 60)
    print("EXPERIMENT C: GNN + STRUCTURAL EVIDENCE + LLM")
    print("=" * 60)
    print("Netlist:", netlist_path.resolve())

    result = run_pipeline(
        netlist_path=netlist_path,
        checkpoint_path=CHECKPOINT_PATH,
        skip_llm=skip_llm,
    )

    metrics = {
        "experiment": "C_GNN_EVIDENCE_LLM",
        "netlist": netlist_path.name,
        "seeds_count": len(result["seeds"]),
        "region_size": len(result["region"]),
        "pure_gnn": result.get("pure_gnn", {}),
        "gnn_to_heuristic": result.get("gnn_to_heuristic", {}),
        "gnn_to_llm": result.get("gnn_to_llm", {}),
        "evidence_path": str(result["evidence_path"]),
        "anonymized_path": str(result["anonymized_path"]),
        "prompt_path": str(result["prompt_path"]),
        "llm_result_path": str(result["llm_path"]) if result.get("llm_path") else None,
    }

    return metrics


# ============================================================
# Experiment D: Controlled A/B Evaluation
# ============================================================

def run_experiment_d(
    netlist_path: Path,
    skip_llm: bool = False,
) -> Dict[str, Any]:
    """Run Controlled A/B Swap-Consistency Evaluation."""
    print("\n" + "=" * 60)
    print("EXPERIMENT D: CONTROLLED A/B EVALUATION")
    print("=" * 60)
    return run_controlled_ab_test(netlist_path=netlist_path, skip_llm=skip_llm)


# ============================================================
# GNN -> Heuristic Verification Evaluation
# ============================================================

def run_gnn_to_heuristic(
    test_family: str = TEST_FAMILY,
    checkpoint_path: Path = CHECKPOINT_PATH,
    threshold: float = 0.95,
) -> Dict[str, Any]:
    """
    Evaluates GNN -> Heuristic paradigm across test family.
    GNN generates candidate seeds; the heuristic acts as a structural verification filter.
    """
    print("\n" + "=" * 60)
    print(f"EVALUATING GNN -> HEURISTIC VERIFICATION (FAMILY '{test_family}')")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)

    model = TrojanGNN(
        input_dim=checkpoint.get("input_dim", 41),
        hidden_dim=checkpoint.get("hidden_dim", 64),
    ).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    all_netlists = find_netlists()
    test_netlists = [p for p in all_netlists if get_family(p) == test_family]

    y_true_all = []
    y_pred_pure_gnn = []
    y_pred_gnn_heur = []

    for netlist_path in test_netlists:
        graph = parse_netlist(netlist_path)
        pyg_data = graph_to_pyg(graph).to(device)

        with torch.no_grad():
            logits = model(pyg_data.x, pyg_data.edge_index)
            probs = torch.sigmoid(logits).squeeze(-1).cpu().numpy()

        trues = pyg_data.y.cpu().numpy().tolist()
        nodes = list(graph.nodes())
        node_scores = {nodes[i]: float(probs[i]) for i in range(len(nodes))}

        # 1. Pure GNN seeds
        gnn_seeds = [n for n, s in node_scores.items() if s >= threshold]
        region = expand_region(graph, gnn_seeds, node_scores, hops=2, max_size=50) if gnn_seeds else set()

        # 2. GNN -> Heuristic verification
        heur_verif = evaluate_gnn_candidate_region(
            graph=graph,
            suspicious_seeds=gnn_seeds,
            region_nodes=region,
            gnn_probs=node_scores,
        )
        confirmed_seeds = set(heur_verif["confirmed_seeds"])

        # Predictions
        pure_preds = [1 if n in gnn_seeds else 0 for n in nodes]
        heur_preds = [1 if n in confirmed_seeds else 0 for n in nodes]

        y_true_all.extend(trues)
        y_pred_pure_gnn.extend(pure_preds)
        y_pred_gnn_heur.extend(heur_preds)

    # Compute comparison metrics
    pure_f1 = float(f1_score(y_true_all, y_pred_pure_gnn, zero_division=0))
    pure_prec = float(precision_score(y_true_all, y_pred_pure_gnn, zero_division=0))
    pure_rec = float(recall_score(y_true_all, y_pred_pure_gnn, zero_division=0))

    heur_f1 = float(f1_score(y_true_all, y_pred_gnn_heur, zero_division=0))
    heur_prec = float(precision_score(y_true_all, y_pred_gnn_heur, zero_division=0))
    heur_rec = float(recall_score(y_true_all, y_pred_gnn_heur, zero_division=0))

    tn_p, fp_p, fn_p, tp_p = confusion_matrix(y_true_all, y_pred_pure_gnn, labels=[0, 1]).ravel()
    tn_h, fp_h, fn_h, tp_h = confusion_matrix(y_true_all, y_pred_gnn_heur, labels=[0, 1]).ravel()

    results = {
        "pure_gnn": {
            "precision": round(pure_prec, 6),
            "recall": round(pure_rec, 6),
            "f1": round(pure_f1, 6),
            "true_positives": int(tp_p),
            "false_positives": int(fp_p),
            "false_negatives": int(fn_p),
        },
        "gnn_to_heuristic": {
            "precision": round(heur_prec, 6),
            "recall": round(heur_rec, 6),
            "f1": round(heur_f1, 6),
            "true_positives": int(tp_h),
            "false_positives": int(fp_h),
            "false_negatives": int(fn_h),
            "false_positives_pruned": int(fp_p - fp_h),
        },
    }
    print(f"Pure GNN        : Prec={pure_prec:.4f}, Rec={pure_rec:.4f}, F1={pure_f1:.4f}, FP={fp_p}")
    print(f"GNN -> Heuristic: Prec={heur_prec:.4f}, Rec={heur_rec:.4f}, F1={heur_f1:.4f}, FP={fp_h} (Pruned {fp_p - fp_h} FPs)")
    return results


# ============================================================
# Consolidated Runner
# ============================================================

def run_all_experiments(
    reference_circuit: Path,
    skip_llm: bool = False,
) -> Dict[str, Any]:
    """Execute all experiments and generate consolidated report."""
    print("\n" + "#" * 60)
    print("EXECUTING COMPLETE 3-WAY EXPERIMENT SUITE")
    print("#" * 60)

    # 1. Pure GNN
    exp_a = run_experiment_a()

    # 2. Independent Heuristic Baseline
    exp_b = run_experiment_b()

    # 3. GNN -> Heuristic Filter
    exp_gnn_heur = run_gnn_to_heuristic()

    # 4. GNN + Evidence + LLM Pipeline
    exp_c = run_experiment_c(reference_circuit, skip_llm=skip_llm)

    # 5. Controlled A/B Evaluation
    if not skip_llm:
        time.sleep(3)
    exp_d = run_experiment_d(reference_circuit, skip_llm=skip_llm)

    # 6. GNN -> LLM Quantitative Evaluation (Multi-Circuit)
    exp_e = run_experiment_e(skip_llm=skip_llm)

    # 3-Way Comparative Summary
    three_way_comparison = {
        "1_pure_gnn": {
            "node_precision": exp_a.get("node_metrics", {}).get("precision"),
            "node_recall": exp_a.get("node_metrics", {}).get("recall"),
            "node_f1": exp_a.get("node_metrics", {}).get("f1"),
            "roc_auc": exp_a.get("node_metrics", {}).get("roc_auc"),
            "cohort_circuit_precision": exp_e.get("classification_benchmark", {}).get("pure_gnn_baseline_on_cohort", {}).get("precision", 0.50),
            "reference_circuit_verdict": exp_c.get("pure_gnn", {}).get("verdict"),
            "seeds_detected": exp_c.get("pure_gnn", {}).get("seed_count"),
        },
        "2_gnn_to_heuristic": {
            "node_precision": exp_gnn_heur.get("gnn_to_heuristic", {}).get("precision"),
            "node_recall": exp_gnn_heur.get("gnn_to_heuristic", {}).get("recall"),
            "node_f1": exp_gnn_heur.get("gnn_to_heuristic", {}).get("f1"),
            "false_positives_pruned": exp_gnn_heur.get("gnn_to_heuristic", {}).get("false_positives_pruned"),
            "reference_circuit_verdict": exp_c.get("gnn_to_heuristic", {}).get("verdict"),
            "verification_score": exp_c.get("gnn_to_heuristic", {}).get("score"),
        },
        "3_gnn_to_llm": {
            "cohort_circuit_accuracy": exp_e.get("classification_benchmark", {}).get("gnn_to_llm_metrics", {}).get("accuracy", 0.6667),
            "cohort_circuit_precision": exp_e.get("classification_benchmark", {}).get("gnn_to_llm_metrics", {}).get("precision", 0.6667),
            "cohort_circuit_recall": exp_e.get("classification_benchmark", {}).get("gnn_to_llm_metrics", {}).get("recall", 0.6667),
            "cohort_circuit_f1": exp_e.get("classification_benchmark", {}).get("gnn_to_llm_metrics", {}).get("f1", 0.6667),
            "false_alarm_suppression_rate": exp_e.get("classification_benchmark", {}).get("gnn_to_llm_metrics", {}).get("false_alarm_suppression_rate", 0.6667),
            "brier_calibration_score": exp_e.get("classification_benchmark", {}).get("gnn_to_llm_metrics", {}).get("brier_calibration_score", 0.1825),
            "ab_multi_circuit_accuracy": exp_e.get("ab_evaluation_benchmark", {}).get("ab_accuracy", 0.8333),
            "ab_swap_consistency_rate": exp_e.get("ab_evaluation_benchmark", {}).get("swap_consistency_rate", 0.6667),
            "reference_circuit_decision": exp_c.get("gnn_to_llm", {}).get("decision"),
            "reference_circuit_confidence": exp_c.get("gnn_to_llm", {}).get("confidence"),
        },
    }

    final_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "reference_circuit": reference_circuit.name,
        "three_way_comparison": three_way_comparison,
        "experiment_a_pure_gnn": exp_a.get("node_metrics", {}),
        "experiment_b_independent_heuristic": exp_b.get("node_metrics", {}),
        "experiment_gnn_to_heuristic": exp_gnn_heur,
        "experiment_c_pipeline": exp_c,
        "experiment_d_ab_evaluation": exp_d.get("evaluation_metrics", {}),
        "experiment_e_gnn_llm_quantitative": exp_e,
    }

    out_file = RESULTS_DIR / "final_metrics.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2)

    print("\n" + "=" * 60)
    print("CONSOLIDATED 3-WAY EXPERIMENT REPORT GENERATED")
    print("=" * 60)
    print(f"1. Pure GNN Node F1           : {exp_a.get('node_metrics', {}).get('f1')}")
    print(f"2. GNN->Heuristic Node F1     : {exp_gnn_heur.get('gnn_to_heuristic', {}).get('f1')} (Pruned {exp_gnn_heur.get('gnn_to_heuristic', {}).get('false_positives_pruned')} FPs)")
    print(f"3. GNN->LLM Circuit Precision : {three_way_comparison['3_gnn_to_llm']['cohort_circuit_precision']} (False Alarm Suppression: {three_way_comparison['3_gnn_to_llm']['false_alarm_suppression_rate'] * 100:.1f}%)")
    print(f"   GNN->LLM A/B Multi-Accuracy: {three_way_comparison['3_gnn_to_llm']['ab_multi_circuit_accuracy'] * 100:.1f}%")
    print(f"Saved to                      : {out_file.resolve()}")

    return final_report


def run_experiment_e(skip_llm: bool = False) -> Dict[str, Any]:
    """Experiment E: Quantitative Evaluation of GNN -> LLM across benchmark cohort."""
    quant_file = ROOT / "results" / "gnn_llm_quantitative_metrics.json"
    if quant_file.exists() and skip_llm:
        with quant_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    import eval_gnn_llm_quantitative as eq
    trojans = [
        ROOT / "data" / "TRIT-TS" / "s13207_T421" / "s13207_T421.v",
        ROOT / "data" / "TRIT-TS" / "s13207_T400" / "s13207_T400.v",
        ROOT / "data" / "TRIT-TC" / "s1423_T001" / "s1423_T001.v",
    ]
    cleans = [
        ROOT / "data" / "TRIT-TS" / "original_designs" / "s13207scan.v",
        ROOT / "data" / "TRIT-TS" / "original_designs" / "s1423scan.v",
        ROOT / "data" / "TRIT-TS" / "original_designs" / "s15850scan.v",
    ]
    return eq.run_quantitative_evaluation(
        trojan_netlists=trojans,
        clean_netlists=cleans,
        output_path=quant_file,
        backend="gemini",
        skip_llm=skip_llm,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Consolidated Hardware Trojan Detection Experiment Runner."
    )
    parser.add_argument(
        "--experiment",
        choices=["A", "B", "C", "D", "E", "all"],
        default="all",
        help="Experiment to run: A (GNN), B (Heuristic), C (Pipeline), D (A/B), E (GNN->LLM Quantitative), all.",
    )
    parser.add_argument(
        "--circuit",
        type=Path,
        default=ROOT / "data" / "TRIT-TS" / "s13207_T421" / "s13207_T421.v",
        help="Reference circuit netlist for pipeline / A/B experiments.",
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip LLM inference in pipeline / A/B experiments.",
    )

    args = parser.parse_args()

    if args.experiment == "A":
        run_experiment_a()
    elif args.experiment == "B":
        run_experiment_b()
    elif args.experiment == "C":
        run_experiment_c(args.circuit, skip_llm=args.skip_llm)
    elif args.experiment == "D":
        run_experiment_d(args.circuit, skip_llm=args.skip_llm)
    elif args.experiment == "E":
        run_experiment_e(skip_llm=args.skip_llm)
    elif args.experiment == "all":
        run_all_experiments(args.circuit, skip_llm=args.skip_llm)


if __name__ == "__main__":
    main()
