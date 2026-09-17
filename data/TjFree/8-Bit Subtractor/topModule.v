`timescale 1ns / 1ps
module top (a, b, result);
input [7:0] a, b;
output [7:0] result;
reg [7:0] result;
reg [7:0] negb;
always @ (a or b)
begin
 negb = ~b + 1;
result = a + negb;
end
endmodule



