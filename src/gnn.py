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
    Graph Attention Network for Hardware Trojan gate localization.

    Architecture:

        41 input features
              |
           GAT layer
          4 attention heads
              |
           GAT layer
          2 attention heads
              |
        Linear classifier
              |
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

        # First GAT layer.
        #
        # input_dim = 41
        # 4 attention heads × 64 features
        # output dimension = 256
        self.gat1 = GATConv(
            in_channels=input_dim,
            out_channels=hidden_dim,
            heads=4,
            concat=True,
            dropout=dropout,
        )

        # Second GAT layer.
        #
        # Input = 64 × 4 = 256
        # 2 attention heads × 64 features
        # output dimension = 128
        self.gat2 = GATConv(
            in_channels=hidden_dim * 4,
            out_channels=hidden_dim,
            heads=2,
            concat=True,
            dropout=dropout,
        )

        # Final node-level classifier.
        #
        # Each node now has 128 learned features.
        # Output is ONE logit:
        #
        # positive -> suspicious / Trojan
        # negative -> normal
        self.classifier = nn.Linear(hidden_dim * 2, 1)

    def forward(self, x, edge_index):
        """
        Parameters
        ----------
        x : Tensor
            Shape [num_nodes, input_dim]

        edge_index : Tensor
            Shape [2, num_edges]

        Returns
        -------
        Tensor
            Shape [num_nodes]

            One Trojan logit per node.
        """

        # First graph-attention layer
        x = self.gat1(x, edge_index)
        x = F.elu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)

        # Second graph-attention layer
        x = self.gat2(x, edge_index)
        x = F.elu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)

        # Node-level Trojan score
        logits = self.classifier(x)

        return logits.squeeze(-1)


def build_model(input_dim: int = 41) -> TrojanGNN:
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