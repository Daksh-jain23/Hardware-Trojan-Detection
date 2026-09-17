module non_restoring_div(clk, reset, Dividend, Divisor, Quotient, Remainder);
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
			//Shift Left carrying a's MSB into p's LSB
			p = (p << 1) | a[63];
			a = a << 1;

			//Check the old value of p
			if( p[63] ) //if p is negative
				temp = Divisor; //add divisor
			else
				temp = ~Divisor+1; //subtract divisor

			//this will do the appropriate add or subtract
			//depending on the value of temp
			p = p + temp;

			//Check the new value of p
			if( p[63] ) // if p is negative
				a = a | 0; //no change to quotient
			else
				a = a | 1; 
		end

		//Correction is needed if remainder is negative
		if( p[63] ) //if p is negative
			p = p + Divisor;
	end
				
endmodule


