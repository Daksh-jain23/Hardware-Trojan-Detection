module top(clk,rst,load,dfinish,crcin,crcout); 

input clk; 
input rst; 
input load; 
input dfinish; 
input [7:0] crcin; 
output [7:0] crcout;
reg [7:0] crcout; 
reg [15:0] crcreg;
reg [1:0] count;  
reg [1:0] state; 
wire [15:0] nextcrcreg; 
parameter idle = 2'b00; 
parameter compute = 2'b01;
parameter finish = 2'b10; 

assign nextcrcreg[0] = (^crcin[7:0]) ^ (^crcreg[15:8]); 
assign nextcrcreg[1] = (^crcin[6:0]) ^ (^crcreg[15:9]); 
assign nextcrcreg[2] = crcin[7] ^ crcin[6] ^ crcreg[9] ^ crcreg[8]; 
assign nextcrcreg[3] = crcin[6] ^ crcin[5] ^ crcreg[10] ^ 
crcreg[9]; 
assign nextcrcreg[4] = crcin[5] ^ crcin[4] ^ crcreg[11] ^ 
crcreg[10]; 
assign nextcrcreg[5] = crcin[4] ^ crcin[3] ^ crcreg[12] ^ 
crcreg[11]; 
assign nextcrcreg[6] = crcin[3] ^ crcin[2] ^ crcreg[13] ^ 
crcreg[12]; 
assign nextcrcreg[7] = crcin[2] ^ crcin[1] ^ crcreg[14] ^ 
crcreg[13]; 
assign nextcrcreg[8] = crcin[1] ^ crcin[0] ^ crcreg[15] ^ crcreg[14] 
^ crcreg[0]; 
assign nextcrcreg[9] = crcin[0] ^ crcreg[15] ^ crcreg[1]; 
assign nextcrcreg[14:10] = crcreg[6:2]; 
assign nextcrcreg[15] = (^crcin[7:0]) ^ (^crcreg[15:7]); 
always@(posedge clk) 
begin 
case(state) 
 idle:begin 
 if(load) 
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
 finish:begin 
 if(count==2)
 state <= idle; 
 else 
 state <= finish; 
 end 
endcase 
end 
always@(posedge clk or negedge rst)
 if(rst) 
 begin 
 crcreg[15:0] <= 16'b0000000000000000;
 state <= idle; 
 count <= 2'b00; 
 end 
 else 
 case(state) 
 idle:begin 
 crcreg[15:0] <= 16'b0000000000000000; 
 end 
 compute:begin 
 crcreg[15:0]<= nextcrcreg[15:0]; 
 crcout[7:0] <= crcin[7:0]; 
 end 
 finish:begin 
 crcreg[15:0] <= {crcreg[7:0],8'b00000000}; 
 crcout[7:0] <= crcreg[15:8]; 
 end 
 endcase 
endmodule 


