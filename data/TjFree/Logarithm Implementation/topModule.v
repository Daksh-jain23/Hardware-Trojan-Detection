module top(input [31:0] a,b,output [127:0] aout, bout);
  assign aout = 1000000000 * $ln(a);
  assign bout = 1000000000 * $log10(b);
endmodule




