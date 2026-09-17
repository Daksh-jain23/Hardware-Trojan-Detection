`timescale 1ns / 1ps

module top (a, b, opcode, rslt);
input [3:0] a, b;
input [2:0] opcode;
output [7:0] rslt;
reg [7:0] rslt;
parameter addop = 3'b000,
subop = 3'b001,
mulop = 3'b010,
andop = 3'b011,
orop = 3'b100,
notop = 3'b101, 
xorop = 3'b110,
xnorop = 3'b111;
always @ (a or b or opcode)
begin
case (opcode)
addop: rslt = a + b;
subop: rslt = a - b;
mulop: rslt = a * b;
andop: rslt = a & b; 
orop: rslt = a | b;
notop: rslt = ~a; 
xorop: rslt = a ^ b;
xnorop: rslt = ~(a ^ b);
endcase
end
endmodule

