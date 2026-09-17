`timescale 1ns / 1ps

module top (a, opcode, result);
input [7:0] a;
input [2:0] opcode;
output [7:0] result;

wire [7:0] a;
wire [2:0] opcode;
reg [7:0] result;


parameter sraop = 3'b000, 
srlop = 3'b001,           
slaop = 3'b010,           
sllop = 3'b011,           
rorop = 3'b100,           
rolop = 3'b101;           

always @ (a or opcode)
begin
case (opcode)
sraop : result = {a[7], a[7], a[6], a[5],
 a[4], a[3], a[2], a[1]};
srlop : result = a >> 1;
slaop : result = {a[6], a[5], a[4], a[3],
 a[2], a[1], a[0], 1'b0};
 sllop : result = a << 1;
rorop : result = {a[0], a[7], a[6], a[5],
a[4], a[3], a[2], a[1]};
rolop : result = {a[6], a[5], a[4], a[3],
a[2], a[1], a[0], a[7]};
default : result = 0;
endcase
end
endmodule


