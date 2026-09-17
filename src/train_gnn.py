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

from __future__ import annotations

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

from dataset import build_node_level_dataset, graph_to_pyg


# ============================================================
# CONFIGURATION
# ============================================================

TRAIN_FAMILIES = [
    "s13207",
    "s1423",
]

VAL_FAMILIES = [
    "s15850",
]

TEST_FAMILIES = [
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
# DATASET SPLIT
# ============================================================

def prepare_dataset():
    """
    Build the complete dataset and split it by family.

    IMPORTANT:
    We use membership checks:

        sample.family in TEST_FAMILIES

    rather than:

        sample.family == TEST_FAMILIES

    because TEST_FAMILIES is a list.
    """

    samples = build_node_level_dataset()

    train_samples = []
    val_samples = []
    test_samples = []

    for sample in samples:

        if sample.family in TEST_FAMILIES:

            test_samples.append(sample)

        elif sample.family in VAL_FAMILIES:

            val_samples.append(sample)

        elif sample.family in TRAIN_FAMILIES:

            train_samples.append(sample)

        else:

            print(
                f"[WARNING] Ignoring unknown family: "
                f"{sample.family}"
            )

    # --------------------------------------------------------
    # Safety checks
    # --------------------------------------------------------

    if len(train_samples) == 0:
        raise RuntimeError(
            "Training set is empty."
        )

    if len(val_samples) == 0:
        raise RuntimeError(
            "Validation set is empty."
        )

    if len(test_samples) == 0:
        raise RuntimeError(
            "Test set is empty."
        )

    # --------------------------------------------------------
    # Verify there is no family leakage
    # --------------------------------------------------------

    train_families = {
        x.family for x in train_samples
    }

    val_families = {
        x.family for x in val_samples
    }

    test_families = {
        x.family for x in test_samples
    }

    if train_families & val_families:
        raise RuntimeError(
            "Family leakage between training and validation."
        )

    if train_families & test_families:
        raise RuntimeError(
            "Family leakage between training and test."
        )

    if val_families & test_families:
        raise RuntimeError(
            "Family leakage between validation and test."
        )

    # --------------------------------------------------------
    # Print split
    # --------------------------------------------------------

    print()
    print("========== DATASET SPLIT ==========")

    print(
        "Training families   :",
        TRAIN_FAMILIES,
    )

    print(
        "Validation families :",
        VAL_FAMILIES,
    )

    print(
        "Test families       :",
        TEST_FAMILIES,
    )

    print()

    print(
        "Training graphs    :",
        len(train_samples),
    )

    print(
        "Validation graphs  :",
        len(val_samples),
    )

    print(
        "Test graphs        :",
        len(test_samples),
    )

    return (
        train_samples,
        val_samples,
        test_samples,
    )


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
    ) = prepare_dataset()

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
        hidden_dim=HIDDEN_DIM,
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
        lr=LEARNING_RATE,
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

    CHECKPOINT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for epoch in range(
        1,
        EPOCHS + 1,
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
                        HIDDEN_DIM,

                    "epoch":
                        epoch,

                    "val_f1":
                        val_f1,

                    "threshold":
                        val_threshold,
                },
                CHECKPOINT_PATH,
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
        CHECKPOINT_PATH,
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
        CHECKPOINT_PATH,
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

    print(
        "Test families:",
        TEST_FAMILIES,
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