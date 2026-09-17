`timescale 1ns / 1ps

module top 
     # (parameter datawidth=8,
	      parameter addrwidth=4,
			parameter depth=16
			)
    (   input clk, 
        input wren,    
        input [datawidth-1:0] datain,    
        input [addrwidth-1:0] addrin0,  
        input [addrwidth-1:0] addrin1,  
        input porten0,    
        input porten1,    
        output [datawidth-1:0] dataout0,    
        output [datawidth-1:0] dataout1    
    );

reg [datawidth-1:0] ram[0:depth-1];

always@(posedge clk)
begin
    if(porten0 == 1 && wren == 1)    
        ram[addrin0] <= datain;
end

assign dataout0 = porten0 ? ram[addrin0] : 'dZ;   
assign dataout1 = porten1 ? ram[addrin1] : 'dZ;   

endmodule 



