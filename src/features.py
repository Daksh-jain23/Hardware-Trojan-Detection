"""
Improved gate-level feature engineering.

Each gate gets features describing:
1. Its own gate type
2. Its local connectivity
3. Its position in the circuit
4. The structure of its 1-hop neighbourhood
5. The structure of its 2-hop neighbourhood

These features are used as node inputs to the GNN.
"""

from __future__ import annotations

import networkx as nx
import numpy as np

# Gate types
GATE_TYPES = [
    "and",
    "nand",
    "or",
    "nor",
    "not",
    "buf",
    "xor",
    "xnor",
    "PI",
    "PO",
]

TYPE_INDEX = {gate_type: i for i, gate_type in enumerate(GATE_TYPES)}

N_TYPES = len(GATE_TYPES)


def _type_index(gate_type: str) -> int:
    """
    Convert gate type into an integer index.

    Unknown gate types are mapped to 'buf' rather than crashing.
    """
    return TYPE_INDEX.get(
        gate_type,
        TYPE_INDEX["buf"]
    )


# Circuit position
def _depth_from_pi(g: nx.DiGraph) -> dict:
    """
    Calculate shortest distance of every node from a primary input.

    Example:

        PI -> A -> B -> C -> PO

        PI depth = 0
        A  depth = 1
        B  depth = 2
        C  depth = 3
    """

    pis = [
        n for n, d in g.nodes(data=True)
        if d.get("node_kind") == "pi"
    ]

    # Fallback if explicit PI nodes don't exist
    if not pis:
        pis = [
            n for n, degree in g.in_degree()
            if degree == 0
        ]

    depth = {}

    for pi in pis:
        distances = nx.single_source_shortest_path_length(g, pi)

        for node, distance in distances.items():
            if node not in depth or distance < depth[node]:
                depth[node] = distance

    max_depth = max(depth.values(), default=0)

    # Nodes unreachable from a PI are placed after the deepest
    # reachable node.
    return {
        node: depth.get(node, max_depth + 1)
        for node in g.nodes()
    }


def _distance_to_po(g: nx.DiGraph) -> dict:
    """
    Calculate shortest distance from every node to a primary output.

    We reverse the graph and perform BFS from the PO nodes.
    """

    pos = [
        n for n, d in g.nodes(data=True)
        if d.get("node_kind") == "po"
    ]

    # Fallback
    if not pos:
        pos = [
            n for n, degree in g.out_degree()
            if degree == 0
        ]

    reversed_graph = g.reverse(copy=False)

    distance = {}

    for po in pos:
        distances = nx.single_source_shortest_path_length(
            reversed_graph,
            po
        )

        for node, d in distances.items():
            if node not in distance or d < distance[node]:
                distance[node] = d

    max_distance = max(distance.values(), default=0)

    return {
        node: distance.get(node, max_distance + 1)
        for node in g.nodes()
    }


# Neighbourhood features
def _build_undirected_adjacency(g: nx.DiGraph, nodes):
    """
    Build sparse undirected adjacency matrix.

    Direction is ignored here because we want to describe
    the local structural neighbourhood of a gate.
    """

    import scipy.sparse as sp

    index = {
        node: i
        for i, node in enumerate(nodes)
    }

    rows = []
    cols = []

    for u, v in g.edges():

        rows.append(index[u])
        cols.append(index[v])

        rows.append(index[v])
        cols.append(index[u])

    n = len(nodes)

    A = sp.csr_matrix(
        (
            np.ones(len(rows), dtype=np.float32),
            (rows, cols)
        ),
        shape=(n, n)
    )

    # Remove duplicate edges.
    A.data[:] = 1.0

    return A


def _neighbourhood_features(
    A,
    type_onehot,
    total_degree,
):
    """
    Calculate 1-hop and 2-hop structural features.

    For each node we calculate:

        1-hop:
            gate-type distribution
            average neighbour degree
            neighbour count

        2-hop:
            gate-type distribution
            average neighbour degree
            neighbour count
    """

    # 1-hop
    hop1 = A

    hop1_count = np.asarray(
        hop1.sum(axis=1)
    ).flatten()

    safe_count = np.where(
        hop1_count == 0,
        1,
        hop1_count
    )

    hop1_type = (
        hop1 @ type_onehot
    ) / safe_count.reshape(-1, 1)

    hop1_degree = (
        hop1 @ total_degree.reshape(-1, 1)
    ).flatten() / safe_count

    # 2-hop
    hop2 = A @ A

    # Remove self
    hop2 = hop2.tolil()
    hop2.setdiag(0)
    hop2 = hop2.tocsr()

    # Remove nodes that are already 1-hop neighbours.
    hop2_only = (
        hop2 - hop2.multiply(A.astype(bool))
    ).tocsr()

    # Path counts can create negative values after subtraction.
    hop2_only.data = np.clip(
        hop2_only.data,
        0,
        None
    )

    hop2_count = np.asarray(
        hop2_only.sum(axis=1)
    ).flatten()

    safe_count = np.where(
        hop2_count == 0,
        1,
        hop2_count
    )

    hop2_type = (
        hop2_only @ type_onehot
    ) / safe_count.reshape(-1, 1)

    hop2_degree = (
        hop2_only @ total_degree.reshape(-1, 1)
    ).flatten() / safe_count

    return (
        hop1_type,
        hop1_degree,
        hop1_count,
        hop2_type,
        hop2_degree,
        hop2_count,
    )


# Main node feature function
def compute_node_features(g: nx.DiGraph):
    """
    Convert a netlist graph into a node-feature matrix.

    Returns:

        X:
            shape = [number_of_nodes, FEATURE_DIM]

        nodes:
            node names in exactly the same order as X
    """

    nodes = list(g.nodes())

    n = len(nodes)

    # Own gate type
    type_onehot = np.zeros(
        (n, N_TYPES),
        dtype=np.float32
    )

    for i, node in enumerate(nodes):

        gate_type = g.nodes[node].get(
            "gate_type",
            "buf"
        )

        type_onehot[
            i,
            _type_index(gate_type)
        ] = 1.0

    
    # Connectivity
    in_degree = np.array(
        [g.in_degree(node) for node in nodes],
        dtype=np.float32
    )

    out_degree = np.array(
        [g.out_degree(node) for node in nodes],
        dtype=np.float32
    )

    total_degree = in_degree + out_degree

    
    # Position in circuit
    depth = _depth_from_pi(g)

    distance_to_po = _distance_to_po(g)

    depth_features = np.array(
        [depth[node] for node in nodes],
        dtype=np.float32
    )

    po_features = np.array(
        [distance_to_po[node] for node in nodes],
        dtype=np.float32
    )

    # Local neighbourhood
    A = _build_undirected_adjacency(
        g,
        nodes
    )

    (
        hop1_type,
        hop1_degree,
        hop1_count,
        hop2_type,
        hop2_degree,
        hop2_count,
    ) = _neighbourhood_features(
        A,
        type_onehot,
        total_degree
    )

    
    # Extra structural features
    
    # Normalized position in the circuit.
    max_depth = max(
        depth_features.max(),
        1
    )

    normalized_depth = (
        depth_features / max_depth
    )

    max_po_distance = max(
        po_features.max(),
        1
    )

    normalized_po_distance = (
        po_features / max_po_distance
    )

    # Final feature vector    
    features = np.concatenate(
        [
            # Own gate identity
            type_onehot,

            # Local connectivity
            in_degree.reshape(-1, 1),
            out_degree.reshape(-1, 1),
            total_degree.reshape(-1, 1),

            # Global circuit position
            depth_features.reshape(-1, 1),
            po_features.reshape(-1, 1),
            normalized_depth.reshape(-1, 1),
            normalized_po_distance.reshape(-1, 1),

            # 1-hop context
            hop1_type,
            hop1_degree.reshape(-1, 1),
            hop1_count.reshape(-1, 1),

            # 2-hop context
            hop2_type,
            hop2_degree.reshape(-1, 1),
            hop2_count.reshape(-1, 1),
        ],
        axis=1
    ).astype(np.float32)

    return features, nodes


# Feature dimension
FEATURE_DIM = (
    N_TYPES       # own gate type
    + 3           # in-degree, out-degree, total-degree
    + 4           # depth, distance-to-PO + normalized versions
    + N_TYPES + 2 # 1-hop
    + N_TYPES + 2 # 2-hop
)


if __name__ == "__main__":

    import sys

    sys.path.insert(0, "src")

    from parser import parse_netlist

    if len(sys.argv) < 2:
        print("Usage:")
        print("python src/features.py <netlist.v>")
        sys.exit(1)

    graph = parse_netlist(sys.argv[1])

    X, nodes = compute_node_features(graph)

    print("========== FEATURES ==========")
    print("Nodes       :", len(nodes))
    print("Feature dim :", FEATURE_DIM)
    print("Shape       :", X.shape)
    print()
    print("First node  :", nodes[0])
    print("First vector:", X[0])