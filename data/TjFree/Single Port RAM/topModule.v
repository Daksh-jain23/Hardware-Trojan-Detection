`timescale 1ns / 1ps

module top
#(parameter addrwidth = 6,
parameter datawidth = 8,
parameter depth = 64)
                (
                input [datawidth-1:0] data,  
				input [addrwidth-1:0] addr,  
				input we,clk,                 
				output [datawidth-1:0] q     
				);
				

reg [datawidth-1:0] ram [depth-1:0];

reg [addrwidth-1:0] addrreg;

always @(posedge clk)
begin
if(we)                     
     ram[addr] <=data; 
	 else                  
	     addrreg <=addr;  
end
assign q= ram[addrreg];  

endmodule 


