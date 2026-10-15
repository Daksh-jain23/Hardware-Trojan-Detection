"""
Graph Neural Network for gate-level Hardware Trojan localization.

Input:
    x          -> node features
    edge_index -> netlist connectivity

Output:
    one Trojan logit for every node

The model is intentionally node-level because our goal is to identify
which gates are suspicious, not merely classify an entire netlist.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from torch_geometric.nn import GATConv


class TrojanGNN(nn.Module):
    """
    3-Layer Residual Graph Attention Network for Hardware Trojan gate localization.

    Architecture:
        Input features (53-dim)
              │
           GAT layer 1 (4 heads, 256-dim) + LayerNorm
              │
           GAT layer 2 (4 heads, 256-dim) + Residual (h1) + LayerNorm
              │
           GAT layer 3 (2 heads, 128-dim) + Residual Projection + LayerNorm
              │
        Linear classifier (128 → 1)
              │
        Trojan logit
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 64,
        dropout: float = 0.2,
    ):
        super().__init__()

        self.dropout = dropout

        # First GAT layer (input_dim -> hidden_dim * 4 = 256)
        self.gat1 = GATConv(
            in_channels=input_dim,
            out_channels=hidden_dim,
            heads=4,
            concat=True,
            dropout=dropout,
        )
        self.norm1 = nn.LayerNorm(hidden_dim * 4)

        # Second GAT layer (256 -> 256) with direct residual addition
        self.gat2 = GATConv(
            in_channels=hidden_dim * 4,
            out_channels=hidden_dim,
            heads=4,
            concat=True,
            dropout=dropout,
        )
        self.norm2 = nn.LayerNorm(hidden_dim * 4)

        # Third GAT layer (256 -> 128)
        self.gat3 = GATConv(
            in_channels=hidden_dim * 4,
            out_channels=hidden_dim,
            heads=2,
            concat=True,
            dropout=dropout,
        )
        self.norm3 = nn.LayerNorm(hidden_dim * 2)

        # Residual projection from 256-dim to 128-dim
        self.res_proj = nn.Linear(hidden_dim * 4, hidden_dim * 2)

        # Final node-level classifier
        self.classifier = nn.Linear(hidden_dim * 2, 1)

    def forward(self, x, edge_index):
        """
        Parameters
        ----------
        x : Tensor [num_nodes, input_dim]
        edge_index : Tensor [2, num_edges]

        Returns
        -------
        Tensor [num_nodes]
            One Trojan logit per node.
        """
        # Layer 1
        h1 = self.gat1(x, edge_index)
        h1 = F.elu(h1)
        h1 = self.norm1(h1)
        h1 = F.dropout(h1, p=self.dropout, training=self.training)

        # Layer 2 with residual addition
        h2 = self.gat2(h1, edge_index)
        h2 = F.elu(h2 + h1)
        h2 = self.norm2(h2)
        h2 = F.dropout(h2, p=self.dropout, training=self.training)

        # Layer 3 with projected residual addition
        h3 = self.gat3(h2, edge_index)
        h3 = F.elu(h3 + self.res_proj(h2))
        h3 = self.norm3(h3)
        h3 = F.dropout(h3, p=self.dropout, training=self.training)

        # Node-level Trojan score
        logits = self.classifier(h3)

        return logits.squeeze(-1)


def build_model(input_dim: int = 53) -> TrojanGNN:
    """
    Convenience function for creating the model.
    """
    return TrojanGNN(input_dim=input_dim)


if __name__ == "__main__":
    # Simple sanity test.
    #
    # This does NOT train the model.
    # It only verifies that the architecture works.

    from parser import parse_netlist
    from dataset import graph_to_pyg

    path = "data/TRIT-TS/s13207_T421/s13207_T421.v"

    graph = parse_netlist(path)
    data = graph_to_pyg(graph)

    model = build_model(input_dim=data.x.shape[1])

    print("========== GNN TEST ==========")
    print("Input features :", data.x.shape)
    print("Edges          :", data.edge_index.shape)

    logits = model(data.x, data.edge_index)

    print("Output shape   :", logits.shape)
    print("Expected shape :", (data.num_nodes,))

    print()
    print("Model:")
    print(model)