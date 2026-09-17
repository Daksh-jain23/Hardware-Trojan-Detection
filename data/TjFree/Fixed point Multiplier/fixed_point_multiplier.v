module qmult #(
	//Parameterized values
	parameter Q = 15,
	parameter N = 32
	)
	(
	 input			[N-1:0]	i_multiplicand,
	 input			[N-1:0]	i_multiplier,
	 output			[N-1:0]	o_result,
	 output	reg				ovr
	 );
	 
	
	
	reg [2*N-1:0]	r_result;		
											
	reg [N-1:0]		r_RetVal;
	

	assign o_result = r_RetVal;	
	
	always @(i_multiplicand, i_multiplier)	begin						
		r_result <= i_multiplicand[N-2:0] * i_multiplier[N-2:0];	
																
		ovr <= 1'b0;															
		end
	
		
	always @(r_result) begin													
		r_RetVal[N-1] <= i_multiplicand[N-1] ^ i_multiplier[N-1];	
		r_RetVal[N-2:0] <= r_result[N-2+Q:Q];								
																						
		if (r_result[2*N-2:N-1+Q] > 0)										
			ovr <= 1'b1;
		end

endmodule
