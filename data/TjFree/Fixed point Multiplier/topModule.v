module top #(
	
	parameter Q = 15,
	parameter N = 32
	)
	(
	 input			[N-1:0]	imultiplicand,
	 input			[N-1:0]	imultiplier,
	 output			[N-1:0]	oresult,
	 output	reg				ovr
	 );
	 
	
	
	reg [2*N-1:0]	rresult;		
											
	reg [N-1:0]		rRetVal;
	

	assign oresult = rRetVal;	
	
	always @(imultiplicand, imultiplier)	begin						
		rresult <= imultiplicand[N-2:0] * imultiplier[N-2:0];	
																
		ovr <= 1'b0;															
		end
	
		
	always @(rresult) begin													
		rRetVal[N-1] <= imultiplicand[N-1] ^ imultiplier[N-1];	
		rRetVal[N-2:0] <= rresult[N-2+Q:Q];								
																						
		if (rresult[2*N-2:N-1+Q] > 0)										
			ovr <= 1'b1;
		end

endmodule


