"""
Unit tests for Verilog netlist parser.
"""

import sys
import tempfile
import unittest
from pathlib import Path

import networkx as nx

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from parser import parse_netlist, is_trojan_gate


class TestNetlistParser(unittest.TestCase):

    def setUp(self):
        self.verilog_code = """
        module sample_circuit (in1, in2, clk, out1);
            input in1, in2, clk;
            output out1;
            wire n1, n2, n3;

            and U1 (.A(in1), .B(in2), .Q(n1));
            not U2 (.A(n1), .Q(n2));
            dff U3 (.CLK(clk), .D(n2), .Q(out1));

            // Trojan logic
            and troj01_gate (.A(n1), .B(n2), .Q(n3));
        endmodule
        """
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".v",
            delete=False,
            encoding="utf-8",
        )
        self.temp_file.write(self.verilog_code)
        self.temp_file.close()
        self.netlist_path = Path(self.temp_file.name)

    def tearDown(self):
        if self.netlist_path.exists():
            self.netlist_path.unlink()

    def test_parse_netlist_structure(self):
        graph = parse_netlist(self.netlist_path)

        self.assertIsInstance(graph, nx.DiGraph)
        self.assertGreater(graph.number_of_nodes(), 0)
        self.assertGreater(graph.number_of_edges(), 0)

        # Check gate nodes exist
        self.assertIn("U1", graph.nodes)
        self.assertIn("U2", graph.nodes)
        self.assertIn("U3", graph.nodes)
        self.assertIn("troj01_gate", graph.nodes)

        # Check gate types
        self.assertEqual(graph.nodes["U1"].get("gate_type"), "and")
        self.assertEqual(graph.nodes["U2"].get("gate_type"), "not")
        self.assertEqual(graph.nodes["U3"].get("gate_type"), "dff")

        # Check signal flow edge: U1 (drives n1) -> U2 (reads n1)
        self.assertTrue(graph.has_edge("U1", "U2"))
        # U2 (drives n2) -> U3 (reads n2)
        self.assertTrue(graph.has_edge("U2", "U3"))

    def test_trojan_gate_detection(self):
        self.assertTrue(is_trojan_gate("troj01_gate"))
        self.assertTrue(is_trojan_gate("trojan_trigger"))
        self.assertFalse(is_trojan_gate("U1"))
        self.assertFalse(is_trojan_gate("g124"))


if __name__ == "__main__":
    unittest.main()
