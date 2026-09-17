`timescale 1ns / 1ps
module fulladder( A, B, Cin, S, Cout);
 input wire A, B, Cin;
 output reg S, Cout;
 always @(A or B or Cin)
  begin
   S = A ^ B ^ Cin;
   Cout = A&B | B&Cin | Cin&A ;
  end
endmodule
module mux(A,B,S,Y);
input A,B,S;
output reg Y;
always@(A,B,S)
begin
Y=~S&A| S&B;
end
endmodule
module top (x,y,carry,s,cout);
input [3:0]x,y;
input carry;
output [3:0]s;
output cout;
wire w1,w2,w3,w4,w5,w6,w7,w8,w9,w10,w11,w12,w13,w14,w15,w16;
fulladder fao (x[0],y[0],1'b0,w1,w2);
fulladder fa1 (x[1],y[1],w2,w3,w4);
fulladder fa2 (x[2],y[2],w4,w5,w6);
fulladder fa3 (x[3],y[3],w6,w7,w8);
fulladder fa4 (x[0],y[0],1'b1,w9,w10);
fulladder fa5 (x[1],y[1],w10,w11,w12);
fulladder fa6 (x[2],y[2],w12,w13,w14);
fulladder fa7 (x[3],y[3],w14,w15,w16);
mux mu0(w1,w9,carry,s[0]);
mux mu1(w3,w11,carry,s[1]);
mux mu2(w5,w13,carry,s[2]);
mux mu3(w7,w15,carry,s[3]);
mux mu4(w8,w16,carry,cout);
endmodule


