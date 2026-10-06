"""
Heuristic Parameter Optimizer for Hardware Trojan Detection.

This module optimizes the heuristic weights w_i and decision threshold tau
to maximize Trojan detection performance while guaranteeing zero data leakage.

Methodology:
    TRAIN Set:      s13207, s1423
    VALIDATION Set: s15850 (used strictly for weight & threshold selection)
    TEST Set:       s35932 (strictly held out, never seen by optimizer)

Algorithms Implemented:
    1. Threshold Sweep (Validation-based threshold optimization)
    2. Random Search on Probability Simplex
    3. Grid Search across Prominent Feature Dimensions
    4. Differential Evolution / Genetic Algorithm (Global Search)
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import numpy as np
from scipy.optimize import differential_evolution
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    average_precision_score,
)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from parser import parse_netlist
from evidence import load_model, score_graph, build_evidence, get_device
from heuristic import (
    extract_heuristic_features,
    calculate_heuristic_score,
    DEFAULT_WEIGHTS,
)

# Active feature keys used in heuristic linear model (bounded in [0, 1])
OPTIMIZATION_FEATURES = [
    "max_gnn_score",
    "mean_gnn_score",
    "high_confidence_ratio",
    "confidence_margin",
    "connectivity",
    "sequential_ratio",
    "exit_ratio",
    "structural_density",
    "po_proximity",
    "trigger_concentration",
]

RESULTS_DIR = ROOT / "results" / "heuristic"


# ============================================================
# 1. Feature Extraction & Dataset Building
# ============================================================

def extract_circuit_sample(
    netlist_path: Path,
    model: Any,
    device: Any,
) -> Dict[str, Any]:
    """
    Parse a netlist, run GNN inference, build evidence, and extract
    heuristic features along with ground-truth label.
    """
    graph = parse_netlist(netlist_path)
    scores, _ = score_graph(model, graph, device)

    # Determine ground truth: is there any actual Trojan gate in the circuit?
    trojan_nodes_in_circuit = [
        n for n, d in graph.nodes(data=True) if d.get("is_trojan", False)
    ]
    is_trojan_circuit = len(trojan_nodes_in_circuit) > 0

    evidence = build_evidence(graph, scores)
    features = extract_heuristic_features(evidence)

    # Region-level ground truth: does the extracted region contain any Trojan gates?
    region_nodes = set(evidence.get("region", {}).get("nodes", []))
    if not region_nodes and "nodes" in evidence:
        region_nodes = {n["gate"] for n in evidence["nodes"]}

    is_trojan_region = any(
        graph.nodes[n].get("is_trojan", False)
        for n in region_nodes
        if n in graph
    )

    return {
        "netlist": netlist_path.name,
        "is_trojan_circuit": is_trojan_circuit,
        "is_trojan_region": is_trojan_region,
        "features": {k: float(features.get(k, 0.0)) for k in OPTIMIZATION_FEATURES},
    }


def build_split_dataset(
    families: List[str],
    max_circuits_per_family: int = 15,
    include_clean: bool = True,
    cache_path: Path | None = None,
    model: Any | None = None,
) -> List[Dict[str, Any]]:
    """
    Build a balanced dataset of heuristic feature vectors for given circuit families.
    Caches results to disk along with dataset-building inputs for validation.
    """
    device = get_device()
    if model is None:
        model = load_model()

    model_name = getattr(model, "__class__", type(model)).__name__
    expected_features = list(OPTIMIZATION_FEATURES)
    sorted_families = sorted(families)

    if cache_path and cache_path.exists():
        try:
            with open(cache_path, "r") as f:
                cached_data = json.load(f)

            if isinstance(cached_data, dict) and "metadata" in cached_data and "samples" in cached_data:
                meta = cached_data["metadata"]
                if (
                    meta.get("families") == sorted_families
                    and meta.get("max_circuits_per_family") == max_circuits_per_family
                    and meta.get("model") == model_name
                    and meta.get("optimization_features") == expected_features
                ):
                    return cached_data["samples"]
                else:
                    print(f"Cache inputs mismatch at {cache_path}. Rebuilding dataset...")
            else:
                print(f"Legacy cache format detected at {cache_path}. Rebuilding dataset...")
        except Exception as exc:
            print(f"Failed to read cache at {cache_path} ({exc}). Rebuilding dataset...")

    dataset: List[Dict[str, Any]] = []
    data_root = ROOT / "data" / "TRIT-TS"

    print(f"\nBuilding dataset for families: {families} ...")

    # 1. Add clean designs if applicable
    if include_clean:
        clean_dir = data_root / "original_designs"
        for fam in families:
            clean_file = clean_dir / f"{fam}scan.v"
            if clean_file.exists():
                try:
                    sample = extract_circuit_sample(clean_file, model, device)
                    dataset.append(sample)
                    print(f"  [Clean] {clean_file.name} -> Loaded")
                except Exception as exc:
                    print(f"  [Clean WARNING] {clean_file.name}: {exc}")

    # 2. Add infected circuits up to limit
    for fam in families:
        fam_dirs = sorted(data_root.glob(f"{fam}_T*"))
        loaded_count = 0
        for d in fam_dirs:
            if loaded_count >= max_circuits_per_family:
                break
            v_files = list(d.glob("*.v"))
            if not v_files:
                continue
            v_file = v_files[0]
            try:
                sample = extract_circuit_sample(v_file, model, device)
                dataset.append(sample)
                loaded_count += 1
            except Exception as exc:
                print(f"  [WARNING] {v_file.name}: {exc}")

        print(f"  [{fam}] Loaded {loaded_count} infected circuits.")

    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_payload = {
            "metadata": {
                "families": sorted_families,
                "max_circuits_per_family": max_circuits_per_family,
                "model": model_name,
                "optimization_features": expected_features,
            },
            "samples": dataset,
        }
        with open(cache_path, "w") as f:
            json.dump(cache_payload, f, indent=2)
        print(f"Dataset cached to: {cache_path}")

    return dataset


# ============================================================
# 2. Evaluation & Metric Utilities
# ============================================================

def evaluate_weights(
    weights: Dict[str, float],
    threshold: float,
    dataset: List[Dict[str, Any]],
    target_key: str = "is_trojan_circuit",
) -> Dict[str, float]:
    """
    Evaluate a specific weight configuration and threshold on a dataset.
    """
    y_true = np.array([1 if d[target_key] else 0 for d in dataset])
    y_scores = np.array([
        calculate_heuristic_score(d["features"], weights)
        for d in dataset
    ])
    y_pred = (y_scores >= threshold).astype(int)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    roc_auc = float("nan")
    pr_auc = float("nan")
    if len(np.unique(y_true)) > 1:
        try:
            roc_auc = float(roc_auc_score(y_true, y_scores))
            pr_auc = float(average_precision_score(y_true, y_scores))
        except Exception:
            pass

    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "threshold": threshold,
    }


def optimize_threshold(
    weights: Dict[str, float],
    dataset: List[Dict[str, Any]],
    target_key: str = "is_trojan_circuit",
    steps: int = 100,
) -> Tuple[float, float]:
    """
    Scan threshold tau in [0.05, 0.95] to find the value that maximizes F1.
    Returns: (best_threshold, best_f1)
    """
    y_true = np.array([1 if d[target_key] else 0 for d in dataset])
    y_scores = np.array([
        calculate_heuristic_score(d["features"], weights)
        for d in dataset
    ])

    best_tau = 0.50
    best_f1 = -1.0

    for tau in np.linspace(0.05, 0.95, steps):
        y_pred = (y_scores >= tau).astype(int)
        score = f1_score(y_true, y_pred, zero_division=0)
        if score > best_f1:
            best_f1 = float(score)
            best_tau = float(tau)

    return best_tau, best_f1


# ============================================================
# 3. Optimization Algorithms
# ============================================================

def random_search(
    val_dataset: List[Dict[str, Any]],
    n_iterations: int = 300,
    seed: int = 42,
) -> Tuple[Dict[str, float], float, float]:
    """
    Sample weight vectors uniformly on the probability simplex using
    Dirichlet distribution: w ~ Dir(1, 1, ..., 1).
    Optimizes threshold on validation data.
    """
    rng = np.random.default_rng(seed)
    n_features = len(OPTIMIZATION_FEATURES)

    best_weights: Dict[str, float] = {}
    best_tau = 0.50
    best_f1 = -1.0

    for _ in range(n_iterations):
        raw = rng.dirichlet(np.ones(n_features))
        candidate_weights = {
            feat: float(raw[i]) for i, feat in enumerate(OPTIMIZATION_FEATURES)
        }
        tau, f1 = optimize_threshold(candidate_weights, val_dataset)
        if f1 > best_f1:
            best_f1 = f1
            best_tau = tau
            best_weights = candidate_weights

    return best_weights, best_tau, best_f1


def grid_search(
    val_dataset: List[Dict[str, Any]],
) -> Tuple[Dict[str, float], float, float]:
    """
    Perform a discrete grid search focusing on key feature groupings:
    (GNN strength, Structural connectivity, Sequential trigger prominence).
    """
    best_weights: Dict[str, float] = {}
    best_tau = 0.50
    best_f1 = -1.0

    levels = [0.05, 0.15, 0.30]

    for w_max in levels:
        for w_conn in levels:
            for w_seq in levels:
                for w_margin in levels:
                    w_dict = {
                        "max_gnn_score": w_max,
                        "mean_gnn_score": 0.10,
                        "high_confidence_ratio": 0.10,
                        "confidence_margin": w_margin,
                        "connectivity": w_conn,
                        "sequential_ratio": w_seq,
                        "exit_ratio": 0.10,
                        "structural_density": 0.05,
                        "po_proximity": 0.05,
                        "trigger_concentration": 0.05,
                    }
                    total = sum(w_dict.values())
                    norm_weights = {k: v / total for k, v in w_dict.items()}

                    tau, f1 = optimize_threshold(norm_weights, val_dataset)
                    if f1 > best_f1:
                        best_f1 = f1
                        best_tau = tau
                        best_weights = norm_weights

    return best_weights, best_tau, best_f1


def differential_evolution_search(
    val_dataset: List[Dict[str, Any]],
    maxiter: int = 40,
    seed: int = 42,
) -> Tuple[Dict[str, float], float, float]:
    """
    Global population-based genetic/differential evolution optimizer.
    Finds continuous weight vector w that maximizes validation F1.
    """
    n_features = len(OPTIMIZATION_FEATURES)
    bounds = [(0.01, 1.0)] * n_features

    def objective(w_vec):
        total = np.sum(w_vec)
        if total <= 0:
            return 1.0
        norm_w = w_vec / total
        weights = {
            OPTIMIZATION_FEATURES[i]: float(norm_w[i])
            for i in range(n_features)
        }
        _, f1 = optimize_threshold(weights, val_dataset)
        # Minimize negative F1
        return -f1

    res = differential_evolution(
        objective,
        bounds,
        maxiter=maxiter,
        popsize=10,
        mutation=(0.5, 1.0),
        recombination=0.7,
        seed=seed,
        polish=False,
    )

    opt_vec = res.x / np.sum(res.x)
    best_weights = {
        OPTIMIZATION_FEATURES[i]: float(opt_vec[i])
        for i in range(n_features)
    }
    best_tau, best_f1 = optimize_threshold(best_weights, val_dataset)

    return best_weights, best_tau, best_f1


# ============================================================
# 4. Master Optimization Workflow
# ============================================================

def run_heuristic_optimization(
    max_train_per_family: int = 15,
    max_val_per_family: int = 15,
) -> Dict[str, Any]:
    """
    Full Phase 2 Pipeline:
    1. Build/load train dataset (s13207, s1423).
    2. Build/load validation dataset (s15850).
    3. Run Baseline, Grid Search, Random Search, and Differential Evolution.
    4. Select optimal parameters w*, tau*.
    5. Save results to results/heuristic/optimized_weights.json.
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    train_cache = RESULTS_DIR / "features_train.json"
    val_cache = RESULTS_DIR / "features_val.json"

    print("==================================================")
    print("  PHASE 2: HEURISTIC OPTIMIZATION ENGINE")
    print("==================================================")

    # 1. Prepare Datasets (Strict zero-leakage split)
    train_dataset = build_split_dataset(
        families=["s13207", "s1423"],
        max_circuits_per_family=max_train_per_family,
        include_clean=True,
        cache_path=train_cache,
    )

    val_dataset = build_split_dataset(
        families=["s15850"],
        max_circuits_per_family=max_val_per_family,
        include_clean=True,
        cache_path=val_cache,
    )

    print(f"\nTrain samples : {len(train_dataset)}")
    print(f"Val samples   : {len(val_dataset)}")

    # 2. Evaluate Baseline Default Weights
    print("\n[1/4] Evaluating Baseline Default Weights...")
    base_weights = {k: DEFAULT_WEIGHTS.get(k, 0.10) for k in OPTIMIZATION_FEATURES}
    total = sum(base_weights.values())
    base_weights = {k: v / total for k, v in base_weights.items()}
    base_tau, _ = optimize_threshold(base_weights, val_dataset)
    base_val_metrics = evaluate_weights(base_weights, base_tau, val_dataset)
    base_train_metrics = evaluate_weights(base_weights, base_tau, train_dataset)

    # 3. Method: Random Search
    print("\n[2/4] Running Random Search (300 iterations)...")
    t0 = time.time()
    rnd_weights, rnd_tau, _ = random_search(val_dataset, n_iterations=300)
    rnd_val_metrics = evaluate_weights(rnd_weights, rnd_tau, val_dataset)
    rnd_time = time.time() - t0

    # 4. Method: Grid Search
    print("\n[3/4] Running Grid Search...")
    t0 = time.time()
    grid_weights, grid_tau, _ = grid_search(val_dataset)
    grid_val_metrics = evaluate_weights(grid_weights, grid_tau, val_dataset)
    grid_time = time.time() - t0

    # 5. Method: Differential Evolution
    print("\n[4/4] Running Differential Evolution Global Search...")
    t0 = time.time()
    de_weights, de_tau, _ = differential_evolution_search(val_dataset, maxiter=25)
    de_val_metrics = evaluate_weights(de_weights, de_tau, val_dataset)
    de_time = time.time() - t0

    # Compile Comparison Table
    methods = [
        ("Baseline (Manual)", base_weights, base_tau, base_val_metrics, 0.0),
        ("Random Search", rnd_weights, rnd_tau, rnd_val_metrics, rnd_time),
        ("Grid Search", grid_weights, grid_tau, grid_val_metrics, grid_time),
        ("Differential Evolution", de_weights, de_tau, de_val_metrics, de_time),
    ]

    print("\n==================================================")
    print("  OPTIMIZATION METHODS COMPARISON (Selection Set: s15850 - In-Sample)")
    print("==================================================")
    print(f"{'Method':25s} | {'Tau':6s} | {'Sel-Precision':13s} | {'Sel-Recall':10s} | {'Sel-F1':8s} | {'Sel-PR-AUC':10s} | {'Time (s)':8s}")
    print("-" * 95)

    best_method_name = ""
    best_opt_weights = base_weights
    best_opt_tau = base_tau
    highest_f1 = -1.0

    comparison_records = []

    for name, w, tau, metrics, el_time in methods:
        f1 = metrics["f1"]
        print(
            f"{name:25s} | {tau:6.3f} | {metrics['precision']:13.4f} | "
            f"{metrics['recall']:10.4f} | {f1:8.4f} | {metrics['pr_auc']:10.4f} | {el_time:8.2f}"
        )
        comparison_records.append({
            "method": name,
            "tau": round(tau, 4),
            "metric_scope": "selection_set_in_sample",
            "selection_precision": round(metrics["precision"], 4),
            "selection_recall": round(metrics["recall"], 4),
            "selection_f1": round(f1, 4),
            "selection_pr_auc": round(metrics["pr_auc"], 4) if not math.isnan(metrics["pr_auc"]) else None,
            "selection_roc_auc": round(metrics["roc_auc"], 4) if not math.isnan(metrics["roc_auc"]) else None,
            "elapsed_seconds": round(el_time, 2),
        })

        if f1 > highest_f1:
            highest_f1 = f1
            best_method_name = name
            best_opt_weights = w
            best_opt_tau = tau

    print("-" * 85)
    print(f"Selected Optimal Method: {best_method_name} (F1: {highest_f1:.4f})")

    # Final evaluation on Train set using selected weights
    final_train_metrics = evaluate_weights(best_opt_weights, best_opt_tau, train_dataset)
    final_val_metrics = evaluate_weights(best_opt_weights, best_opt_tau, val_dataset)

    # Feature Importance ranking
    sorted_features = sorted(
        best_opt_weights.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    output_payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "best_method": best_method_name,
        "optimal_threshold": round(best_opt_tau, 4),
        "optimal_weights": {k: round(v, 6) for k, v in best_opt_weights.items()},
        "feature_importance_ranking": [
            {"feature": k, "weight": round(v, 6)} for k, v in sorted_features
        ],
        "validation_metrics": {
            k: (round(v, 4) if isinstance(v, float) and not math.isnan(v) else v)
            for k, v in final_val_metrics.items()
        },
        "training_metrics": {
            k: (round(v, 4) if isinstance(v, float) and not math.isnan(v) else v)
            for k, v in final_train_metrics.items()
        },
        "comparison_table": comparison_records,
    }

    output_path = RESULTS_DIR / "optimized_weights.json"
    with open(output_path, "w") as f:
        json.dump(output_payload, f, indent=2)

    print(f"\nOptimal weights successfully saved to: {output_path}")
    return output_payload


if __name__ == "__main__":
    run_heuristic_optimization()
