"""
Train a GAT-based Hardware Trojan detector.

Pipeline:
    Verilog -> NetworkX graph -> 53 node features -> PyTorch Geometric graph
    -> 3-Layer Residual GAT -> Node-level Trojan probabilities
    -> Validation threshold tuning -> Unseen test evaluation
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv

# Path setup
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dataset import (
    GraphSample,
    build_node_level_dataset,
    graph_to_pyg,
    split_dataset,
)

# Default split and training configuration
DEFAULT_TRAIN_FAMILIES = ["s13207", "s1423"]
DEFAULT_VAL_FAMILIES = ["s15850"]
DEFAULT_TEST_FAMILIES = ["s35932"]

EPOCHS = 100
LEARNING_RATE = 0.001
WEIGHT_DECAY = 1e-4
HIDDEN_DIM = 64
HEADS_1 = 4
HEADS_2 = 2
DROPOUT = 0.2

CHECKPOINT_DIR = ROOT / "checkpoints"
CHECKPOINT_PATH = CHECKPOINT_DIR / "trojan_gnn.pt"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


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
    """Build the dataset and split into train, val, and test subsets."""
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


class TrojanGNN(nn.Module):
    """
    3-Layer Residual Graph Attention Network for Hardware Trojan localization.

    Layer 1: GATConv(input_dim -> hidden_dim, heads=4) = 256 + LayerNorm
    Layer 2: GATConv(256 -> hidden_dim, heads=4) = 256 + Residual(h1) + LayerNorm
    Layer 3: GATConv(256 -> hidden_dim, heads=2) = 128 + Residual Projection + LayerNorm
    Classifier: Linear(128 -> 1)
    """
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = HIDDEN_DIM,
        dropout: float = DROPOUT,
    ):
        super().__init__()
        self.dropout = dropout

        # Layer 1
        self.gat1 = GATConv(
            in_channels=input_dim,
            out_channels=hidden_dim,
            heads=HEADS_1,
            concat=True,
            dropout=dropout,
        )
        self.norm1 = nn.LayerNorm(hidden_dim * HEADS_1)

        # Layer 2 with direct residual
        self.gat2 = GATConv(
            in_channels=hidden_dim * HEADS_1,
            out_channels=hidden_dim,
            heads=HEADS_1,
            concat=True,
            dropout=dropout,
        )
        self.norm2 = nn.LayerNorm(hidden_dim * HEADS_1)

        # Layer 3 with projected residual
        self.gat3 = GATConv(
            in_channels=hidden_dim * HEADS_1,
            out_channels=hidden_dim,
            heads=HEADS_2,
            concat=True,
            dropout=dropout,
        )
        self.norm3 = nn.LayerNorm(hidden_dim * HEADS_2)

        # Projection from 256 to 128
        self.res_proj = nn.Linear(hidden_dim * HEADS_1, hidden_dim * HEADS_2)

        # Final linear classifier
        self.classifier = nn.Linear(hidden_dim * HEADS_2, 1)

    def forward(self, x, edge_index):
        # Layer 1
        h1 = self.gat1(x, edge_index)
        h1 = F.elu(h1)
        h1 = self.norm1(h1)
        h1 = F.dropout(h1, p=self.dropout, training=self.training)

        # Layer 2
        h2 = self.gat2(h1, edge_index)
        h2 = F.elu(h2 + h1)
        h2 = self.norm2(h2)
        h2 = F.dropout(h2, p=self.dropout, training=self.training)

        # Layer 3
        h3 = self.gat3(h2, edge_index)
        h3 = F.elu(h3 + self.res_proj(h2))
        h3 = self.norm3(h3)
        h3 = F.dropout(h3, p=self.dropout, training=self.training)

        logits = self.classifier(h3)
        return logits.squeeze(-1)


def convert_samples(samples):
    """Convert every GraphSample into a PyG Data object."""
    data_list = []
    for sample in samples:
        data = graph_to_pyg(sample.graph)
        data.family = sample.family
        data.source = sample.source
        data_list.append(data)
    return data_list


class FocalLoss(nn.Module):
    """
    Focal Loss with calibrated positive weight.
    Down-weights easy negatives and focuses on hard ambiguous gates near the Trojan boundary.
    """
    def __init__(
        self,
        alpha: float = 0.5,
        gamma: float = 2.0,
        pos_weight: float | None = None,
    ):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.pos_weight = pos_weight

    def forward(self, logits, targets):
        pos_w = (
            torch.tensor([self.pos_weight], device=logits.device, dtype=torch.float32)
            if self.pos_weight is not None
            else None
        )
        bce = F.binary_cross_entropy_with_logits(
            logits,
            targets,
            pos_weight=pos_w,
            reduction="none",
        )
        probs = torch.sigmoid(logits)
        p_t = targets * probs + (1.0 - targets) * (1.0 - probs)
        alpha_t = targets * self.alpha + (1.0 - targets) * (1.0 - self.alpha)
        focal_factor = alpha_t * torch.pow((1.0 - p_t).clamp(min=1e-6), self.gamma)
        return (focal_factor * bce).mean()


def calculate_class_weight(data_list):
    """Calculate calibrated positive-class weight for class-imbalanced training."""
    normal = 0
    trojan = 0
    for data in data_list:
        normal += int((data.y == 0).sum().item())
        trojan += int((data.y == 1).sum().item())

    if trojan == 0:
        raise RuntimeError("Training data contains zero Trojan nodes.")

    raw_ratio = normal / trojan
    damped_weight = min(25.0, max(5.0, math.sqrt(raw_ratio) * 1.5))

    print("\n========== CLASS BALANCE ==========")
    print(f"Normal nodes     : {normal}")
    print(f"Trojan nodes     : {trojan}")
    print(f"Raw imbalance    : {raw_ratio:.2f}")
    print(f"Calibrated weight: {damped_weight:.2f}")

    return torch.tensor(damped_weight, dtype=torch.float32, device=DEVICE)


def refine_predictions_with_topology(
    edge_index_tensor,
    raw_preds,
    probas,
    threshold=0.5,
):
    """
    Apply graph topological priors:
    1. Prune isolated false alarms (0 positive neighbors within 2 hops).
    2. Fill Trojan cluster gaps (normal gates with >= 2 Trojan neighbors).
    """
    if edge_index_tensor is None or edge_index_tensor.numel() == 0:
        return raw_preds

    num_nodes = len(raw_preds)
    if num_nodes == 0 or np.sum(raw_preds) == 0:
        return raw_preds

    ei = edge_index_tensor.cpu().numpy()
    adj = sp.csr_matrix(
        (np.ones(ei.shape[1], dtype=np.float32), (ei[0], ei[1])),
        shape=(num_nodes, num_nodes),
    )
    adj = (adj + adj.T).tocsr()
    adj.data[:] = 1.0

    preds = np.copy(raw_preds)
    pos_nodes = np.where(preds == 1)[0]

    if len(pos_nodes) > 0:
        pos_vec = np.zeros(num_nodes, dtype=np.float32)
        pos_vec[pos_nodes] = 1.0

        hop1_pos = np.asarray(adj @ pos_vec).flatten()
        hop2_pos = np.asarray((adj @ adj) @ pos_vec).flatten()

        # 1. Prune isolated false alarms
        for n in pos_nodes:
            if hop1_pos[n] == 0 and hop2_pos[n] == 0 and probas[n] < 0.90:
                preds[n] = 0

        # 2. Fill cluster gaps
        neg_nodes = np.where(preds == 0)[0]
        for n in neg_nodes:
            if hop1_pos[n] >= 2 and probas[n] >= max(0.20, threshold - 0.20):
                preds[n] = 1

    return preds


def train_one_epoch(model, data_list, optimizer, criterion):
    """Train the model across all graphs in the training set for one epoch."""
    model.train()
    total_loss = 0.0

    for data in data_list:
        data = data.to(DEVICE)
        optimizer.zero_grad()
        logits = model(data.x, data.edge_index)
        loss = criterion(logits, data.y.float())
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
        optimizer.step()
        total_loss += loss.item()

    return total_loss / len(data_list)


@torch.no_grad()
def collect_probabilities(model, data_list):
    """Collect model probabilities and ground truth labels across all graphs."""
    model.eval()
    all_probabilities = []
    all_labels = []

    for data in data_list:
        data = data.to(DEVICE)
        logits = model(data.x, data.edge_index)
        probabilities = torch.sigmoid(logits)
        all_probabilities.extend(probabilities.cpu().numpy())
        all_labels.extend(data.y.cpu().numpy())

    return (
        np.asarray(all_probabilities, dtype=np.float32),
        np.asarray(all_labels, dtype=np.int64),
    )


def find_best_threshold(model, data_list):
    """Find the threshold producing highest validation F1 across [0.05, 0.98]."""
    probabilities, labels = collect_probabilities(model, data_list)
    best_threshold = 0.5
    best_f1 = -1.0

    thresholds = np.arange(0.05, 0.981, 0.01)
    for threshold in thresholds:
        predictions = (probabilities >= threshold).astype(np.int64)
        f1 = f1_score(labels, predictions, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = float(threshold)

    return best_threshold, best_f1


@torch.no_grad()
def evaluate(model, data_list, threshold=0.5, apply_refinement=False):
    """Evaluate precision, recall, and F1 on node-level predictions."""
    model.eval()
    all_preds = []
    all_labels = []

    for data in data_list:
        data = data.to(DEVICE)
        logits = model(data.x, data.edge_index)
        probs = torch.sigmoid(logits).cpu().numpy()
        labels = data.y.cpu().numpy()
        raw_preds = (probs >= threshold).astype(np.int64)

        if apply_refinement and hasattr(data, "edge_index") and data.edge_index.numel() > 0:
            preds = refine_predictions_with_topology(
                data.edge_index, raw_preds, probs, threshold=threshold
            )
        else:
            preds = raw_preds

        all_preds.extend(preds)
        all_labels.extend(labels)

    all_preds = np.asarray(all_preds, dtype=np.int64)
    all_labels = np.asarray(all_labels, dtype=np.int64)

    precision = precision_score(all_labels, all_preds, zero_division=0)
    recall = recall_score(all_labels, all_preds, zero_division=0)
    f1 = f1_score(all_labels, all_preds, zero_division=0)
    return precision, recall, f1


@torch.no_grad()
def print_confusion_matrix(model, data_list, threshold, apply_refinement=False):
    """Print confusion matrix breakdown (TN, FP, FN, TP)."""
    model.eval()
    all_preds = []
    all_labels = []

    for data in data_list:
        data = data.to(DEVICE)
        logits = model(data.x, data.edge_index)
        probs = torch.sigmoid(logits).cpu().numpy()
        labels = data.y.cpu().numpy()
        raw_preds = (probs >= threshold).astype(np.int64)

        if apply_refinement and hasattr(data, "edge_index") and data.edge_index.numel() > 0:
            preds = refine_predictions_with_topology(
                data.edge_index, raw_preds, probs, threshold=threshold
            )
        else:
            preds = raw_preds

        all_preds.extend(preds)
        all_labels.extend(labels)

    all_preds = np.asarray(all_preds, dtype=np.int64)
    all_labels = np.asarray(all_labels, dtype=np.int64)

    tn, fp, fn, tp = confusion_matrix(all_labels, all_preds, labels=[0, 1]).ravel()
    header = "CONFUSION MATRIX (TOPOLOGY-REFINED)" if apply_refinement else "CONFUSION MATRIX (RAW)"
    print(f"\n========== {header} ==========")
    print(f"True Negatives  : {tn}")
    print(f"False Positives : {fp}")
    print(f"False Negatives : {fn}")
    print(f"True Positives  : {tp}")


def main():
    parser = argparse.ArgumentParser(description="Train GAT-based Hardware Trojan detector.")
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
    parser.add_argument(
        "--patience",
        type=int,
        default=20,
        help="Early stopping patience (epochs without validation F1 improvement, default: 20).",
    )
    parser.add_argument(
        "--use-bce",
        action="store_true",
        help="Use standard BCEWithLogitsLoss instead of FocalLoss.",
    )

    args = parser.parse_args()

    print("========== HARDWARE TROJAN GNN ==========")
    print("Device:", DEVICE)
    if torch.cuda.is_available():
        print("GPU   :", torch.cuda.get_device_name(0))
    else:
        print("GPU   : CPU")

    print("Loading node-level dataset...")
    train_samples, val_samples, test_samples = prepare_dataset(
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

    train_data = convert_samples(train_samples)
    val_data = convert_samples(val_samples)
    test_data = convert_samples(test_samples)

    input_dim = train_data[0].x.shape[1]
    print("\n========== GRAPH INFORMATION ==========")
    print("Input feature dimension:", input_dim)

    model = TrojanGNN(input_dim=input_dim, hidden_dim=args.hidden_dim).to(DEVICE)
    print("\n", model)

    positive_weight = calculate_class_weight(train_data)
    if args.use_bce:
        criterion = nn.BCEWithLogitsLoss(pos_weight=positive_weight)
        print("Loss function: BCEWithLogitsLoss")
    else:
        criterion = FocalLoss(alpha=0.5, gamma=2.0, pos_weight=positive_weight.item())
        print("Loss function: Calibrated FocalLoss (gamma=2.0, alpha=0.5)")

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=5, min_lr=1e-5
    )

    print("\n========== TRAINING ==========")
    best_f1 = -1.0
    best_threshold = 0.5
    best_epoch = 0
    no_improve_epochs = 0

    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        loss = train_one_epoch(model, train_data, optimizer, criterion)
        val_threshold, val_f1 = find_best_threshold(model, val_data)
        val_precision, val_recall, _ = evaluate(model, val_data, threshold=val_threshold)

        scheduler.step(val_f1)

        if val_f1 > best_f1:
            best_f1 = val_f1
            best_threshold = val_threshold
            best_epoch = epoch
            no_improve_epochs = 0

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "input_dim": input_dim,
                    "hidden_dim": args.hidden_dim,
                    "epoch": epoch,
                    "val_f1": val_f1,
                    "threshold": val_threshold,
                },
                args.checkpoint,
            )
        else:
            no_improve_epochs += 1

        current_lr = optimizer.param_groups[0]["lr"]
        if epoch == 1 or epoch % 5 == 0 or no_improve_epochs == 0:
            print(
                f"Epoch {epoch:03d} | "
                f"loss={loss:.4f} | "
                f"lr={current_lr:.1e} | "
                f"threshold={val_threshold:.2f} | "
                f"val_precision={val_precision:.4f} | "
                f"val_recall={val_recall:.4f} | "
                f"val_f1={val_f1:.4f}"
            )

        if no_improve_epochs >= args.patience:
            print(
                f"\n[INFO] Early stopping triggered at epoch {epoch} "
                f"(no validation F1 improvement for {args.patience} epochs)."
            )
            break

    # Load best model for evaluation
    checkpoint = torch.load(args.checkpoint, map_location=DEVICE)
    model.load_state_dict(checkpoint["model_state_dict"])
    best_threshold = float(checkpoint["threshold"])

    print("\n========== BEST MODEL ==========")
    print("Best epoch                :", checkpoint["epoch"])
    print("Best validation threshold :", best_threshold)
    print("Best validation F1        :", checkpoint["val_f1"])
    print("Checkpoint                :", args.checkpoint)

    # Final validation evaluation
    val_precision, val_recall, val_f1 = evaluate(model, val_data, threshold=best_threshold)
    print("\n========== FINAL VALIDATION ==========")
    print(f"Threshold   : {best_threshold:.2f}")
    print(f"Precision   : {val_precision:.4f}")
    print(f"Recall      : {val_recall:.4f}")
    print(f"F1          : {val_f1:.4f}")

    # Final test evaluation (Raw GNN)
    test_precision, test_recall, test_f1 = evaluate(
        model, test_data, threshold=best_threshold, apply_refinement=False
    )
    test_family_names = sorted(set(s.family for s in test_samples))
    print("\n========== TEST RESULT (RAW GNN) ==========")
    print("Test families:", test_family_names)
    print(f"Threshold   : {best_threshold:.2f}")
    print(f"Precision   : {test_precision:.4f}")
    print(f"Recall      : {test_recall:.4f}")
    print(f"F1          : {test_f1:.4f}")
    print_confusion_matrix(model, test_data, best_threshold, apply_refinement=False)

    # Final test evaluation (Topology-Refined)
    ref_precision, ref_recall, ref_f1 = evaluate(
        model, test_data, threshold=best_threshold, apply_refinement=True
    )
    print("\n========== TEST RESULT (TOPOLOGY-REFINED) ==========")
    print(f"Threshold   : {best_threshold:.2f}")
    print(f"Precision   : {ref_precision:.4f}")
    print(f"Recall      : {ref_recall:.4f}")
    print(f"F1          : {ref_f1:.4f}")
    print_confusion_matrix(model, test_data, best_threshold, apply_refinement=True)


if __name__ == "__main__":
    main()
