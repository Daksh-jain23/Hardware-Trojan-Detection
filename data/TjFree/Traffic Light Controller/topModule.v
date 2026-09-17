module top (clk, Sa, Sb, Ra, Rb, Ga, Gb, Ya, Yb);
input clk;
input Sa;
input Sb;
inout Ra;
inout Rb;
inout Ga;
inout Gb; 
inout Ya;
inout Yb;
reg Ratmp;
reg Rbtmp;
reg Gatmp;
reg Gbtmp;
reg Yatmp;
reg Ybtmp;
reg[3:0] state;
reg[3:0] nextstate;
parameter[1:0] R = 0;
parameter[1:0] Y = 1;
parameter[1:0] G = 2;
wire[1:0] lightA;
wire[1:0] lightB;
assign Ra = Ratmp;
assign Rb = Rbtmp;
assign Ga = Gatmp;
assign Gb = Gbtmp;
assign Ya = Yatmp;
assign Yb = Ybtmp;
initial
begin
 state = 0;
end
always @(state or Sa or Sb)
begin
 Ratmp = 1'b0 ;
 Rbtmp = 1'b0 ;
 Gatmp = 1'b0 ;
 Gbtmp = 1'b0 ;
 Yatmp = 1'b0 ;
 Ybtmp = 1'b0 ;
 nextstate = 0;
 case (state)
 0, 1, 2, 3, 4 :
 begin Gatmp = 1'b1 ;
 Rbtmp = 1'b1 ;
 nextstate = state + 1 ;
 end
 5 :
 begin
 Gatmp = 1'b1 ;
 Rbtmp = 1'b1 ;
 if (Sb == 1'b1)
 begin
 nextstate = 6 ;
 end
 else
 begin
 nextstate = 5 ;
 end 
 end
 6 :
 begin
 Yatmp = 1'b1 ;
 Rbtmp = 1'b1 ;
 nextstate = 7 ;
 end
 7, 8, 9, 10 :
 begin
 Ratmp = 1'b1 ;
 Gbtmp = 1'b1 ;
 nextstate = state + 1 ;
 end
 11 :
 begin
 Ratmp = 1'b1 ;
 Gbtmp = 1'b1 ;
 if (Sa == 1'b1 | Sb == 1'b0)
 begin
 nextstate = 12 ;
 end 
 else
 begin
 nextstate = 11 ;
 end 
 end
 12 :
 begin
 Ratmp = 1'b1 ;
 Ybtmp = 1'b1 ;
 nextstate = 0 ;
 end
 endcase
end always @(posedge clk)
begin
 state <= nextstate ;
end
assign lightA = (Ra==1'b1) ? R : (Ya==1'b1) ? Y : (Ga==1'b1) ? G : lightA;
assign lightB = (Rb==1'b1) ? R : (Yb==1'b1) ? Y : (Gb==1'b1) ? G : lightB;
endmodule


