"""
Evaluation utilities for Hardware Trojan Detection.

Evaluates the trained GNN on complete netlist graphs.

Important:
    - Evaluation is node-level.
    - Each Verilog netlist remains a separate graph.
    - Metrics are computed globally over all nodes.
    - Supports family-level evaluation to measure generalization.
    - Uses the same 41-dimensional feature representation as training.

Usage:

    python src/evaluation.py

or:

    python src/evaluation.py data/TRIT-TS/s35932_T400/s35932_T400.v
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

import torch
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    average_precision_score,
    roc_auc_score,
)

# Make src imports work when executed directly.
SRC_DIR = Path(__file__).resolve().parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from dataset import (
    build_node_level_dataset,
    graph_to_pyg,
    get_family,
)

from gnn import TrojanGNN


# ============================================================
# Configuration
# ============================================================

CHECKPOINT = (
    SRC_DIR.parent
    / "checkpoints"
    / "trojan_gnn.pt"
)

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

# This should match the threshold selected during training.
DEFAULT_THRESHOLD = 0.95


# ============================================================
# Model loading
# ============================================================

def load_model(
    checkpoint_path: Path = CHECKPOINT,
    input_dim: int = 41,
):
    """
    Load the trained TrojanGNN.

    The architecture must match the architecture used during training.
    """

    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Checkpoint not found:\n{checkpoint_path}"
        )

    model = TrojanGNN(
        input_dim=input_dim
    ).to(DEVICE)

    checkpoint = torch.load(
        checkpoint_path,
        map_location=DEVICE,
        weights_only=False,
    )

    # --------------------------------------------------------
    # Support several checkpoint formats.
    # --------------------------------------------------------

    if isinstance(checkpoint, dict):

        if "model_state_dict" in checkpoint:

            state_dict = checkpoint["model_state_dict"]

        elif "state_dict" in checkpoint:

            state_dict = checkpoint["state_dict"]

        else:

            # Could itself be a state_dict.
            state_dict = checkpoint

    else:

        raise RuntimeError(
            "Unsupported checkpoint format."
        )

    model.load_state_dict(
        state_dict,
        strict=True,
    )

    model.eval()

    return model, checkpoint


# ============================================================
# Prediction
# ============================================================

@torch.no_grad()
def predict_graph(
    model,
    data,
):
    """
    Generate Trojan probabilities for every node.
    """

    data = data.to(DEVICE)

    logits = model(
        data.x,
        data.edge_index,
    )

    # Trojan probability.
    probabilities = torch.sigmoid(
        logits
    )

    return (
        probabilities.detach().cpu(),
        data.y.detach().cpu(),
    )


# ============================================================
# Metrics
# ============================================================

def calculate_metrics(
    y_true: torch.Tensor,
    probabilities: torch.Tensor,
    threshold: float,
):
    """
    Calculate classification metrics.
    """

    y_true = y_true.numpy()
    probabilities = probabilities.numpy()

    y_pred = (
        probabilities >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1],
    ).ravel()

    metrics = {
        "accuracy": accuracy_score(
            y_true,
            y_pred,
        ),

        "precision": precision_score(
            y_true,
            y_pred,
            zero_division=0,
        ),

        "recall": recall_score(
            y_true,
            y_pred,
            zero_division=0,
        ),

        "f1": f1_score(
            y_true,
            y_pred,
            zero_division=0,
        ),

        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }

    # --------------------------------------------------------
    # ROC-AUC
    # --------------------------------------------------------

    if len(set(y_true)) == 2:

        metrics["roc_auc"] = roc_auc_score(
            y_true,
            probabilities,
        )

        metrics["average_precision"] = (
            average_precision_score(
                y_true,
                probabilities,
            )
        )

    else:

        metrics["roc_auc"] = float("nan")
        metrics["average_precision"] = float("nan")

    return metrics


# ============================================================
# Evaluate samples
# ============================================================

@torch.no_grad()
def evaluate_samples(
    model,
    samples,
    threshold: float = DEFAULT_THRESHOLD,
):
    """
    Evaluate a collection of complete netlist graphs.

    Predictions from all graphs are concatenated before calculating
    global metrics.
    """

    all_probabilities = []
    all_labels = []

    graph_results = []

    for index, sample in enumerate(samples):

        data = graph_to_pyg(
            sample.graph
        )

        probabilities, labels = predict_graph(
            model,
            data,
        )

        all_probabilities.append(
            probabilities
        )

        all_labels.append(
            labels
        )

        metrics = calculate_metrics(
            labels,
            probabilities,
            threshold,
        )

        graph_results.append(
            {
                "family": sample.family,
                "source": sample.source,
                "nodes": len(labels),
                "trojan_nodes": int(labels.sum()),
                **metrics,
            }
        )

    if not all_labels:

        raise RuntimeError(
            "No graphs were available for evaluation."
        )

    y_true = torch.cat(
        all_labels
    )

    probabilities = torch.cat(
        all_probabilities
    )

    global_metrics = calculate_metrics(
        y_true,
        probabilities,
        threshold,
    )

    return (
        global_metrics,
        graph_results,
        y_true,
        probabilities,
    )


# ============================================================
# Print metrics
# ============================================================

def print_metrics(
    metrics,
    title="EVALUATION RESULT",
):
    """
    Pretty-print evaluation metrics.
    """

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)

    print(
        f"Accuracy          : "
        f"{metrics['accuracy']:.4f}"
    )

    print(
        f"Precision         : "
        f"{metrics['precision']:.4f}"
    )

    print(
        f"Recall            : "
        f"{metrics['recall']:.4f}"
    )

    print(
        f"F1                : "
        f"{metrics['f1']:.4f}"
    )

    print(
        f"ROC-AUC           : "
        f"{metrics['roc_auc']:.4f}"
    )

    print(
        f"Average Precision : "
        f"{metrics['average_precision']:.4f}"
    )

    print()
    print("Confusion Matrix")
    print("----------------")

    print(
        f"True Negatives  : {metrics['tn']}"
    )

    print(
        f"False Positives : {metrics['fp']}"
    )

    print(
        f"False Negatives : {metrics['fn']}"
    )

    print(
        f"True Positives  : {metrics['tp']}"
    )


# ============================================================
# Per-family evaluation
# ============================================================

def evaluate_by_family(
    model,
    samples,
    threshold,
):
    """
    Evaluate every circuit family separately.

    This is important because the model should generalize to
    unseen circuits rather than simply memorizing one family.
    """

    families = sorted(
        set(
            sample.family
            for sample in samples
        )
    )

    print()
    print("=" * 60)
    print("PER-FAMILY EVALUATION")
    print("=" * 60)

    for family in families:

        family_samples = [
            sample
            for sample in samples
            if sample.family == family
        ]

        metrics, _, _, _ = evaluate_samples(
            model,
            family_samples,
            threshold,
        )

        print()
        print(
            f"Family: {family}"
        )

        print(
            f"  Graphs    : "
            f"{len(family_samples)}"
        )

        print(
            f"  Precision : "
            f"{metrics['precision']:.4f}"
        )

        print(
            f"  Recall    : "
            f"{metrics['recall']:.4f}"
        )

        print(
            f"  F1        : "
            f"{metrics['f1']:.4f}"
        )

        print(
            f"  ROC-AUC   : "
            f"{metrics['roc_auc']:.4f}"
        )


# ============================================================
# Top suspicious nodes
# ============================================================

def print_top_predictions(
    model,
    sample,
    top_k=20,
):
    """
    Show the highest-scoring nodes for one circuit.

    This connects evaluation with region.py and explainability.
    """

    data = graph_to_pyg(
        sample.graph
    )

    probabilities, labels = predict_graph(
        model,
        data,
    )

    # Recreate feature/node ordering.
    from features import compute_node_features

    _, nodes = compute_node_features(
        sample.graph
    )

    ranked = sorted(
        zip(
            nodes,
            probabilities.tolist(),
            labels.tolist(),
        ),
        key=lambda x: x[1],
        reverse=True,
    )

    print()
    print("=" * 60)
    print("TOP SUSPICIOUS NODES")
    print("=" * 60)

    print(
        f"Family: {sample.family}"
    )

    print(
        f"File  : {sample.source}"
    )

    print()

    for i, (node, score, label) in enumerate(
        ranked[:top_k],
        start=1,
    ):

        node_type = sample.graph.nodes[node].get(
            "type",
            sample.graph.nodes[node].get(
                "gate_type",
                "unknown",
            ),
        )

        print(
            f"{i:2d}. "
            f"{node:35s} "
            f"{str(node_type):12s} "
            f"score={score:.4f} "
            f"label={label}"
        )


# ============================================================
# Main
# ============================================================

def main():

    print(
        "========== HARDWARE TROJAN EVALUATION =========="
    )

    print(
        f"Device     : {DEVICE}"
    )

    if torch.cuda.is_available():

        print(
            f"GPU        : "
            f"{torch.cuda.get_device_name(0)}"
        )

    print(
        f"Checkpoint : {CHECKPOINT}"
    )

    print(
        f"Threshold  : {DEFAULT_THRESHOLD}"
    )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    print()
    print("Loading trained model...")

    model, checkpoint = load_model(
        CHECKPOINT,
        input_dim=41,
    )

    print()
    print(model)

    # --------------------------------------------------------
    # Determine checkpoint threshold if available.
    # --------------------------------------------------------

    threshold = DEFAULT_THRESHOLD

    if isinstance(checkpoint, dict):

        saved_threshold = checkpoint.get(
            "threshold"
        )

        if saved_threshold is not None:

            threshold = float(
                saved_threshold
            )

    print(
        f"\nEvaluation threshold: {threshold:.4f}"
    )

    # --------------------------------------------------------
    # Specific file evaluation
    # --------------------------------------------------------

    if len(sys.argv) > 1:

        netlist_path = Path(
            sys.argv[1]
        )

        if not netlist_path.exists():

            raise FileNotFoundError(
                f"Netlist not found: "
                f"{netlist_path}"
            )

        print()
        print(
            "Evaluating single netlist:"
        )

        print(
            netlist_path
        )

        from parser import parse_netlist

        graph = parse_netlist(
            netlist_path
        )

        from dataset import GraphSample

        sample = GraphSample(
            graph=graph,
            family=get_family(
                netlist_path
            ),
            source=str(
                netlist_path
            ),
        )

        metrics, _, _, _ = evaluate_samples(
            model,
            [sample],
            threshold,
        )

        print_metrics(
            metrics,
            "SINGLE NETLIST RESULT",
        )

        print_top_predictions(
            model,
            sample,
            top_k=20,
        )

        return

    # --------------------------------------------------------
    # Full dataset evaluation
    # --------------------------------------------------------

    print()
    print("Loading complete dataset...")

    samples = build_node_level_dataset()

    print()
    print(
        f"Graphs available: "
        f"{len(samples)}"
    )

    # --------------------------------------------------------
    # Global evaluation
    # --------------------------------------------------------

    metrics, graph_results, _, _ = (
        evaluate_samples(
            model,
            samples,
            threshold,
        )
    )

    print_metrics(
        metrics,
        "FULL DATASET RESULT",
    )

    # --------------------------------------------------------
    # Family evaluation
    # --------------------------------------------------------

    evaluate_by_family(
        model,
        samples,
        threshold,
    )

    # --------------------------------------------------------
    # Worst-performing circuits
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("LOWEST-F1 CIRCUITS")
    print("=" * 60)

    ranked_graphs = sorted(
        graph_results,
        key=lambda x: x["f1"],
    )

    for result in ranked_graphs[:10]:

        print(
            f"{result['family']:10s} "
            f"{Path(result['source']).parent.name:25s} "
            f"F1={result['f1']:.4f} "
            f"P={result['precision']:.4f} "
            f"R={result['recall']:.4f}"
        )


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    main()