module top(input [31:0] a,input [31:0] b,output exception,overflow,underflow,output [31:0] res);

wire sign,round,normalised,zero;
wire [8:0] exponent,sumexponent;
wire [22:0] productmantissa;
wire [23:0] opa,opb;
wire [47:0] product,productnormalised; 


assign sign = a[31] ^ b[31];   													
assign exception = (&a[30:23]) | (&b[30:23]);											
																

assign opa = (|a[30:23]) ? {1'b1,a[22:0]} : {1'b0,a[22:0]};
assign opb = (|b[30:23]) ? {1'b1,b[22:0]} : {1'b0,b[22:0]};

assign product = opa * opb;													
assign round = |productnormalised[22:0];  											
assign normalised = product[47] ? 1'b1 : 1'b0;	
assign productnormalised = normalised ? product : product << 1;								
assign productmantissa = productnormalised[46:24] + (productnormalised[23] & round); 					
assign zero = exception ? 1'b0 : (productmantissa == 23'd0) ? 1'b1 : 1'b0;
assign sumexponent = a[30:23] + b[30:23];
assign exponent = sumexponent - 8'd127 + normalised;
assign overflow = ((exponent[8] & !exponent[7]) & !zero) ; 									
assign underflow = ((exponent[8] & exponent[7]) & !zero) ? 1'b1 : 1'b0; 							
assign res = exception ? 32'd0 : zero ? {sign,31'd0} : overflow ? {sign,8'hFF,23'd0} : underflow ? {sign,31'd0} : {sign,exponent[7:0],productmantissa};

endmodule





