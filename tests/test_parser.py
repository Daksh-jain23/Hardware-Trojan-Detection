"""Regression tests for the gate-level Verilog parser."""

import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from parser import parse_netlist


class TestParser(unittest.TestCase):

    def test_qn_escaped_output_is_a_driver_not_a_primary_input(self):
        """Complemented DFF output must retain its downstream connection."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            netlist = Path(tmp_dir) / "escaped_qn.v"
            netlist.write_text(
                """
                module top(input clk, input d, output y);
                  dff U1 (.D(d), .CK(clk), .Q(q), .QN(\\DFF_1/net0));
                  nand U2 (.DIN1(\\DFF_1/net0), .DIN2(d), .Q(y));
                endmodule
                """
            )

            graph = parse_netlist(netlist)
            self.assertTrue(graph.has_edge("U1", "U2"))
            self.assertEqual(graph.edges["U1", "U2"]["net"], "\\DFF_1/net0")
            self.assertNotIn("PI_\\DFF_1/net0", graph)

    def test_named_q_output_preserves_normal_identifier_connections(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            netlist = Path(tmp_dir) / "normal.v"
            netlist.write_text(
                """
                module top(input a, input b, output y);
                  and2 U1 (.DIN1(a), .DIN2(b), .Q(n1));
                  not1 U2 (.DIN(n1), .Q(y));
                endmodule
                """
            )

            graph = parse_netlist(netlist)
            self.assertTrue(graph.has_edge("U1", "U2"))


if __name__ == "__main__":
    unittest.main()
