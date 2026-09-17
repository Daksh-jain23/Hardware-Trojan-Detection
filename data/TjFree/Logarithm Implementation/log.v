module logarithm(input [31:0] a,b,output [127:0] a_out, b_out);
  assign a_out = 1000000000 * $ln(a);
  assign b_out = 1000000000 * $log10(b);
endmodule


