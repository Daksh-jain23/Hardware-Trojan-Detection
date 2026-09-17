module top(clk, reset, Dividend, Divisor, Quotient, Remainder);
	input clk, reset;
	input [63:0] Dividend, Divisor;

	output [63:0] Quotient, Remainder;
	reg [63:0] Quotient, Remainder;

	reg [63:0] p, a, temp;
	integer i;

	always @(posedge clk, negedge reset)
	begin
		if( !reset )
		begin
			Quotient <= 0;
			Remainder <= 0;
		end
		else
		begin
			Quotient <= a;
			Remainder <= p;
		end
	end

	always @(*)
	begin
		a = Dividend;
		p = 0;

		for(i = 0; i < 64; i = i+1)
		begin
			
			p = (p << 1) | a[63];
			a = a << 1;

			
			temp = p;

			
			p = p - Divisor;

			if( p[63] ) 
				p = temp; 
			else
				a = a | 1;
		end	
	end
				
endmodule
	



