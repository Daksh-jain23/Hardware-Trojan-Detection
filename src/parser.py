import re
from pathlib import Path
import networkx as nx



# Regular expressions for the Verilog syntax we expect
INSTANCE_RE = re.compile(
    r"(?P<type>[A-Za-z_]\w*)\s+"
    r"(?P<name>[A-Za-z_]\w*)\s*"
    r"\((?P<body>.*?)\)\s*;",
    re.DOTALL,
)

NAMED_PORT_RE = re.compile(
    r"\.(?P<port>\w+)\s*\(\s*(?P<net>\w+)\s*\)"
)



# Trojan identification
def is_trojan_gate(name):
    """
    Trust-Hub Trojan gates use names such as:

        troj00U1
        troj100U2
        trojan00

    We identify them using the 'troj' prefix.
    """
    return name.lower().startswith("troj")



# Main parser
def parse_netlist(file_path):
    """
    Read a gate-level Verilog file and convert it into
    a directed NetworkX graph.

    Returns:
        graph
    """

    file_path = Path(file_path)

    # Read Verilog
    text = file_path.read_text(errors="ignore")

    # Remove // comments
    text = re.sub(r"//.*", "", text)

    graph = nx.DiGraph()

    # net -> gate that drives the net
    net_driver = {}

    # net -> gates that consume the net
    net_loads = {}

    
    # Find every gate instance in the Verilog text
    for match in INSTANCE_RE.finditer(text):

        gate_type = match.group("type").lower()
        gate_name = match.group("name")
        body = match.group("body")

        # Ignore Verilog module-related constructs
        if gate_type in {"module", "endmodule"}:
            continue

        
        # Determine input/output nets
        named_ports = NAMED_PORT_RE.findall(body)

        if named_ports:

            output_nets = []
            input_nets = []

            for port, net in named_ports:

                # Trust-Hub TjIn convention:
                # Q = output
                if port.lower() == "q":
                    output_nets.append(net)
                else:
                    input_nets.append(net)

        else:

            # TjFree uses positional syntax:
            #
            # and G1 (OUT, IN1, IN2);
            #
            # first net = output
            # remaining nets = inputs

            nets = [
                x.strip()
                for x in body.split(",")
                if x.strip()
            ]

            if not nets:
                continue

            output_nets = nets[:1]
            input_nets = nets[1:]

        
        # Add gate node
        graph.add_node(
            gate_name,
            gate_type=gate_type,
            is_trojan=is_trojan_gate(gate_name),
            node_kind="gate",
        )

        
        # Record output connections
        for net in output_nets:
            net_driver[net] = gate_name

        # Record input connections
        for net in input_nets:
            net_loads.setdefault(net, set()).add(gate_name)

    
    # Convert net connections into graph edges
    for net, loaders in net_loads.items():

        driver = net_driver.get(net)

        if driver is not None:

            # Example:
            #
            # G1 -> G2
            #
            # means G1 produces the signal consumed by G2

            for loader in loaders:
                graph.add_edge(
                    driver,
                    loader,
                    net=net
                )

        else:

            # No gate drives this net.
            #
            # Therefore it behaves like a primary input.

            pi_name = f"PI_{net}"

            graph.add_node(
                pi_name,
                gate_type="PI",
                is_trojan=False,
                node_kind="pi",
            )

            for loader in loaders:
                graph.add_edge(
                    pi_name,
                    loader,
                    net=net
                )

    
    # Find primary outputs
    for net, driver in net_driver.items():

        # Driven but never consumed
        if net not in net_loads:

            po_name = f"PO_{net}"

            graph.add_node(
                po_name,
                gate_type="PO",
                is_trojan=False,
                node_kind="po",
            )

            graph.add_edge(
                driver,
                po_name,
                net=net
            )

    return graph


# Simple command-line test
if __name__ == "__main__":

    import sys

    if len(sys.argv) != 2:
        print("Usage:")
        print("python src/parser.py <netlist.v>")
        sys.exit(1)

    path = sys.argv[1]

    graph = parse_netlist(path)

    gate_nodes = [
        n for n, d in graph.nodes(data=True)
        if d["node_kind"] == "gate"
    ]

    trojan_nodes = [
        n for n, d in graph.nodes(data=True)
        if d["is_trojan"]
    ]

    pi_nodes = [
        n for n, d in graph.nodes(data=True)
        if d["node_kind"] == "pi"
    ]

    po_nodes = [
        n for n, d in graph.nodes(data=True)
        if d["node_kind"] == "po"
    ]

    print("\n========== NETLIST ==========")
    print(f"File:           {path}")
    print(f"Gate nodes:     {len(gate_nodes)}")
    print(f"Trojan gates:   {len(trojan_nodes)}")
    print(f"PI nodes:       {len(pi_nodes)}")
    print(f"PO nodes:       {len(po_nodes)}")
    print(f"Total nodes:    {graph.number_of_nodes()}")
    print(f"Total edges:    {graph.number_of_edges()}")
    print("==============================")