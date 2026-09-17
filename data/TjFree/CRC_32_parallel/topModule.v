module top(clk,rst,load,dfinish,crcin,crcout); 
input clk; 
input rst; 
input load; 
input dfinish; 
input [7:0] crcin; 
output [7:0] crcout; 
reg [7:0] crcout; 
reg [31:0] crcreg; 
reg [1:0] count; 
reg [1:0] state; 
wire [31:0] nextcrcreg; 
parameter idle = 2'b00; 
parameter compute = 2'b01; 
parameter finish = 2'b10; 
assign nextcrcreg[0] = crcreg[24] ^ crcreg[30] ^ crcin[0] ^ 
crcin[6]; 
assign nextcrcreg[1] = crcreg[24] ^ crcreg[25] ^ crcreg[30] ^ 
crcreg[31] ^ crcin[0] ^ crcin[1] ^ crcin[6] ^ crcin[7]; 
assign nextcrcreg[2] = crcreg[24] ^ crcreg[25] ^ crcreg[26] ^ 
crcreg[30] ^ crcreg[31] ^ crcin[0] ^ crcin[1] ^ crcin[2] ^ crcin[6] 
^ crcin[7]; 
assign nextcrcreg[3] = crcreg[25] ^ crcreg[26] ^ crcreg[27] ^ 
crcreg[31] ^ crcin[1] ^ crcin[2] ^ crcin[3] ^ crcin[7]; 
assign nextcrcreg[4] = crcreg[24] ^ crcreg[26] ^ crcreg[27] ^ 
crcreg[28] ^ crcreg[30] ^ crcin[0] ^ crcin[2] ^ crcin[3] ^ crcin[4] 
^ crcin[6]; 
assign nextcrcreg[5] = crcreg[24] ^ crcreg[25] ^ crcreg[27] ^ 
crcreg[28] ^ crcreg[29] ^ crcreg[30] ^ crcreg[31] ^ crcin[0] ^ 
crcin[1] ^ crcin[3] ^ crcin[4] ^ crcin[5] ^ crcin[6] ^ crcin[7]; 
assign nextcrcreg[6] = crcreg[25] ^ crcreg[26] ^ crcreg[28] ^ 
crcreg[29] ^ crcreg[30] ^ crcreg[31] ^ crcin[1] ^ crcin[2] ^ crcin[4] 
^ crcin[5] ^ crcin[6] ^ crcin[7]; 
assign nextcrcreg[7] = crcreg[24] ^ crcreg[26] ^ crcreg[27] ^ 
crcreg[29] ^ crcreg[31] ^ crcin[0] ^ crcin[2] ^ crcin[3] ^ crcin[5] 
^ crcin[7]; 
assign nextcrcreg[8] = crcreg[0] ^ crcreg[24] ^ crcreg[25] ^ 
crcreg[27] ^ crcreg[28] ^ crcin[0] ^ crcin[1] ^ crcin[3] ^ crcin[4]; 
assign nextcrcreg[9] = crcreg[1] ^ crcreg[25] ^ crcreg[26] ^ 
crcreg[28] ^ crcreg[29] ^ crcin[1] ^ crcin[2] ^ crcin[4] ^ crcin[5]; 
assign nextcrcreg[10] = crcreg[2] ^ crcreg[24] ^ crcreg[26] ^ 
crcreg[27] ^ crcreg[29] ^ crcin[0] ^ crcin[2] ^ crcin[3] ^ crcin[5]; 
assign nextcrcreg[11] = crcreg[3] ^ crcreg[24] ^ crcreg[25] ^ 
crcreg[27] ^ crcreg[28] ^ crcin[0] ^ crcin[1] ^ crcin[3] ^ crcin[4]; 
assign nextcrcreg[12] = crcreg[4] ^ crcreg[24] ^ crcreg[25] ^ 
crcreg[26] ^ crcreg[28] ^ crcreg[29] ^ crcreg[30] ^ crcin[0] ^ 
crcin[1] ^ crcin[2] ^ crcin[4] ^ crcin[5] ^ crcin[6]; 
assign nextcrcreg[13] = crcreg[5] ^ crcreg[25] ^ crcreg[26] ^ 
crcreg[27] ^ crcreg[29] ^ crcreg[30] ^ crcreg[31] ^ crcin[1] ^ 
crcin[2] ^ crcin[3] ^ crcin[5] ^ crcin[6] ^ crcin[7]; 
assign nextcrcreg[14] = crcreg[6] ^ crcreg[26] ^ crcreg[27] ^ 
crcreg[28] ^ crcreg[30] ^ crcreg[31] ^ crcin[2] ^ crcin[3] ^ crcin[4] 
^ crcin[6] ^ crcin[7]; 
assign nextcrcreg[15] = crcreg[7] ^ crcreg[27] ^ crcreg[28] ^ 
crcreg[29] ^ crcreg[31] ^ crcin[3] ^ crcin[4] ^ crcin[5] ^ crcin[7]; 
assign nextcrcreg[16] = crcreg[8] ^ crcreg[24] ^ crcreg[28] ^ 
crcreg[29] ^ crcin[0] ^ crcin[4] ^ crcin[5]; 
assign nextcrcreg[17] = crcreg[9] ^ crcreg[25] ^ crcreg[29] ^ 
crcreg[30] ^ crcin[1] ^ crcin[5] ^ crcin[6]; 
assign nextcrcreg[18] = crcreg[10] ^ crcreg[26] ^ crcreg[30] ^ 
crcreg[31] ^ crcin[2] ^ crcin[6] ^ crcin[7]; 
assign nextcrcreg[19] = crcreg[11] ^ crcreg[27] ^ crcreg[31] ^ 
crcin[3] ^ crcin[7]; 
assign nextcrcreg[20] = crcreg[12] ^ crcreg[28] ^ crcin[4]; 
assign nextcrcreg[21] = crcreg[13] ^ crcreg[29] ^ crcin[5]; 
assign nextcrcreg[22] = crcreg[14] ^ crcreg[24] ^ crcin[0]; 
assign nextcrcreg[23] = crcreg[15] ^ crcreg[24] ^ crcreg[25] ^ 
crcreg[30] ^ crcin[0] ^ crcin[1] ^ crcin[6]; 
assign nextcrcreg[24] = crcreg[16] ^ crcreg[25] ^ crcreg[26] ^ 
crcreg[31] ^ crcin[1] ^ crcin[2] ^ crcin[7]; 
assign nextcrcreg[25] = crcreg[17] ^ crcreg[26] ^ crcreg[27] ^ 
crcin[2] ^ crcin[3]; 
assign nextcrcreg[26] = crcreg[18] ^ crcreg[24] ^ crcreg[27] ^ 
crcreg[28] ^ crcreg[30] ^ crcin[0] ^ crcin[3] ^ crcin[4] ^ crcin[6]; 
assign nextcrcreg[27] = crcreg[19] ^ crcreg[25] ^ crcreg[28] ^ 
crcreg[29] ^ crcreg[31] ^ crcin[1] ^ crcin[4] ^ crcin[5] ^ crcin[7]; 
assign nextcrcreg[28] = crcreg[20] ^ crcreg[26] ^ crcreg[29] ^ 
crcreg[30] ^ crcin[2] ^ crcin[5] ^ crcin[6]; 
assign nextcrcreg[29] = crcreg[21] ^ crcreg[27] ^ crcreg[30] ^ 
crcreg[31] ^ crcin[3] ^ crcin[6] ^ crcin[7]; 
assign nextcrcreg[30] = crcreg[22] ^ crcreg[28] ^ crcreg[31] ^ 
crcin[4] ^ crcin[7]; 
assign nextcrcreg[31] = crcreg[23] ^ crcreg[29] ^ crcin[5]; 
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
 crcreg[31:0] <= 32'b00000000000000000000000000000000; 

 state <= idle; 
 count <= 2'b00; 
 end 
 else 
 case(state) 
 idle:begin 
 crcreg[31:0] <= 
32'b00000000000000000000000000000000; 
 end 
 compute:begin 
 crcreg[31:0]<= nextcrcreg[31:0]; 
 crcout[7:0] <= crcin[7:0]; 
 end 
 finish:begin 
 crcreg[31:0] <= {crcreg[23:0],8'b00000000}; 
 crcout[7:0] <= crcreg[31:24]; 
 end 
 endcase 
endmodule 


