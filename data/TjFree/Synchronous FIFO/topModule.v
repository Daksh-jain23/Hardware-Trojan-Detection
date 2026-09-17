`timescale 1ns / 1ps

module top (input [7:0] datain, input clk, rst, rd, wr,
output empty, full, output reg [3:0]fifocnt,
output reg [7:0] dataout);


reg [7:0] fiforam [0:7];
reg [2:0] rdptr, wrptr;
assign empty= (fifocnt==0);
assign full =(fifocnt==8);
always @(posedge clk) begin: write
if (wr && ! full)
fiforam [wrptr] <= datain;
else if (wr && rd)
fiforam [wrptr] <= datain;
end

always @ (posedge clk) begin: read
if (rd && !empty)
dataout <= fiforam [rdptr];
else if (rd && wr)
dataout <= fiforam [rdptr];
end



always @(posedge clk) begin: pointer
if (rst) begin
wrptr <= 0;
rdptr <= 0;
end 
else begin
wrptr <= ((wr && ! full) || (wr && rd)) ? wrptr+1 :
wrptr;
rdptr <= ((rd && !empty) || (wr && rd)) ? rdptr+1:
rdptr;
end
end

always @(posedge clk) begin: count
if (rst) fifocnt <= 0;
else begin
case ({wr, rd})
2'b00: fifocnt <= fifocnt;
2'b01: fifocnt <= (fifocnt==0) ? 0: fifocnt-1;
2'b10: fifocnt <= (fifocnt==8) ? 8: fifocnt+1;
2'b11 : fifocnt <= fifocnt;
default: fifocnt <= fifocnt;
endcase
end
end
endmodule


