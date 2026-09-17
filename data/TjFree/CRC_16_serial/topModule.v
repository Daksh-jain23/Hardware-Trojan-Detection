module top(clk,rst,load,dfinish,crcin,crcout); 
input clk; 
input rst; 
input load; 
input dfinish; 
input crcin; 
output crcout; 
reg crcout; 
reg [15:0] crcreg; 
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
 if(count==16) 
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
 crcreg[15:0] <= 16'b0000000000000000; 
 end
 compute:begin 
 
 crcreg[0] <= crcreg[15] ^ crcin; 
 crcreg[1] <= crcreg[0]; 
 crcreg[2] <= crcreg[1] ^ crcreg[15] ^ crcin; 
 crcreg[14:3] <= crcreg[13:2]; 
 crcreg[15] <= crcreg[14] ^ crcreg[15] ^ crcin; 
 crcout <= crcin; 
 end 
 finish:begin 
 crcout <= crcreg[15]; 
 crcreg[15:0] <= {crcreg[14:0],1'b0}; 
 end 
 endcase 
endmodule







