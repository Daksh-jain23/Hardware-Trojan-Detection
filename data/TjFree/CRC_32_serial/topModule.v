module top(clk,rst,load,dfinish,crcin,crcout); 
input clk; 
input rst; 
input load; 
input dfinish; 
input crcin; 
output crcout; 
reg crcout; 
reg [31:0] crcreg; 
reg [1:0] state; 
reg [4:0] count; 
parameter idle = 2'b00; 
parameter compute = 2'b01; 
parameter finish = 2'b10; 
  always@ (posedge clk) 
begin 
case (state) 
 idle: begin 
 if (load) 
 state <= compute; 
 else
 state <= idle; 
 end
 compute:begin 
 if(dfinish) 
 state <= finish; 
 else
 state <= compute; 
 end
 finish: begin 
   if(count==32) 
 state <= idle; 
 else
 count <= count+1; 
 end
endcase
end 
always@ (posedge clk or negedge rst)
 if(rst) 
 begin 
 count <= 5'b00000; 
 state <= idle; 
 end
 else
 case(state) 
 idle:begin
   crcreg[31:0] <= 32'b00000000000000000000000000000000; 
 end
 compute:begin 
 
   crcreg[0] <= crcreg[31] ^ crcin; 
 crcreg[1] <= crcreg[0]; 
   crcreg[2] <= crcreg[1] ^ crcreg[31] ^ crcin; 
   crcreg[30:3] <= crcreg[29:2]; 
   crcreg[31] <= crcreg[30] ^ crcreg[31] ^ crcin; 
 crcout <= crcin; 
 end 
 finish:begin 
   crcout <= crcreg[31]; 
   crcreg[31:0] <= {crcreg[30:0],1'b0}; 
 end 
 endcase 
endmodule


