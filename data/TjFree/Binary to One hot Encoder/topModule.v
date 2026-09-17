
module top(bini,topo);
parameter BINW=4;
parameter ONEHOTW=16;
input   [BINW-1:0]     bini;
 output  reg [ONEHOTW-1:0] topo;

  assign topo = 1'b1<<bini;

endmodule


