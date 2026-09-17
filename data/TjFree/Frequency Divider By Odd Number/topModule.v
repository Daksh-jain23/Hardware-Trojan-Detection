`timescale 1ns / 1ps




module top
#(parameter N=5)
(
 input   clkin,
 output   clkout
    );

reg  [3:0] count = 4'b0;        
reg     A1 = 0;
reg       B1 = 0;
reg     TffA = 0;
reg    TffB = 0;
wire    clockout;
wire    wTffA;
wire    wTffB;

assign   wTffA  = TffA; 
assign   wTffB  = TffB; 

assign   clkout = wTffB ^ wTffA; 

always@(posedge clkin)
 begin
  if(count == N-1) 
   begin 
    count <= 4'b0000;
   end 
  else
   begin
    count <= count + 1;
   end 
 end

always@(posedge clkin)
 begin
  if(count == 4'b0000)
   A1 <= 1;
  else
   A1 <= 0;
 end

always@(posedge clkin)
 begin
  if(count == (N+1)/2) 
   B1 <= 1; 
  else
   B1 <= 0;
 end

always@(negedge A1) 
 begin   
  TffA <= ~TffA;
 end

always@(negedge clkin)
 begin
  if(B1) 
   begin 
    TffB <= ~TffB;
   end
 end

endmodule



