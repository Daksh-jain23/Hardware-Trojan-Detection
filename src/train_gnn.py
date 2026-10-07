"""
Train a GAT-based Hardware Trojan detector.

Pipeline:

    Verilog
       ↓
    NetworkX graph
       ↓
    41 node features
       ↓
    PyTorch Geometric graph
       ↓
    GAT
       ↓
    Trojan probability for every node
       ↓
    Validation threshold selection
       ↓
    Unseen test-family evaluation

Dataset split is by circuit family to avoid node-level leakage.

TRAIN:
    s13207
    s1423

VALIDATION:
    s15850

TEST:
    s35932
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from torch_geometric.nn import GATConv


# ============================================================
# PATH SETUP
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dataset import (
    build_node_level_dataset,
    graph_to_pyg,
    split_dataset,
    GraphSample,
)


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_TRAIN_FAMILIES = [
    "s13207",
    "s1423",
]

DEFAULT_VAL_FAMILIES = [
    "s15850",
]

DEFAULT_TEST_FAMILIES = [
    "s35932",
]

EPOCHS = 100

LEARNING_RATE = 0.001

WEIGHT_DECAY = 1e-4

HIDDEN_DIM = 64

HEADS_1 = 4
HEADS_2 = 2

DROPOUT = 0.2

CHECKPOINT_DIR = ROOT / "checkpoints"

CHECKPOINT_PATH = (
    CHECKPOINT_DIR / "trojan_gnn.pt"
)

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# DATASET PREPARATION
# ============================================================

def prepare_dataset(
    data_roots=None,
    files=None,
    train_families=None,
    val_families=None,
    test_families=None,
    split_by="family",
    train_ratio=0.70,
    val_ratio=0.15,
    test_ratio=0.15,
    max_samples=None,
    seed=42,
):
    """
    Build the dataset from files/roots and split into Train, Validation, Test.
    """
    # If no explicit families or files given, check default family splits
    has_custom_split = (
        train_families is not None
        or val_families is not None
        or test_families is not None
        or files is not None
        or split_by == "file"
    )

    if not has_custom_split and data_roots is None:
        train_families = DEFAULT_TRAIN_FAMILIES
        val_families = DEFAULT_VAL_FAMILIES
        test_families = DEFAULT_TEST_FAMILIES

    all_filter_families = None
    if train_families or val_families or test_families:
        all_filter_families = list(set((train_families or []) + (val_families or []) + (test_families or [])))

    samples = build_node_level_dataset(
        families=all_filter_families,
        data_roots=data_roots,
        files=files,
        max_samples=max_samples,
    )

    train_samples, val_samples, test_samples = split_dataset(
        samples=samples,
        split_by=split_by,
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        test_ratio=test_ratio,
        train_families=train_families,
        val_families=val_families,
        test_families=test_families,
        seed=seed,
    )

    if len(train_samples) == 0:
        raise RuntimeError("Training set is empty.")
    if len(val_samples) == 0:
        print("[WARNING] Validation set is empty, using 1 sample from train.")
        val_samples = [train_samples[0]]
    if len(test_samples) == 0:
        print("[WARNING] Test set is empty, using validation set as test.")
        test_samples = list(val_samples)

    return train_samples, val_samples, test_samples


# ============================================================
# MODEL
# ============================================================

class TrojanGNN(nn.Module):
    """
    Two-layer Graph Attention Network.

    Input:
        41 node features

    Output:
        One logit for every node.

    The logit is converted to a probability using sigmoid.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = HIDDEN_DIM,
    ):
        super().__init__()

        # ----------------------------------------------------
        # First GAT layer
        #
        # input_dim
        #      ↓
        # 64 × 4 attention heads
        #      ↓
        # 256 features
        # ----------------------------------------------------

        self.gat1 = GATConv(
            in_channels=input_dim,
            out_channels=hidden_dim,
            heads=HEADS_1,
            dropout=DROPOUT,
        )

        # ----------------------------------------------------
        # Second GAT layer
        #
        # 256
        #  ↓
        # 64 × 2 heads
        #  ↓
        # 128
        # ----------------------------------------------------

        self.gat2 = GATConv(
            in_channels=hidden_dim * HEADS_1,
            out_channels=hidden_dim,
            heads=HEADS_2,
            dropout=DROPOUT,
        )

        # ----------------------------------------------------
        # Node classifier
        #
        # 128 → 1
        # ----------------------------------------------------

        self.classifier = nn.Linear(
            hidden_dim * HEADS_2,
            1,
        )

    def forward(
        self,
        x,
        edge_index,
    ):
        # First graph attention
        x = self.gat1(
            x,
            edge_index,
        )

        x = F.elu(x)

        # Second graph attention
        x = self.gat2(
            x,
            edge_index,
        )

        x = F.elu(x)

        # Trojan score for each node
        x = self.classifier(x)

        return x.squeeze(-1)


# ============================================================
# NETWORKX → PYTORCH GEOMETRIC
# ============================================================

def convert_samples(samples):
    """
    Convert every complete circuit into a PyG Data object.
    """

    data_list = []

    for sample in samples:

        data = graph_to_pyg(
            sample.graph
        )

        # Keep metadata for later analysis.
        data.family = sample.family
        data.source = sample.source

        data_list.append(data)

    return data_list


# ============================================================
# CLASS BALANCE
# ============================================================

def calculate_class_weight(data_list):
    """
    Calculate positive-class weight for BCEWithLogitsLoss.

    Hardware Trojan datasets are heavily imbalanced:

        normal >> Trojan

    Therefore false negatives need stronger weighting.
    """

    normal = 0
    trojan = 0

    for data in data_list:

        normal += int(
            (data.y == 0).sum().item()
        )

        trojan += int(
            (data.y == 1).sum().item()
        )

    if trojan == 0:
        raise RuntimeError(
            "Training data contains zero Trojan nodes."
        )

    positive_weight = (
        normal / trojan
    )

    print()
    print("========== CLASS BALANCE ==========")

    print(
        "Normal nodes :",
        normal,
    )

    print(
        "Trojan nodes :",
        trojan,
    )

    print(
        "Positive weight:",
        positive_weight,
    )

    return torch.tensor(
        positive_weight,
        dtype=torch.float32,
        device=DEVICE,
    )


# ============================================================
# TRAIN ONE EPOCH
# ============================================================

def train_one_epoch(
    model,
    data_list,
    optimizer,
    criterion,
):
    """
    Train on every graph in the training set.
    """

    model.train()

    total_loss = 0.0

    for data in data_list:

        data = data.to(DEVICE)

        optimizer.zero_grad()

        logits = model(
            data.x,
            data.edge_index,
        )

        loss = criterion(
            logits,
            data.y.float(),
        )

        loss.backward()

        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(data_list)


# ============================================================
# COLLECT PROBABILITIES
# ============================================================

@torch.no_grad()
def collect_probabilities(
    model,
    data_list,
):
    """
    Run the model and return:

        probabilities
        labels

    We deliberately DO NOT threshold here.

    This allows validation to determine the best threshold.
    """

    model.eval()

    all_probabilities = []
    all_labels = []

    for data in data_list:

        data = data.to(DEVICE)

        logits = model(
            data.x,
            data.edge_index,
        )

        probabilities = torch.sigmoid(
            logits
        )

        all_probabilities.extend(
            probabilities.cpu().numpy()
        )

        all_labels.extend(
            data.y.cpu().numpy()
        )

    return (
        np.asarray(
            all_probabilities,
            dtype=np.float32,
        ),
        np.asarray(
            all_labels,
            dtype=np.int64,
        ),
    )


# ============================================================
# FIND BEST THRESHOLD
# ============================================================

def find_best_threshold(
    model,
    data_list,
):
    """
    Find the probability threshold producing
    the highest F1 on the VALIDATION set.

    The TEST set is never used here.
    """

    probabilities, labels = (
        collect_probabilities(
            model,
            data_list,
        )
    )

    best_threshold = 0.5
    best_f1 = -1.0

    # Search from 0.05 to 0.95.
    thresholds = np.arange(
        0.05,
        0.951,
        0.01,
    )

    for threshold in thresholds:

        predictions = (
            probabilities >= threshold
        ).astype(np.int64)

        f1 = f1_score(
            labels,
            predictions,
            zero_division=0,
        )

        if f1 > best_f1:

            best_f1 = f1
            best_threshold = float(
                threshold
            )

    return (
        best_threshold,
        best_f1,
    )


# ============================================================
# EVALUATION
# ============================================================

@torch.no_grad()
def evaluate(
    model,
    data_list,
    threshold=0.5,
):
    """
    Evaluate node-level predictions.
    """

    probabilities, labels = (
        collect_probabilities(
            model,
            data_list,
        )
    )

    predictions = (
        probabilities >= threshold
    ).astype(np.int64)

    precision = precision_score(
        labels,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        labels,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        labels,
        predictions,
        zero_division=0,
    )

    return (
        precision,
        recall,
        f1,
    )


# ============================================================
# CONFUSION MATRIX
# ============================================================

@torch.no_grad()
def print_confusion_matrix(
    model,
    data_list,
    threshold,
):
    """
    Print TP / TN / FP / FN.
    """

    probabilities, labels = (
        collect_probabilities(
            model,
            data_list,
        )
    )

    predictions = (
        probabilities >= threshold
    ).astype(np.int64)

    tn, fp, fn, tp = confusion_matrix(
        labels,
        predictions,
        labels=[0, 1],
    ).ravel()

    print()
    print("========== CONFUSION MATRIX ==========")

    print(
        "True Negatives  :",
        tn,
    )

    print(
        "False Positives :",
        fp,
    )

    print(
        "False Negatives :",
        fn,
    )

    print(
        "True Positives  :",
        tp,
    )


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Train GAT-based Hardware Trojan detector."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        nargs="+",
        default=None,
        help="Path or list of paths to dataset roots (e.g. data/TRIT-TS, data/TRIT-TC).",
    )
    parser.add_argument(
        "--files",
        type=Path,
        nargs="+",
        default=None,
        help="Explicit list of Verilog (.v) files to train on.",
    )
    parser.add_argument(
        "--train-families",
        nargs="+",
        default=None,
        help="Circuit families for training (e.g. s13207 s1423 or c2670).",
    )
    parser.add_argument(
        "--val-families",
        nargs="+",
        default=None,
        help="Circuit families for validation (e.g. s15850 or c3540).",
    )
    parser.add_argument(
        "--test-families",
        nargs="+",
        default=None,
        help="Circuit families for test (e.g. s35932 or c6288).",
    )
    parser.add_argument(
        "--split-by",
        choices=["family", "file"],
        default="family",
        help="How to split the dataset ('family' to prevent circuit leakage, or 'file' for random split).",
    )
    parser.add_argument(
        "--split-ratio",
        type=float,
        nargs=3,
        default=[0.70, 0.15, 0.15],
        help="Train, validation, test ratio (default: 0.70 0.15 0.15).",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=EPOCHS,
        help=f"Number of training epochs (default: {EPOCHS}).",
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=LEARNING_RATE,
        help=f"Learning rate (default: {LEARNING_RATE}).",
    )
    parser.add_argument(
        "--hidden-dim",
        type=int,
        default=HIDDEN_DIM,
        help=f"Hidden dimension (default: {HIDDEN_DIM}).",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=CHECKPOINT_PATH,
        help=f"Path to save model checkpoint (default: {CHECKPOINT_PATH}).",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Maximum number of netlists to load.",
    )

    args = parser.parse_args()

    print(
        "========== HARDWARE TROJAN GNN =========="
    )

    print(
        "Device:",
        DEVICE,
    )

    if torch.cuda.is_available():

        print(
            "GPU:",
            torch.cuda.get_device_name(0),
        )

    else:

        print(
            "GPU: CPU"
        )

    # --------------------------------------------------------
    # LOAD DATASET
    # --------------------------------------------------------

    print(
        "Loading node-level dataset..."
    )

    (
        train_samples,
        val_samples,
        test_samples,
    ) = prepare_dataset(
        data_roots=args.data_dir,
        files=args.files,
        train_families=args.train_families,
        val_families=args.val_families,
        test_families=args.test_families,
        split_by=args.split_by,
        train_ratio=args.split_ratio[0],
        val_ratio=args.split_ratio[1],
        test_ratio=args.split_ratio[2],
        max_samples=args.max_samples,
    )

    print(f"Training graphs    : {len(train_samples)}")
    print(f"Validation graphs  : {len(val_samples)}")
    print(f"Test graphs        : {len(test_samples)}")

    # --------------------------------------------------------
    # CONVERT GRAPHS
    # --------------------------------------------------------

    train_data = convert_samples(
        train_samples
    )

    val_data = convert_samples(
        val_samples
    )

    test_data = convert_samples(
        test_samples
    )

    # --------------------------------------------------------
    # FEATURE INFORMATION
    # --------------------------------------------------------

    input_dim = train_data[0].x.shape[1]

    print()
    print("========== GRAPH INFORMATION ==========")

    print(
        "Input feature dimension:",
        input_dim,
    )

    # --------------------------------------------------------
    # CREATE MODEL
    # --------------------------------------------------------

    model = TrojanGNN(
        input_dim=input_dim,
        hidden_dim=args.hidden_dim,
    ).to(DEVICE)

    print()
    print(model)

    # --------------------------------------------------------
    # CLASS WEIGHT
    # --------------------------------------------------------

    positive_weight = (
        calculate_class_weight(
            train_data
        )
    )

    criterion = nn.BCEWithLogitsLoss(
        pos_weight=positive_weight
    )

    # --------------------------------------------------------
    # OPTIMIZER
    # --------------------------------------------------------

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=args.lr,
        weight_decay=WEIGHT_DECAY,
    )

    # --------------------------------------------------------
    # TRAINING
    # --------------------------------------------------------

    print()
    print("========== TRAINING ==========")

    best_f1 = -1.0

    best_threshold = 0.5

    best_epoch = 0

    args.checkpoint.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    for epoch in range(
        1,
        args.epochs + 1,
    ):

        loss = train_one_epoch(
            model,
            train_data,
            optimizer,
            criterion,
        )

        # ----------------------------------------------------
        # Find threshold ONLY using validation data.
        # ----------------------------------------------------

        val_threshold, val_f1 = (
            find_best_threshold(
                model,
                val_data,
            )
        )

        val_precision, val_recall, _ = (
            evaluate(
                model,
                val_data,
                threshold=val_threshold,
            )
        )

        # ----------------------------------------------------
        # Save best model.
        # ----------------------------------------------------

        if val_f1 > best_f1:

            best_f1 = val_f1

            best_threshold = (
                val_threshold
            )

            best_epoch = epoch

            torch.save(
                {
                    "model_state_dict":
                        model.state_dict(),

                    "input_dim":
                        input_dim,

                    "hidden_dim":
                        args.hidden_dim,

                    "epoch":
                        epoch,

                    "val_f1":
                        val_f1,

                    "threshold":
                        val_threshold,
                },
                args.checkpoint,
            )

        # ----------------------------------------------------
        # Print progress.
        # ----------------------------------------------------

        if (
            epoch == 1
            or epoch % 10 == 0
        ):

            print(
                f"Epoch {epoch:03d} | "
                f"loss={loss:.4f} | "
                f"threshold={val_threshold:.2f} | "
                f"val_precision={val_precision:.4f} | "
                f"val_recall={val_recall:.4f} | "
                f"val_f1={val_f1:.4f}"
            )

    # --------------------------------------------------------
    # LOAD BEST MODEL
    # --------------------------------------------------------

    checkpoint = torch.load(
        args.checkpoint,
        map_location=DEVICE,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    best_threshold = float(
        checkpoint["threshold"]
    )


    print()
    print(
        "========== BEST MODEL =========="
    )

    print(
        "Best epoch:",
        checkpoint["epoch"],
    )

    print(
        "Best validation threshold:",
        best_threshold,
    )

    print(
        "Best validation F1:",
        checkpoint["val_f1"],
    )

    print(
        "Checkpoint:",
        args.checkpoint,
    )

    # --------------------------------------------------------
    # FINAL VALIDATION RESULT
    # --------------------------------------------------------

    val_precision, val_recall, val_f1 = (
        evaluate(
            model,
            val_data,
            threshold=best_threshold,
        )
    )

    print()
    print(
        "========== FINAL VALIDATION =========="
    )

    print(
        f"Threshold   : {best_threshold:.2f}"
    )

    print(
        f"Precision   : {val_precision:.4f}"
    )

    print(
        f"Recall      : {val_recall:.4f}"
    )

    print(
        f"F1          : {val_f1:.4f}"
    )

    # --------------------------------------------------------
    # FINAL TEST
    #
    # IMPORTANT:
    # We use the threshold selected from validation.
    #
    # We DO NOT search for a better threshold on test.
    # --------------------------------------------------------

    test_precision, test_recall, test_f1 = (
        evaluate(
            model,
            test_data,
            threshold=best_threshold,
        )
    )

    print()
    print(
        "========== TEST RESULT =========="
    )

    test_family_names = sorted(set(s.family for s in test_samples))
    print(
        "Test families:",
        test_family_names,
    )

    print(
        f"Threshold   : {best_threshold:.2f}"
    )

    print(
        f"Precision   : {test_precision:.4f}"
    )

    print(
        f"Recall      : {test_recall:.4f}"
    )

    print(
        f"F1          : {test_f1:.4f}"
    )

    # --------------------------------------------------------
    # CONFUSION MATRIX
    # --------------------------------------------------------

    print_confusion_matrix(
        model,
        test_data,
        best_threshold,
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()