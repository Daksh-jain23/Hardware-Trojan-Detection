module top(clk, reset, in, out);
parameter zero=0, one1=1, two1s=2;
output out; input clk, reset, in;
reg out; reg [1:0] state, nextstate;
always @(posedge clk or posedge reset) begin
 if (reset)
 state <= zero;
 else
 state <= nextstate;
 end
always @(state or in) begin
 case (state)
 zero: begin 
 if (in)
 nextstate=one1;
 else
 nextstate=zero;
 end
 one1: begin 
 if (in)
 nextstate=two1s;
 else
 nextstate=zero;
 end
 two1s: begin 
 if (in) 
 nextstate=two1s;
 else
 nextstate=zero;
 end
 default: 
 nextstate=zero;
 endcase
end
always @(state) begin
 case (state)
 zero: out <= 0;
 one1: out <= 0;
 two1s: out <= 1;
 default : out <= 0;
 endcase
end
endmodule



