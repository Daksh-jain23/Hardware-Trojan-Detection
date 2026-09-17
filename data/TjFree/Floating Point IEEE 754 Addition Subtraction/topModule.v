module priorityencoder(
			input [24:0] significand,
			input [7:0] expa,
			output reg [24:0] Significand,
			output [7:0] expsub
			);

reg [4:0] shift;

always @(significand)
begin
	casex (significand)
		25'b11xxxxxxxxxxxxxxxxxxxxxxx :	begin
													Significand = significand;
									 				shift = 5'd0;
								 			  	end
		25'b101xxxxxxxxxxxxxxxxxxxxxx : 	begin						
										 			Significand = significand << 1;
									 				shift = 5'd1;
								 			  	end

		25'b1001xxxxxxxxxxxxxxxxxxxxx : 	begin						
										 			Significand = significand << 2;
									 				shift = 5'd2;
								 				end

		25'b10001xxxxxxxxxxxxxxxxxxxx : 	begin 							
													Significand = significand << 3;
								 	 				shift = 5'd3;
								 				end

		25'b100001xxxxxxxxxxxxxxxxxxx : 	begin						
									 				Significand = significand << 4;
								 	 				shift = 5'd4;
								 				end

		25'b1000001xxxxxxxxxxxxxxxxxx : 	begin						
									 				Significand = significand << 5;
								 	 				shift = 5'd5;
								 				end

		25'b10000001xxxxxxxxxxxxxxxxx : 	begin						
									 				Significand = significand << 6;
								 	 				shift = 5'd6;
								 				end

		25'b100000001xxxxxxxxxxxxxxxx : 	begin						
									 				Significand = significand << 7;
								 	 				shift = 5'd7;
								 				end

		25'b1000000001xxxxxxxxxxxxxxx : 	begin						
									 				Significand = significand << 8;
								 	 				shift = 5'd8;
								 				end

		25'b10000000001xxxxxxxxxxxxxx : 	begin						
									 				Significand = significand << 9;
								 	 				shift = 5'd9;
								 				end

		25'b100000000001xxxxxxxxxxxxx : 	begin						
									 				Significand = significand << 10;
								 	 				shift = 5'd10;
								 				end

		25'b1000000000001xxxxxxxxxxxx : 	begin						
									 				Significand = significand << 11;
								 	 				shift = 5'd11;
								 				end

		25'b10000000000001xxxxxxxxxxx : 	begin						
									 				Significand = significand << 12;
								 	 				shift = 5'd12;
								 				end

		25'b100000000000001xxxxxxxxxx : 	begin						
									 				Significand = significand << 13;
								 	 				shift = 5'd13;
								 				end

		25'b1000000000000001xxxxxxxxx : 	begin						
									 				Significand = significand << 14;
								 	 				shift = 5'd14;
								 				end

		25'b10000000000000001xxxxxxxx  : 	begin						
									 				Significand = significand << 15;
								 	 				shift = 5'd15;
								 				end

		25'b100000000000000001xxxxxxx : 	begin						
									 				Significand = significand << 16;
								 	 				shift = 5'd16;
								 				end

		25'b1000000000000000001xxxxxx : 	begin						
											 		Significand = significand << 17;
										 	 		shift = 5'd17;
												end

		25'b10000000000000000001xxxxx : 	begin						
									 				Significand = significand << 18;
								 	 				shift = 5'd18;
								 				end

		25'b100000000000000000001xxxx : 	begin						
									 				Significand = significand << 19;
								 	 				shift = 5'd19;
												end

		25'b1000000000000000000001xxx :	begin						
									 				Significand = significand << 20;
								 					shift = 5'd20;
								 				end

		25'b10000000000000000000001xx : 	begin						
									 				Significand = significand << 21;
								 	 				shift = 5'd21;
								 				end

		25'b100000000000000000000001x : 	begin						
									 				Significand = significand << 22;
								 	 				shift = 5'd22;
								 				end

		25'b1000000000000000000000001 : 	begin						
									 				Significand = significand << 23;
								 	 				shift = 5'd23;
								 				end

		25'b1000000000000000000000000 : 	begin						
								 					Significand = significand << 24;
							 	 					shift = 5'd24;
								 				end
		default : 	begin
						Significand = (~significand) + 1'b1;
						shift = 8'd0;
					end

	endcase
end
assign expsub = expa - shift;

endmodule

module top(input [31:0] a,b,
input addsubsignal,														
output exception,
output [31:0] res );

wire operationaddsubsignal;
wire enable;
wire outputsign;

wire [31:0] opa,opb;
wire [23:0] significanda,significandb;
wire [7:0] expdiff;


wire [23:0] significandbaddsub;
wire [7:0] expbaddsub;

wire [24:0] significandadd;
wire [30:0] addsum;

wire [23:0] significandsubcomplement;
wire [24:0] significandsub;
wire [30:0] subdiff;
wire [24:0] subtractiondiff; 
wire [7:0] expsub;

assign {enable,opa,opb} = (a[30:0] < b[30:0]) ? {1'b1,b,a} : {1'b0,a,b};							

assign expa = opa[30:23];
assign expb = opb[30:23];

assign exception = (&opa[30:23]) | (&opb[30:23]);										

assign outputsign = addsubsignal ? enable ? !opa[31] : opa[31] : opa[31] ;

assign operationaddsubsignal = addsubsignal ? opa[31] ^ opb[31] : ~(opa[31] ^ opb[31]);
																
assign significanda = (|opa[30:23]) ? {1'b1,opa[22:0]} : {1'b0,opa[22:0]};							
assign significandb = (|opb[30:23]) ? {1'b1,opb[22:0]} : {1'b0,opb[22:0]};

assign expdiff = opa[30:23] - opb[30:23];											
assign significandbaddsub = significandb >> expdiff;
assign expbaddsub = opb[30:23] + expdiff; 

assign perform = (opa[30:23] == expbaddsub);										


assign significandadd = (perform & operationaddsubsignal) ? (significanda + significandbaddsub) : 25'd0; 

assign addsum[22:0] = significandadd[24] ? significandadd[23:1] : significandadd[22:0];					

assign addsum[30:23] = significandadd[24] ? (1'b1 + opa[30:23]) : opa[30:23];						

assign significandsubcomplement = (perform & !operationaddsubsignal) ? ~(significandbaddsub) + 24'd1 : 24'd0 ; 

assign significandsub = perform ? (significanda + significandsubcomplement) : 25'd0;

priorityencoder pe(significandsub,opa[30:23],subtractiondiff,expsub);

assign subdiff[30:23] = expsub;

assign subdiff[22:0] = subtractiondiff[22:0];

assign res = exception ? 32'b0 : ((!operationaddsubsignal) ? {outputsign,subdiff} : {outputsign,addsum});

endmodule




