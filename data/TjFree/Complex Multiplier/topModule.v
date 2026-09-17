module top(c1,c2,product);
input [15:0]c1,c2;
output [31:0]product;
assign product={((c1[15:8]*c2[15:8])-(c1[7:0]*c2[7:0])),((c1[15:8]*c2[7:0])+(c1[7:0]*c2[15:8]))};
endmodule



