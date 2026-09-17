`timescale 1ns / 1ps
module top(a,b,result,start);

input [7:0] a;
input [3:0] b;
output [7:0] result;
input start;

wire [3:0] bbar;

reg [3:0] bneg;
reg [7:0] result;
reg [3:0] count;

assign bbar=~b;

always @(bbar)
bneg=bbar+1;

always @(posedge start)
begin
result=a;
count =4'b0100;

if ((a!=0) && (b!=0))
while(count)
begin
result=result<<1;
result={(result[7:4]+bneg),result[3:0]};
if(result[7]==1)
begin
result= {(result[7:4] + b), result[3:1], 1'b0};
count=count-1;
end
else
begin
result={result[7:1],1'b1};
count=count-1;
end
end
end
endmodule



