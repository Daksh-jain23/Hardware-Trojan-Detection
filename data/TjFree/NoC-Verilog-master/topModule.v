module Buffer (output [63:0] bfout, 
			   output reg [2:0] empl, 
			   input clk, reset, pop, push, input [63:0] bfin);
  
  reg [63:0] bf [0:3];
  reg [1:0] addwr;
  reg [1:0] addrd;
  
  assign bfout = bf[addrd];
  
  always @(posedge clk)
  begin
    if(reset)
    begin
      bf[0] <= 64'b0;
      bf[1] <= 64'b0;
      bf[2] <= 64'b0;
      bf[3] <= 64'b0;
      empl = 3'd4;
      addwr = 0;
      addrd = 0;
    end
    else
    begin
      if(push == 1 && pop == 0 && empl > 3'd0)
      begin
        bf[addwr] <= bfin;
        empl = empl - 1;
        addwr = addwr + 1;
      end
      else if(push == 0 && pop == 1 && empl < 3'd4)
      begin
        empl = empl + 1;
        addrd = addrd + 1;
      end
      else if(push == 1 && pop == 1)
      begin
        if(empl == 3'd4)
        begin
          bf[addwr] <= bfin;
          addwr = addwr + 1;
          empl = empl - 1;
        end
        else
        begin
          bf[addwr] <= bfin;
          addwr = addwr + 1;
          addrd = addrd + 1;
        end
      end
    end
    
  end
  
endmodule
module Counter(output reg [2:0] c, input reset, clk, en);
  
  always @(posedge clk)
  begin
    if(reset)
      c = 3'd0;
    else
    begin
      if(en == 1)
        c = c + 1;
      if(c == 3'd5)
        c = 0;
    end
  end
  
endmodule
module CrossBar (output reg [63:0] OE,OW,ON,OS,Eject, input [2:0] SE, SW, SN, SS, SEjec, input [63:0] IE, IW, IN, IS, Inject);
  
  always @(*)
  begin
    case (SE)
      3'd0: OE = IE;
      3'd1: OE = IW;
      3'd2: OE = IN;
      3'd3: OE = IS;
      3'd4: OE = Inject;
      default:
        OE = 64'b0;
    endcase
    
    case (SW)
      3'd0: OW = IE;
      3'd1: OW = IW;
      3'd2: OW = IN;
      3'd3: OW = IS;
      3'd4: OW = Inject;
      default:
        OW = 64'b0;
    endcase
    
    case (SN)
      3'd0: ON = IE;
      3'd1: ON = IW;
      3'd2: ON = IN;
      3'd3: ON = IS;
      3'd4: ON = Inject;
      default:
        ON = 64'b0;
    endcase
    
    case (SS)
      3'd0: OS = IE;
      3'd1: OS = IW;
      3'd2: OS = IN;
      3'd3: OS = IS;
      3'd4: OS = Inject;
      default:
        OS = 64'b0;
    endcase
    
    case (SEjec)
      3'd0: Eject = IE;
      3'd1: Eject = IW;
      3'd2: Eject = IN;
      3'd3: Eject = IS;
      3'd4: Eject = Inject;
      default:
        Eject = 64'b0;
    endcase
    
  end
  
endmodule
module inputUnit(output [63:0] bfout,  
				  output reg en, 
				  output [2:0] empl, 
				  output reg [2:0] outnum, 
				  output reg PW, vcg, vcf, pusho,
                  input clk, reset, pushx, PWfail, vcgrant, STack, 
				  input [63:0] bfin, input [2:0] Xcur, Ycur, inchannel, output reg pushack);
  
  wire [4:0] validout, status;
  reg [2:0] Xdest, Ydest;

  reg Pri;
  reg pop;
  reg push;
  
  reg [2:0] state;
  reg [2:0] nextstate;
  
  always @(posedge clk)
  begin
   
   
  end
  
  always @(posedge clk)
  begin
    if(reset)
      state <= 3'b0;
    else
      state <= nextstate;
  end
  
  always @(*)
  begin
    case (state)
      3'b000:
      begin
        if(vcgrant == 0)
          nextstate = 3'b0;
        else
          nextstate = 3'b1;
      end
      3'b001:
      begin
        if(STack)
          nextstate = 3'b010;
        else
          nextstate = 3'b001;
      end
      3'b010: nextstate = 3'b011;
      3'b011: nextstate = 3'b100;
      3'b100: nextstate = 3'b101;
      3'b101: nextstate = 3'b110;
      3'b110: nextstate = 3'b000;
    endcase
  end
  
  always @(*)
  begin
    case (state)
      3'b000: 
      begin
        {vcf,pusho,pop} = 3'b100;
        if(vcgrant == 1)
          vcf = 0;
      end
      3'b001: {vcf,pusho,pop} = 3'b000;
      3'b010: {vcf,pusho,pop} = 3'b011;
      3'b011: {vcf,pusho,pop} = 3'b011;
      3'b100: {vcf,pusho,pop} = 3'b011;
      3'b101: {vcf,pusho,pop} = 3'b011;
      3'b110: {vcf,pusho,pop} = 3'b100;
    endcase
  end
      
  
  Buffer bf (bfout, empl, clk, reset, pop, push, bfin);
  RouteFunc RF(validout, status, Xcur, Ycur, Xdest, Ydest, inchannel, reset);
  
  
  
  always @(*)
  begin
	if (reset)
	begin
		push = 0;
		pushack = 0;
	end
	else
	begin
		push = 0;
		pushack = 0;
		if(bfin[63:62] == 2'b11 && empl == 3'd4)
		begin
			push = pushx;
			pushack = pushx;
		end
		else if(bfin[63:62] == 2'b01 || bfin[63:62] == 2'b10)
		begin
			push = pushx;
			pushack = pushx;
		end
	end
  end
  
  always @(*)
  begin
	if (reset)
		en=0;
	else
	begin
		en = 0;
		if(bfout[63:62] == 2'b11 && empl < 3'd4)  
		begin
			Xdest = bfout[8:6];
			Ydest = bfout[11:9];
			en = 1;
			Pri = Pri + 1;
		end
	end
  end
  
  always @(posedge clk)
  begin
    if(reset)
    begin
      vcg = 0;
    end
    else
    begin
      if(bfout[63:62] == 2'b11)
      begin
        vcg = vcgrant;
      end
    end
  end 
  
/*  always @(posedge clk)
  begin
    if(reset)
    begin
      pop = 1'b0;
      pusho = 1'b0;
  
    end
    else
    begin
      pop = STack & vcgrant;
      pusho = STack & vcgrant;
    end
    if(bfout[63:62] == 2'b11 && empl < 3'd4) 
    begin
      if(vcgrant)
        vcf = 0; 
    end
    else if(bfout[63:62] == 2'b10)
    begin
      if(STack == 1 && vcgrant == 1)
      begin
        vcf = 1;
        pusho = 0;
      end
    end
    if(empl == 3'd4)
    begin
      pop = 1'b0;
      pusho = 1'b0;
      vcf = 1'b1;
    end
  end*/

  always @(*)
  begin
	if(reset)
	begin
		PW = 0;
		outnum=5;
    end
	else
	case (validout)
      5'b10000:
        outnum = 4;
      5'b01000:
        outnum = 3;
      5'b00100:
        outnum = 2;
      5'b00010:
        outnum = 1;
      5'b00001:
        outnum = 0;
      5'b00101:
      begin
        if(status[0] == 1)
        begin
          if(PWfail == 0)
          begin
            outnum = 0;
            PW = 1;
          end
          else
          begin
            outnum = 2;
            PW = 0;
          end
        end
        else if(status[2] == 1)
        begin
          if(PWfail == 0)
          begin
            outnum = 2;
            PW = 1;
          end
          else
          begin
            outnum = 0;
            PW = 0;
          end
        end
        else
        begin
          PW = 0;
          if(Pri == 0)
            outnum = 0;         
          else
            outnum = 2;
        end
      end
      
      5'b00110:
      begin
        if(status[1] == 1)
        begin
          if(PWfail == 0)
          begin
            outnum = 1;
            PW = 1;
          end
          else
          begin
            outnum = 2;
            PW = 0;
          end
        end
        else if(status[2] == 1)
        begin
          if(PWfail == 0)
          begin
            outnum = 2;
            PW = 1;
          end
          else
          begin
            outnum = 1;
            PW = 0;
          end
        end
        else
        begin
          PW = 0;
          if(Pri == 0)
            outnum = 1;         
          else
            outnum = 2;
        end
      end
      
      5'b01001:
      begin
        if(status[0] == 1)
        begin
          if(PWfail == 0)
          begin
            outnum = 0;
            PW = 1;
          end
          else
          begin
            outnum = 3;
            PW = 0;
          end
        end
        else if(status[3] == 1)
        begin
          if(PWfail == 0)
          begin
            outnum = 3;
            PW = 1;
          end
          else
          begin
            outnum = 0;
            PW = 0;
          end
        end
        else
        begin
          PW = 0;
          if(Pri == 0)
            outnum = 0;         
          else
            outnum = 3;
        end
      end
      
      5'b01010:
      begin
        if(status[1] == 1)
        begin
          if(PWfail == 0)
          begin
            outnum = 1;
            PW = 1;
          end
          else
          begin
            outnum = 3;
            PW = 0;
          end
        end
        else if(status[3] == 1)
        begin
          if(PWfail == 0)
          begin
            outnum = 3;
            PW = 1;
          end
          else
          begin
            outnum = 1;
            PW = 0;
          end
        end
        else
        begin
          PW = 0;
          if(Pri == 0)
            outnum = 1;         
          else
            outnum = 3;
        end
      end
      
      default:
      begin
        PW = 0;
        outnum = 5;
      end
            
    endcase
  end
  
  
    
  
  
  
endmodule
module top (input clk, reset,
                input [63:0] inj0, inj1, inj2, inj3, inj4, inj5, inj6, inj7, inj8, inj9, inj10, inj11, inj12, inj13, inj14, inj15, 
                             inj16, inj17, inj18, inj19, inj20, inj21, inj22, inj23, inj24, inj25, inj26, inj27, inj28, inj29, inj30, inj31,
                             inj32, inj33, inj34, inj35, inj36, inj37, inj38, inj39, inj40, inj41, inj42, inj43, inj44, inj45, inj46, inj47,
                             inj48, inj49, inj50, inj51, inj52, inj53, inj54, inj55, inj56, inj57, inj58, inj59, inj60, inj61, inj62, inj63,
                output [63:0] ej0, ej1, ej2, ej3, ej4, ej5, ej6, ej7, ej8, ej9, ej10, ej11, ej12, ej13, ej14, ej15, 
                             ej16, ej17, ej18, ej19, ej20, ej21, ej22, ej23, ej24, ej25, ej26, ej27, ej28, ej29, ej30, ej31,
                             ej32, ej33, ej34, ej35, ej36, ej37, ej38, ej39, ej40, ej41, ej42, ej43, ej44, ej45, ej46, ej47,
                             ej48, ej49, ej50, ej51, ej52, ej53, ej54, ej55, ej56, ej57, ej58, ej59, ej60, ej61, ej62, ej63,
                input [63:0] pushj,
                output [63:0] writereqj, 
                output [63:0] je,
                input [63:0] wjack,
                output [63:0] pushjack);
  
 /* wire [63:0] east, west;
  wire pushw, estate, writereqe, we;
  wire pushwack, weack;*/
  
  wire [63:0] east [0:63];
  wire [63:0] west [0:63];
  wire [63:0] north [0:63];
  wire [63:0] south [0:63];
  
  wire Een [0:63];
  wire Wen [0:63];
  wire Nen [0:63];
  wire Sen [0:63];
  
  wire Ereq [0:63];
  wire Wreq [0:63];
  wire Nreq [0:63];
  wire Sreq [0:63];
  
  wire Eack [0:63];
  wire Wack [0:63];
  wire Nack [0:63];
  wire Sack [0:63];
  
/*ProcessNode (input endsim, input [2:0] Xcur, Ycur, input [63:0] ie, iw, in, is, input clk, reset, pushe, pushw, pushn, pushs,
                     estate, wstate, nstate, sstate, output [63:0] oe, ow, on, os, output writereqe, writereqw, writereqn, writereqs, 
                     ee, we, ne, se,
                     input weack, wwack, wnack, wsack, output pusheack, pushwack, pushnack, pushsack);*/ 
  
  
  ProcessNode p0(3'b000, 3'b000,west[0], south[0], clk, reset, Wreq[0], Sreq[0], Een[0],  Nen[0], east[0], north[0], Ereq[0],  Nreq[0],  Wen[0],  Sen[0], Eack[0], Nack[0]  , Wack[0], Sack[0], inj0, pushj[0], wjack[0], writereqj[0], je[0], pushjack[0], ej0);
  
  
  ProcessNode p1(3'b001, 3'b000, east[0], west[1], south[8],  clk, reset, Ereq[0], Wreq[1], Sreq[8], Een[1], Wen[0], Nen[8], east[1], west[0], north[8], Ereq[1], Wreq[0], Nreq[8], Een[0], Wen[1], Sen[8], Eack[1], Wack[0], Nack[8], Eack[0], Wack[1], Sack[8], inj1, pushj[1], wjack[1], writereqj[1], je[1], pushjack[1], ej1);
                  
  ProcessNode p2(3'b010, 3'b000, east[1], west[2], south[16],  clk, reset, Ereq[1], Wreq[2], Sreq[16], Een[2], Wen[1], Nen[16], east[2], west[1], north[16], Ereq[2], Wreq[1], Nreq[16], Een[1], Wen[2], Sen[16], Eack[2], Wack[1], Nack[16], Eack[1], Wack[2], Sack[16], inj2, pushj[2], wjack[2], writereqj[2], je[2], pushjack[2], ej2);
  
  ProcessNode p3(3'b011, 3'b000, east[2], west[3], south[24],  clk, reset, Ereq[2], Wreq[3], Sreq[24], Een[3], Wen[2], Nen[24], east[3], west[2], north[24], Ereq[3], Wreq[2], Nreq[24], Een[2], Wen[3], Sen[24], Eack[3], Wack[2], Nack[24], Eack[2], Wack[3], Sack[24], inj3, pushj[3], wjack[3], writereqj[3], je[3], pushjack[3], ej3);  
  
  ProcessNode p4(3'b100, 3'b000, east[3], west[4], south[32],  clk, reset, Ereq[3], Wreq[4], Sreq[32], Een[4], Wen[3], Nen[32], east[4], west[3], north[32], Ereq[4], Wreq[3], Nreq[32], Een[3], Wen[4], Sen[32], Eack[4], Wack[3], Nack[32], Eack[3], Wack[4], Sack[32], inj4, pushj[4], wjack[4], writereqj[4], je[4], pushjack[4], ej4);
  
  ProcessNode p5(3'b101, 3'b000, east[4], west[5], south[40],  clk, reset, Ereq[4], Wreq[5], Sreq[40], Een[5], Wen[4], Nen[40], east[5], west[4], north[40], Ereq[5], Wreq[4], Nreq[40], Een[4], Wen[5], Sen[40], Eack[5], Wack[4], Nack[40], Eack[4], Wack[5], Sack[40], inj5, pushj[5], wjack[5], writereqj[5], je[5], pushjack[5], ej5);  
  
  ProcessNode p6(3'b110, 3'b000, east[5], west[6], south[48],  clk, reset, Ereq[5], Wreq[6], Sreq[48], Een[6], Wen[5], Nen[48], east[6], west[5], north[48], Ereq[6], Wreq[5], Nreq[48], Een[5], Wen[6], Sen[48], Eack[6], Wack[5], Nack[48], Eack[5], Wack[6], Sack[48], inj6, pushj[6], wjack[6], writereqj[6], je[6], pushjack[6], ej6);  
  
  ProcessNode p7(3'b111, 3'b000, east[6], west[7], south[56],  clk, reset, Ereq[6], Wreq[7], Sreq[56], Een[7], Wen[6], Nen[56], east[7], west[6], north[56], Ereq[7], Wreq[6], Nreq[56], Een[6], Wen[7], Sen[56], Eack[7], Wack[6], Nack[56], Eack[6], Wack[7], Sack[56], inj7, pushj[7], wjack[7], writereqj[7], je[7], pushjack[7], ej7);  
  
  ProcessNode p8(3'b000, 3'b001, west[8], north[0], south[1],  clk, reset, Wreq[8], Nreq[0], Sreq[1], Een[8], Nen[1], Sen[0],  east[8],north[1] ,south[0] , Ereq[8], Nreq[1], Sreq[0], Wen[8], Nen[0], Sen[1], Eack[8], Nack[1], Sack[0], Wack[8], Nack[0], Sack[1], inj8, pushj[8], wjack[8], writereqj[8], je[8], pushjack[8], ej8);
  
  ProcessNode p9( 3'b001, 3'b001, east[8], west[9], north[8], south[9],  clk, reset, Ereq[8], Wreq[9], Nreq[8], Sreq[9], Een[9], Wen[8], Nen[9], Sen[8], east[9], west[8], north[9], south[8], Ereq[9], Wreq[8], Nreq[9], Sreq[8], Een[8], Wen[9], Nen[8], Sen[9], Eack[9], Wack[8], Nack[9], Sack[8], Eack[8], Wack[9], Nack[8], Sack[9], inj9, pushj[9], wjack[9], writereqj[9], je[9], pushjack[9], ej9);
                  
  ProcessNode p10( 3'b010, 3'b001, east[9], west[10], north[16], south[17], clk, reset, Ereq[9], Wreq[10], Nreq[16], Sreq[17], Een[10], Wen[9], Nen[17], Sen[16], east[10], west[9], north[17], south[16], Ereq[10], Wreq[9], Nreq[17], Sreq[16], Een[9], Wen[10], Nen[16], Sen[17], Eack[10], Wack[9], Nack[17], Sack[16], Eack[9], Wack[10], Nack[16], Sack[17], inj10, pushj[10], wjack[10], writereqj[10], je[10], pushjack[10], ej10);
  
  ProcessNode p11( 3'b011, 3'b001, east[10], west[11], north[24], south[25], clk, reset, Ereq[10], Wreq[11], Nreq[24], Sreq[25], Een[11], Wen[10], Nen[25], Sen[24], east[11], west[10], north[25], south[24], Ereq[11], Wreq[10], Nreq[25], Sreq[24], Een[10], Wen[11], Nen[24], Sen[25], Eack[11], Wack[10], Nack[25], Sack[24], Eack[10], Wack[11], Nack[24], Sack[25], inj11, pushj[11], wjack[11], writereqj[11], je[11], pushjack[11], ej11);  
  
  ProcessNode p12( 3'b100, 3'b001, east[11], west[12], north[32], south[33], clk, reset, Ereq[11], Wreq[12], Nreq[32], Sreq[33], Een[12], Wen[11], Nen[33], Sen[32], east[12], west[11], north[33], south[32], Ereq[12], Wreq[11], Nreq[33], Sreq[32], Een[11], Wen[12], Nen[32], Sen[33], Eack[12], Wack[11], Nack[33], Sack[32], Eack[11], Wack[12], Nack[32], Sack[33], inj12, pushj[12], wjack[12], writereqj[12], je[12], pushjack[12], ej12);
  
  ProcessNode p13( 3'b101, 3'b001, east[12], west[13], north[40], south[41], clk, reset, Ereq[12], Wreq[13], Nreq[40], Sreq[41], Een[13], Wen[12], Nen[41], Sen[40], east[13], west[12], north[41], south[40], Ereq[13], Wreq[12], Nreq[41], Sreq[40], Een[12], Wen[13], Nen[40], Sen[41], Eack[13], Wack[12], Nack[41], Sack[40], Eack[12], Wack[13], Nack[40], Sack[41], inj13, pushj[13], wjack[13], writereqj[13], je[13], pushjack[13], ej13);  
  
  ProcessNode p14( 3'b110, 3'b001, east[13], west[14], north[48], south[49], clk, reset, Ereq[13], Wreq[14], Nreq[48], Sreq[49], Een[14], Wen[13], Nen[49], Sen[48], east[14], west[13], north[49], south[48], Ereq[14], Wreq[13], Nreq[49], Sreq[48], Een[13], Wen[14], Nen[48], Sen[49], Eack[14], Wack[13], Nack[49], Sack[48], Eack[13], Wack[14], Nack[48], Sack[49], inj14, pushj[14], wjack[14], writereqj[14], je[14], pushjack[14], ej14);  
  
  ProcessNode p15( 3'b111, 3'b001, east[14], west[15], north[56], south[57], clk, reset, Ereq[14], Wreq[15], Nreq[56], Sreq[57], Een[15], Wen[14], Nen[57], Sen[56], east[15], west[14], north[57], south[56], Ereq[15], Wreq[14], Nreq[57], Sreq[56], Een[14], Wen[15], Nen[56], Sen[57], Eack[15], Wack[14], Nack[57], Sack[56], Eack[14], Wack[15], Nack[56], Sack[57], inj15, pushj[15], wjack[15], writereqj[15], je[15], pushjack[15], ej15);  
  
  ProcessNode p16( 3'b000, 3'b010, west[16], north[1], south[2],  clk, reset, Wreq[16], Nreq[1], Sreq[2], Een[16], Nen[2], Sen[1],  east[16], north[2], south[1], Ereq[16], Nreq[2], Sreq[1], Wen[16], Nen[1], Sen[2], Eack[16], Nack[2], Sack[1], Wack[16], Nack[1], Sack[2], inj16, pushj[16], wjack[16], writereqj[16], je[16], pushjack[16], ej16);
  
  ProcessNode p17( 3'b001, 3'b010, east[16], west[17], north[9], south[10],  clk, reset, Ereq[16], Wreq[17], Nreq[9], Sreq[10], Een[17], Wen[16], Nen[10], Sen[9], east[17], west[16], north[10], south[9], Ereq[17], Wreq[16], Nreq[10], Sreq[9], Een[16], Wen[17], Nen[9], Sen[10], Eack[17], Wack[16], Nack[10], Sack[9], Eack[16], Wack[17], Nack[9], Sack[10], inj17, pushj[17], wjack[17], writereqj[17], je[17], pushjack[17], ej17);
                  
  ProcessNode p18( 3'b010, 3'b010, east[17], west[18], north[17], south[18], clk, reset, Ereq[17], Wreq[18], Nreq[17], Sreq[18], Een[18], Wen[17], Nen[18], Sen[17], east[18], west[17], north[18], south[17], Ereq[18], Wreq[17], Nreq[18], Sreq[17], Een[17], Wen[18], Nen[17], Sen[18], Eack[18], Wack[17], Nack[18], Sack[17], Eack[17], Wack[18], Nack[17], Sack[18], inj18, pushj[18], wjack[18], writereqj[18], je[18], pushjack[18], ej18);
  
  ProcessNode p19( 3'b011, 3'b010, east[18], west[19], north[25], south[26], clk, reset, Ereq[18], Wreq[19], Nreq[25], Sreq[26], Een[19], Wen[18], Nen[26], Sen[25], east[19], west[18], north[26], south[25], Ereq[19], Wreq[18], Nreq[26], Sreq[25], Een[18], Wen[19], Nen[25], Sen[26], Eack[19], Wack[18], Nack[26], Sack[25], Eack[18], Wack[19], Nack[25], Sack[26], inj19, pushj[19], wjack[19], writereqj[19], je[19], pushjack[19], ej19);  
  
  ProcessNode p20( 3'b100, 3'b010, east[19], west[20], north[33], south[34], clk, reset, Ereq[19], Wreq[20], Nreq[33], Sreq[34], Een[20], Wen[19], Nen[34], Sen[33], east[20], west[19], north[34], south[33], Ereq[20], Wreq[19], Nreq[34], Sreq[33], Een[19], Wen[20], Nen[33], Sen[34], Eack[20], Wack[19], Nack[34], Sack[33], Eack[19], Wack[20], Nack[33], Sack[34], inj20, pushj[20], wjack[20], writereqj[20], je[20], pushjack[20], ej20);
  
  ProcessNode p21( 3'b101, 3'b010, east[20], west[21], north[41], south[42], clk, reset, Ereq[20], Wreq[21], Nreq[41], Sreq[42], Een[21], Wen[20], Nen[42], Sen[41], east[21], west[20], north[42], south[41], Ereq[21], Wreq[20], Nreq[42], Sreq[41], Een[20], Wen[21], Nen[41], Sen[42], Eack[21], Wack[20], Nack[42], Sack[41], Eack[20], Wack[21], Nack[41], Sack[42], inj21, pushj[21], wjack[21], writereqj[21], je[21], pushjack[21], ej21);  
  
  ProcessNode p22( 3'b110, 3'b010, east[21], west[22], north[49], south[50], clk, reset, Ereq[21], Wreq[22], Nreq[49], Sreq[50], Een[22], Wen[21], Nen[50], Sen[49], east[22], west[21], north[50], south[49], Ereq[22], Wreq[21], Nreq[50], Sreq[49], Een[21], Wen[22], Nen[49], Sen[50], Eack[22], Wack[21], Nack[50], Sack[49], Eack[21], Wack[22], Nack[49], Sack[50], inj22, pushj[22], wjack[22], writereqj[22], je[22], pushjack[22], ej22);  
  
  ProcessNode p23( 3'b111, 3'b010, east[22], west[23], north[57], south[58], clk, reset, Ereq[22], Wreq[23], Nreq[57], Sreq[58], Een[23], Wen[22], Nen[58], Sen[57], east[23], west[22], north[58], south[57], Ereq[23], Wreq[22], Nreq[58], Sreq[57], Een[22], Wen[23], Nen[57], Sen[58], Eack[23], Wack[22], Nack[58], Sack[57], Eack[22], Wack[23], Nack[57], Sack[58], inj23, pushj[23], wjack[23], writereqj[23], je[23], pushjack[23], ej23);  
  
  ProcessNode p24( 3'b000, 3'b011, west[24], north[2], south[3],  clk, reset, Wreq[24], Nreq[2], Sreq[3], Een[24], Nen[3], Sen[2], east[24], north[3], south[2], Ereq[24], Nreq[3], Sreq[2], Wen[24], Nen[2], Sen[3], Eack[24], Nack[3], Sack[2], Wack[24], Nack[2], Sack[3], inj24, pushj[24], wjack[24], writereqj[24], je[24], pushjack[24], ej24);
  
  ProcessNode p25( 3'b001, 3'b011, east[24], west[25], north[10], south[11],  clk, reset, Ereq[24], Wreq[25], Nreq[10], Sreq[11], Een[25], Wen[24], Nen[11], Sen[10], east[25], west[24], north[11], south[10], Ereq[25], Wreq[24], Nreq[11], Sreq[10], Een[24], Wen[25], Nen[10], Sen[11], Eack[25], Wack[24], Nack[11], Sack[10], Eack[24], Wack[25], Nack[10], Sack[11], inj25, pushj[25], wjack[25], writereqj[25], je[25], pushjack[25], ej25);
                  
  ProcessNode p26( 3'b010, 3'b011, east[25], west[26], north[18], south[19], clk, reset, Ereq[25], Wreq[26], Nreq[18], Sreq[19], Een[26], Wen[25], Nen[19], Sen[18], east[26], west[25], north[19], south[18], Ereq[26], Wreq[25], Nreq[19], Sreq[18], Een[25], Wen[26], Nen[18], Sen[19], Eack[26], Wack[25], Nack[19], Sack[18], Eack[25], Wack[26], Nack[18], Sack[19], inj26, pushj[26], wjack[26], writereqj[26], je[26], pushjack[26], ej26);
  
  ProcessNode p27( 3'b011, 3'b011, east[26], west[27], north[26], south[27], clk, reset, Ereq[26], Wreq[27], Nreq[26], Sreq[27], Een[27], Wen[26], Nen[27], Sen[26], east[27], west[26], north[27], south[26], Ereq[27], Wreq[26], Nreq[27], Sreq[26], Een[26], Wen[27], Nen[26], Sen[27], Eack[27], Wack[26], Nack[27], Sack[26], Eack[26], Wack[27], Nack[26], Sack[27], inj27, pushj[27], wjack[27], writereqj[27], je[27], pushjack[27], ej27);  
  
  ProcessNode p28( 3'b100, 3'b011, east[27], west[28], north[34], south[35], clk, reset, Ereq[27], Wreq[28], Nreq[34], Sreq[35], Een[28], Wen[27], Nen[35], Sen[34], east[28], west[27], north[35], south[34], Ereq[28], Wreq[27], Nreq[35], Sreq[34], Een[27], Wen[28], Nen[34], Sen[35], Eack[28], Wack[27], Nack[35], Sack[34], Eack[27], Wack[28], Nack[34], Sack[35], inj28, pushj[28], wjack[28], writereqj[28], je[28], pushjack[28], ej28);
  
  ProcessNode p29( 3'b101, 3'b011, east[28], west[29], north[42], south[43], clk, reset, Ereq[28], Wreq[29], Nreq[42], Sreq[43], Een[29], Wen[28], Nen[43], Sen[42], east[29], west[28], north[43], south[42], Ereq[29], Wreq[28], Nreq[43], Sreq[42], Een[28], Wen[29], Nen[42], Sen[43], Eack[29], Wack[28], Nack[43], Sack[42], Eack[28], Wack[29], Nack[42], Sack[43], inj29, pushj[29], wjack[29], writereqj[29], je[29], pushjack[29], ej29);  
  
  ProcessNode p30( 3'b110, 3'b011, east[29], west[30], north[50], south[51], clk, reset, Ereq[29], Wreq[30], Nreq[50], Sreq[51], Een[30], Wen[29], Nen[51], Sen[50], east[30], west[29], north[51], south[50], Ereq[30], Wreq[29], Nreq[51], Sreq[50], Een[29], Wen[30], Nen[50], Sen[51], Eack[30], Wack[29], Nack[51], Sack[50], Eack[29], Wack[30], Nack[50], Sack[51], inj30, pushj[30], wjack[30], writereqj[30], je[30], pushjack[30], ej30);  
  
  ProcessNode p31( 3'b111, 3'b011, east[30], west[31], north[58], south[59], clk, reset, Ereq[30], Wreq[31], Nreq[58], Sreq[59], Een[31], Wen[30], Nen[59], Sen[58], east[31], west[30], north[59], south[58], Ereq[31], Wreq[30], Nreq[59], Sreq[58], Een[30], Wen[31], Nen[58], Sen[59], Eack[31], Wack[30], Nack[59], Sack[58], Eack[30], Wack[31], Nack[58], Sack[59], inj31, pushj[31], wjack[31], writereqj[31], je[31], pushjack[31], ej31);  
  
  ProcessNode p32( 3'b000, 3'b100, west[32], north[3], south[4],  clk, reset, Wreq[32], Nreq[3], Sreq[4], Een[32], Nen[4], Sen[3],  east[32], north[4], south[3], Ereq[32], Nreq[4], Sreq[3], Wen[32], Nen[3], Sen[4], Eack[32], Nack[4], Sack[3], Wack[32], Nack[3], Sack[4], inj32, pushj[32], wjack[32], writereqj[32], je[32], pushjack[32], ej32);
  
  ProcessNode p33( 3'b001, 3'b100, east[32], west[33], north[11], south[12],  clk, reset, Ereq[32], Wreq[33], Nreq[11], Sreq[12], Een[33], Wen[32], Nen[12], Sen[11], east[33], west[32], north[12], south[11], Ereq[33], Wreq[32], Nreq[12], Sreq[11], Een[32], Wen[33], Nen[11], Sen[12], Eack[33], Wack[32], Nack[12], Sack[11], Eack[32], Wack[33], Nack[11], Sack[12], inj33, pushj[33], wjack[33], writereqj[33], je[33], pushjack[33], ej33);
                  
  ProcessNode p34( 3'b010, 3'b100, east[33], west[34], north[19], south[20], clk, reset, Ereq[33], Wreq[34], Nreq[19], Sreq[20], Een[34], Wen[33], Nen[20], Sen[19], east[34], west[33], north[20], south[19], Ereq[34], Wreq[33], Nreq[20], Sreq[19], Een[33], Wen[34], Nen[19], Sen[20], Eack[34], Wack[33], Nack[20], Sack[19], Eack[33], Wack[34], Nack[19], Sack[20], inj34, pushj[34], wjack[34], writereqj[34], je[34], pushjack[34], ej34);
  
  ProcessNode p35( 3'b011, 3'b100, east[34], west[35], north[27], south[28], clk, reset, Ereq[34], Wreq[35], Nreq[27], Sreq[28], Een[35], Wen[34], Nen[28], Sen[27], east[35], west[34], north[28], south[27], Ereq[35], Wreq[34], Nreq[28], Sreq[27], Een[34], Wen[35], Nen[27], Sen[28], Eack[35], Wack[34], Nack[28], Sack[27], Eack[34], Wack[35], Nack[27], Sack[28], inj35, pushj[35], wjack[35], writereqj[35], je[35], pushjack[35], ej35);  
  
  ProcessNode p36( 3'b100, 3'b100, east[35], west[36], north[35], south[36], clk, reset, Ereq[35], Wreq[36], Nreq[35], Sreq[36], Een[36], Wen[35], Nen[36], Sen[35], east[36], west[35], north[36], south[35], Ereq[36], Wreq[35], Nreq[36], Sreq[35], Een[35], Wen[36], Nen[35], Sen[36], Eack[36], Wack[35], Nack[36], Sack[35], Eack[35], Wack[36], Nack[35], Sack[36], inj36, pushj[36], wjack[36], writereqj[36], je[36], pushjack[36], ej36);
  
  ProcessNode p37( 3'b101, 3'b100, east[36], west[37], north[43], south[44], clk, reset, Ereq[36], Wreq[37], Nreq[43], Sreq[44], Een[37], Wen[36], Nen[44], Sen[43], east[37], west[36], north[44], south[43], Ereq[37], Wreq[36], Nreq[44], Sreq[43], Een[36], Wen[37], Nen[43], Sen[44], Eack[37], Wack[36], Nack[44], Sack[43], Eack[36], Wack[37], Nack[43], Sack[44], inj37, pushj[37], wjack[37], writereqj[37], je[37], pushjack[37], ej37);  
  
  ProcessNode p38( 3'b110, 3'b100, east[37], west[38], north[51], south[52], clk, reset, Ereq[37], Wreq[38], Nreq[51], Sreq[52], Een[38], Wen[37], Nen[52], Sen[51], east[38], west[37], north[52], south[51], Ereq[38], Wreq[37], Nreq[52], Sreq[51], Een[37], Wen[38], Nen[51], Sen[52], Eack[38], Wack[37], Nack[52], Sack[51], Eack[37], Wack[38], Nack[51], Sack[52], inj38, pushj[38], wjack[38], writereqj[38], je[38], pushjack[38], ej38);  
  
  ProcessNode p39( 3'b111, 3'b100, east[38], west[39], north[59], south[60], clk, reset, Ereq[38], Wreq[39], Nreq[59], Sreq[60], Een[39], Wen[38], Nen[60], Sen[59], east[39], west[38], north[60], south[59], Ereq[39], Wreq[38], Nreq[60], Sreq[59], Een[38], Wen[39], Nen[59], Sen[60], Eack[39], Wack[38], Nack[60], Sack[59], Eack[38], Wack[39], Nack[59], Sack[60], inj39, pushj[39], wjack[39], writereqj[39], je[39], pushjack[39], ej39);  
  
  ProcessNode p40( 3'b000, 3'b101, west[40], north[4], south[5],  clk, reset, Wreq[40], Nreq[4], Sreq[5], Een[40], Nen[5], Sen[4],  east[40], north[5], south[4], Ereq[40], Nreq[5], Sreq[4], Wen[40], Nen[4], Sen[5], Eack[40], Nack[5], Sack[4], Wack[40], Nack[4], Sack[5], inj40, pushj[40], wjack[40], writereqj[40], je[40], pushjack[40], ej40);
  
  ProcessNode p41( 3'b001, 3'b101, east[40], west[41], north[12], south[13],  clk, reset, Ereq[40], Wreq[41], Nreq[12], Sreq[13], Een[41], Wen[40], Nen[13], Sen[12], east[41], west[40], north[13], south[12], Ereq[41], Wreq[40], Nreq[13], Sreq[12], Een[40], Wen[41], Nen[12], Sen[13], Eack[41], Wack[40], Nack[13], Sack[12], Eack[40], Wack[41], Nack[12], Sack[13], inj41, pushj[41], wjack[41], writereqj[41], je[41], pushjack[41], ej41);
                  
  ProcessNode p42( 3'b010, 3'b101, east[41], west[42], north[20], south[21], clk, reset, Ereq[41], Wreq[42], Nreq[20], Sreq[21], Een[42], Wen[41], Nen[21], Sen[20], east[42], west[41], north[21], south[20], Ereq[42], Wreq[41], Nreq[21], Sreq[20], Een[41], Wen[42], Nen[20], Sen[21], Eack[42], Wack[41], Nack[21], Sack[20], Eack[41], Wack[42], Nack[20], Sack[21], inj42, pushj[42], wjack[42], writereqj[42], je[42], pushjack[42], ej42);
  
  ProcessNode p43( 3'b011, 3'b101, east[42], west[43], north[28], south[29], clk, reset, Ereq[42], Wreq[43], Nreq[28], Sreq[29], Een[43], Wen[42], Nen[29], Sen[28], east[43], west[42], north[29], south[28], Ereq[43], Wreq[42], Nreq[29], Sreq[28], Een[42], Wen[43], Nen[28], Sen[29], Eack[43], Wack[42], Nack[29], Sack[28], Eack[42], Wack[43], Nack[28], Sack[29], inj43, pushj[43], wjack[43], writereqj[43], je[43], pushjack[43], ej43);  
  
  ProcessNode p44( 3'b100, 3'b101, east[43], west[44], north[36], south[37], clk, reset, Ereq[43], Wreq[44], Nreq[36], Sreq[37], Een[44], Wen[43], Nen[37], Sen[36], east[44], west[43], north[37], south[36], Ereq[44], Wreq[43], Nreq[37], Sreq[36], Een[43], Wen[44], Nen[36], Sen[37], Eack[44], Wack[43], Nack[37], Sack[36], Eack[43], Wack[44], Nack[36], Sack[37], inj44, pushj[44], wjack[44], writereqj[44], je[44], pushjack[44], ej44);
  
  ProcessNode p45( 3'b101, 3'b101, east[44], west[45], north[44], south[45], clk, reset, Ereq[44], Wreq[45], Nreq[44], Sreq[45], Een[45], Wen[44], Nen[45], Sen[44], east[45], west[44], north[45], south[44], Ereq[45], Wreq[44], Nreq[45], Sreq[44], Een[44], Wen[45], Nen[44], Sen[45], Eack[45], Wack[44], Nack[45], Sack[44], Eack[44], Wack[45], Nack[44], Sack[45], inj45, pushj[45], wjack[45], writereqj[45], je[45], pushjack[45], ej45);  
  
  ProcessNode p46( 3'b110, 3'b101, east[45], west[46], north[52], south[53], clk, reset, Ereq[45], Wreq[46], Nreq[52], Sreq[53], Een[46], Wen[45], Nen[53], Sen[52], east[46], west[45], north[53], south[52], Ereq[46], Wreq[45], Nreq[53], Sreq[52], Een[45], Wen[46], Nen[52], Sen[53], Eack[46], Wack[45], Nack[53], Sack[52], Eack[45], Wack[46], Nack[52], Sack[53], inj46, pushj[46], wjack[46], writereqj[46], je[46], pushjack[46], ej46);  
  
  ProcessNode p47( 3'b111, 3'b101, east[46], west[47], north[60], south[61], clk, reset, Ereq[46], Wreq[47], Nreq[60], Sreq[61], Een[47], Wen[46], Nen[61], Sen[60], east[47], west[46], north[61], south[60], Ereq[47], Wreq[46], Nreq[61], Sreq[60], Een[46], Wen[47], Nen[60], Sen[61], Eack[47], Wack[46], Nack[61], Sack[60], Eack[46], Wack[47], Nack[60], Sack[61], inj47, pushj[47], wjack[47], writereqj[47], je[47], pushjack[47], ej47);  
  
  ProcessNode p48( 3'b000, 3'b110, west[48], north[5], south[6],  clk, reset, Wreq[48], Nreq[5], Sreq[6], Een[48], Nen[6], Sen[5],  east[48], north[6], south[5], Ereq[48], Nreq[6], Sreq[5], Wen[48], Nen[5], Sen[6], Eack[48], Nack[6], Sack[5], Wack[48], Nack[5], Sack[6], inj48, pushj[48], wjack[48], writereqj[48], je[48], pushjack[48], ej48);
  
  ProcessNode p49( 3'b001, 3'b110, east[48], west[49], north[13], south[14],  clk, reset, Ereq[48], Wreq[49], Nreq[13], Sreq[14], Een[49], Wen[48], Nen[14], Sen[13], east[49], west[48], north[14], south[13], Ereq[49], Wreq[48], Nreq[14], Sreq[13], Een[48], Wen[49], Nen[13], Sen[14], Eack[49], Wack[48], Nack[14], Sack[13], Eack[48], Wack[49], Nack[13], Sack[14], inj49, pushj[49], wjack[49], writereqj[49], je[49], pushjack[49], ej49);
                  
  ProcessNode p50( 3'b010, 3'b110, east[49], west[50], north[21], south[22], clk, reset, Ereq[49], Wreq[50], Nreq[21], Sreq[22], Een[50], Wen[49], Nen[22], Sen[21], east[50], west[49], north[22], south[21], Ereq[50], Wreq[49], Nreq[22], Sreq[21], Een[49], Wen[50], Nen[21], Sen[22], Eack[50], Wack[49], Nack[22], Sack[21], Eack[49], Wack[50], Nack[21], Sack[22], inj50, pushj[50], wjack[50], writereqj[50], je[50], pushjack[50], ej50);
  
  ProcessNode p51( 3'b011, 3'b110, east[50], west[51], north[29], south[30], clk, reset, Ereq[50], Wreq[51], Nreq[29], Sreq[30], Een[51], Wen[50], Nen[30], Sen[29], east[51], west[50], north[30], south[29], Ereq[51], Wreq[50], Nreq[30], Sreq[29], Een[50], Wen[51], Nen[29], Sen[30], Eack[51], Wack[50], Nack[30], Sack[29], Eack[50], Wack[51], Nack[29], Sack[30], inj51, pushj[51], wjack[51], writereqj[51], je[51], pushjack[51], ej51);  
  
  ProcessNode p52( 3'b100, 3'b110, east[51], west[52], north[37], south[38], clk, reset, Ereq[51], Wreq[52], Nreq[37], Sreq[38], Een[52], Wen[51], Nen[38], Sen[37], east[52], west[51], north[38], south[37], Ereq[52], Wreq[51], Nreq[38], Sreq[37], Een[51], Wen[52], Nen[37], Sen[38], Eack[52], Wack[51], Nack[38], Sack[37], Eack[51], Wack[52], Nack[37], Sack[38], inj52, pushj[52], wjack[52], writereqj[52], je[52], pushjack[52], ej52);
  
  ProcessNode p53( 3'b101, 3'b110, east[52], west[53], north[45], south[46], clk, reset, Ereq[52], Wreq[53], Nreq[45], Sreq[46], Een[53], Wen[52], Nen[46], Sen[45], east[53], west[52], north[46], south[45], Ereq[53], Wreq[52], Nreq[46], Sreq[45], Een[52], Wen[53], Nen[45], Sen[46], Eack[53], Wack[52], Nack[46], Sack[45], Eack[52], Wack[53], Nack[45], Sack[46], inj53, pushj[53], wjack[53], writereqj[53], je[53], pushjack[53], ej53);  
  
  ProcessNode p54( 3'b110, 3'b110, east[53], west[54], north[53], south[54], clk, reset, Ereq[53], Wreq[54], Nreq[53], Sreq[54], Een[54], Wen[53], Nen[54], Sen[53], east[54], west[53], north[54], south[53], Ereq[54], Wreq[53], Nreq[54], Sreq[53], Een[53], Wen[54], Nen[53], Sen[54], Eack[54], Wack[53], Nack[54], Sack[53], Eack[53], Wack[54], Nack[53], Sack[54], inj54, pushj[54], wjack[54], writereqj[54], je[54], pushjack[54], ej54);  
  
  ProcessNode p55( 3'b111, 3'b110, east[54], west[55], north[61], south[62], clk, reset, Ereq[54], Wreq[55], Nreq[61], Sreq[62], Een[55], Wen[54], Nen[62], Sen[61], east[55], west[54], north[62], south[61], Ereq[55], Wreq[54], Nreq[62], Sreq[61], Een[54], Wen[55], Nen[61], Sen[62], Eack[55], Wack[54], Nack[62], Sack[61], Eack[54], Wack[55], Nack[61], Sack[62], inj55, pushj[55], wjack[55], writereqj[55], je[55], pushjack[55], ej55);  
  
  ProcessNode p56( 3'b000, 3'b111, west[56], north[6], south[7],  clk, reset, Wreq[56], Nreq[6], Sreq[7], Een[56], Nen[7], Sen[6],  east[56], north[7], south[6], Ereq[56], Nreq[7], Sreq[6], Wen[56], Nen[6], Sen[7], Eack[56], Nack[7], Sack[6], Wack[56], Nack[6], Sack[7], inj56, pushj[56], wjack[56], writereqj[56], je[56], pushjack[56], ej56);
  
  ProcessNode p57( 3'b001, 3'b111, east[56], west[57], north[14], south[15],  clk, reset, Ereq[56], Wreq[57], Nreq[14], Sreq[15], Een[57], Wen[56], Nen[15], Sen[14], east[57], west[56], north[15], south[14], Ereq[57], Wreq[56], Nreq[15], Sreq[14], Een[56], Wen[57], Nen[14], Sen[15], Eack[57], Wack[56], Nack[15], Sack[14], Eack[56], Wack[57], Nack[14], Sack[15], inj57, pushj[57], wjack[57], writereqj[57], je[57], pushjack[57], ej57);
                  
  ProcessNode p58( 3'b010, 3'b111, east[57], west[58], north[22], south[23], clk, reset, Ereq[57], Wreq[58], Nreq[22], Sreq[23], Een[58], Wen[57], Nen[23], Sen[22], east[58], west[57], north[23], south[22], Ereq[58], Wreq[57], Nreq[23], Sreq[22], Een[57], Wen[58], Nen[22], Sen[23], Eack[58], Wack[57], Nack[23], Sack[22], Eack[57], Wack[58], Nack[22], Sack[23], inj58, pushj[58], wjack[58], writereqj[58], je[58], pushjack[58], ej58);
  
  ProcessNode p59( 3'b011, 3'b111, east[58], west[59], north[30], south[31], clk, reset, Ereq[58], Wreq[59], Nreq[30], Sreq[31], Een[59], Wen[58], Nen[31], Sen[30], east[59], west[58], north[31], south[30], Ereq[59], Wreq[58], Nreq[31], Sreq[30], Een[58], Wen[59], Nen[30], Sen[31], Eack[59], Wack[58], Nack[31], Sack[30], Eack[58], Wack[59], Nack[30], Sack[31], inj59, pushj[59], wjack[59], writereqj[59], je[59], pushjack[59], ej59);  
  
  ProcessNode p60( 3'b100, 3'b111, east[59], west[60], north[38], south[39], clk, reset, Ereq[59], Wreq[60], Nreq[38], Sreq[39], Een[60], Wen[59], Nen[39], Sen[38], east[60], west[59], north[39], south[38], Ereq[60], Wreq[59], Nreq[39], Sreq[38], Een[59], Wen[60], Nen[38], Sen[39], Eack[60], Wack[59], Nack[39], Sack[38], Eack[59], Wack[60], Nack[38], Sack[39], inj60, pushj[60], wjack[60], writereqj[60], je[60], pushjack[60], ej60);
  
  ProcessNode p61( 3'b101, 3'b111, east[60], west[61], north[46], south[47], clk, reset, Ereq[60], Wreq[61], Nreq[46], Sreq[47], Een[61], Wen[60], Nen[47], Sen[46], east[61], west[60], north[47], south[46], Ereq[61], Wreq[60], Nreq[47], Sreq[46], Een[60], Wen[61], Nen[46], Sen[47], Eack[61], Wack[60], Nack[47], Sack[46], Eack[60], Wack[61], Nack[46], Sack[47], inj61, pushj[61], wjack[61], writereqj[61], je[61], pushjack[61], ej61);  
  
  ProcessNode p62( 3'b110, 3'b111, east[61], west[62], north[54], south[55], clk, reset, Ereq[61], Wreq[62], Nreq[54], Sreq[55], Een[62], Wen[61], Nen[55], Sen[54], east[62], west[61], north[55], south[54], Ereq[62], Wreq[61], Nreq[55], Sreq[54], Een[61], Wen[62], Nen[54], Sen[55], Eack[62], Wack[61], Nack[55], Sack[54], Eack[61], Wack[62], Nack[54], Sack[55], inj62, pushj[62], wjack[62], writereqj[62], je[62], pushjack[62], ej62);  
  
  ProcessNode p63( 3'b111, 3'b111, east[62], west[63], north[62], south[63], clk, reset, Ereq[62], Wreq[63], Nreq[62], Sreq[63], Een[63], Wen[62], Nen[63], Sen[62], east[63], west[62], north[63], south[62], Ereq[63], Wreq[62], Nreq[63], Sreq[62], Een[62], Wen[63], Nen[62], Sen[63], Eack[63], Wack[62], Nack[63], Sack[62], Eack[62], Wack[63], Nack[62], Sack[63], inj63, pushj[63], wjack[63], writereqj[63], je[63], pushjack[63], ej63);  
  
  
endmodule
module outputbufferavailablity (output reg ea, wa, na, sa, ejecta, input clk,
                                  input [2:0] eempl, wempl, nempl, sempl, ejectempl, 
								  input reset, eallocOrnot, wallocOrnot, nallocOrnot, sallocOrnot, ejectallocOrnot);
                                  
                                  
  always @(*)
  begin
	if(reset)
		{ea, wa, na, sa, ejecta} = 5'b11111;
	else
	begin
		{ea, wa, na, sa, ejecta} = 5'b0;
		if(eallocOrnot == 0 && (eempl > 3'd0))
		begin
		  ea = 1;
		end
		if(wallocOrnot == 0 && (wempl > 3'd0))
		begin
		  wa = 1;
		end
		if(nallocOrnot == 0 && (nempl > 3'd0))
		begin
		  na = 1;
		end
		if(sallocOrnot == 0 && (sempl > 3'd0))
		begin
		  sa = 1;
		end
		if(ejectallocOrnot == 0 && (ejectempl > 3'd0))
		begin
		  ejecta = 1;
		end
	end
  end
                                  
endmodule

module outputunit (output [63:0] bfout,  
					output reg writereq, allocOrnot, 
					output [2:0] empl,
					input clk, reset, push, nextrouterstate, alloc, 
                    input [63:0] bfin, input writereqack);
  
  reg pop;
  reg pushx;
  Buffer bf (bfout, empl, clk, reset, pop, pushx, bfin);

  always @(*)
  begin
    pushx = push;
    if(push == 0 && empl > 3'd0 && bfin[63:62] == 2'b10 && (bfout[63:62] == 2'b01 || bfout[63:62] == 2'b11) )
      pushx = 1;
  end
  
  always @(*)
  begin
	if(reset)
		writereq = 0;
	else
	begin
	  writereq = 1'b0;
		if(nextrouterstate && (bfout[63:62] != 2'b00) && (empl != 3'd4))
		begin
  		  writereq = 1'b1;
		end
	end
  end
  
  always @(*)
  begin
    pop = 0;
    if(writereqack == 1)
      pop = 1'b1;
  end
  
  always @(*)
  begin
    if(reset)
    begin
      allocOrnot = 0;
    end
    else
    begin
      allocOrnot = alloc;
    end
  end
  
endmodule
module outengen (output reg Een, Wen, Nen, Sen, Ejecten, 
                   input [2:0] SE, SW, SN, SS, Seject, 
				   input epusho, wpusho, npusho, spusho, jpusho, input reset);
				   
  always @(*)
  begin
	if (reset)
		{Een, Wen, Nen, Sen, Ejecten} = 5'b0; 
	else
	begin 
		{Een, Wen, Nen, Sen, Ejecten} = 5'b0; 	
		if(epusho == 1)
		begin
		  if(SE == 3'b000)
			Een = 1;
		  if(SW == 3'b000)
			Wen = 1;
		  if(SN == 3'b000)
			Nen = 1;
		  if(SS == 3'b000)
			Sen = 1;
		  if(Seject == 3'b000)
			Ejecten = 1;
		end
		if(wpusho == 1)
		begin
		  if(SE == 3'b001)
			Een = 1;
		  if(SW == 3'b001)
			Wen = 1;
		  if(SN == 3'b001)
			Nen = 1;
		  if(SS == 3'b001)
			Sen = 1;
		  if(Seject == 3'b001)
			Ejecten = 1;
		end
		if(npusho == 1)
		begin
		  if(SE == 3'b010)
			Een = 1;
		  if(SW == 3'b010)
			Wen = 1;
		  if(SN == 3'b010)
			Nen = 1;
		  if(SS == 3'b010)
			Sen = 1;
		  if(Seject == 3'b010)
			Ejecten = 1;
		end
		if(spusho == 1)
		begin
		  if(SE == 3'b011)
			Een = 1;
		  if(SW == 3'b011)
			Wen = 1;
		  if(SN == 3'b011)
			Nen = 1;
		  if(SS == 3'b011)
			Sen = 1;
		  if(Seject == 3'b011)
			Ejecten = 1;
		end
		if(jpusho == 1)
		begin
		  if(SE == 3'b100)
			Een = 1;
		  if(SW == 3'b100)
			Wen = 1;
		  if(SN == 3'b100)
			Nen = 1;
		  if(SS == 3'b100)
			Sen = 1;
		  if(Seject == 3'b100)
			Ejecten = 1;
		end
	end
  end
  
  
  
  
endmodule

module Packetgen (input endsim, input clk, reset, input je, input [2:0] srcX, srcY, output reg [63:0] Flit, output reg writereq, input writereqack);
  
  reg [4:0] count;
  reg [31:0] t1, t2;
  reg [63:0] temp;
  reg [49:0] FlitID;
  
  reg [43:0] cnt;
  
  reg [5:0] ID;
  
  
  
  reg [2:0] destY, destX;
  
  reg [2:0] State;
  reg [2:0] NextState;
  
  
  always @(posedge clk)
  begin
    case (State)
      3'b000:
      begin
       count = 0;
       cnt = 0;
      end
      3'b001:
      begin
        count = count + 1;
        cnt = cnt;
      end
      3'b010:
      begin
       count = count;
       cnt = cnt;
      end
      3'b011:
      begin
        count = count;
        cnt = cnt + 1;
      end
      3'b100:
      begin
        count = count;
        cnt = cnt;
      end
      3'b101:
      begin
        count = count;
        cnt = cnt;
      end
      3'b110:
      begin
        count = 0;
        cnt = cnt;
      end
      3'b111:
      begin
        count = 0;
        cnt = cnt;
      end      
    endcase
  end
  

  
  always @(posedge clk)
  begin
    if(reset == 1)
      State <= 3'b0;
    else
      State <= NextState;
  end
  
  always @(*)
  begin
    case (State)
      3'b000:
          NextState = 3'b001;
      3'b001:
      begin
        if(count == 5'b01001)
          NextState = 3'b010;
        else
          NextState = 3'b001;
      end
      3'b010:
      begin
        if(je == 0)
          NextState = 3'b010;
        else if(je == 1)
          NextState = 3'b011;
      end
      3'b011: NextState = 3'b100;
      3'b100: NextState = 3'b101;
      3'b101: NextState = 3'b110;
      3'b110: NextState = 3'b111;
      3'b111: NextState = 3'b001;
    endcase
  end
  
  always @(*)
  begin
    case (State)
      3'b000:
      begin
        writereq = 0;
      end
      3'b001:
        writereq = 0;
      3'b010:
        writereq = 0;
      3'b011: 
      begin
		destX = srcX;
        destY = srcY;
        while(destX == srcX && destY == srcY)
        begin
          {destX, destY} = $random();
        end
        writereq = 1;
        FlitID = {cnt, ID};
        t1 = $random();
        t2 = $random();
        temp = {t1, t2};
        temp[63:62] = 2'b11;
        temp[11:0] = {destY, destX, srcY, srcX};
        temp[61:12] = FlitID;
        Flit = temp;
      end
      3'b100:
      begin
        writereq = 1;
        t1 = $random();
        t2 = $random();
        temp = {t1, t2};
        temp[63:62] = 2'b01;
        temp[11:0] = {destY, destX, srcY, srcX};
        Flit = temp;
      end
      3'b101:
      begin
        writereq = 1;
        t1 = $random();
        t2 = $random();
        temp = {t1, t2};
        temp[63:62] = 2'b01;
        temp[11:0] = {destY, destX, srcY, srcX};
        Flit = temp;
      end
      3'b110:
      begin
        writereq = 1;
        t1 = $random();
        t2 = $random();
        temp = {t1, t2};
        temp[63:62] = 2'b10;
        temp[11:0] = {destY, destX, srcY, srcX};
        Flit = temp;
      end
      3'b111:
      begin
        writereq = 0;
      end
    endcase
  end
  
  always @(*)
  begin
    ID = srcY * 8 + srcX;
  end
  
  
  endmodule
  module Packetrec (input clk, reset, endsim, write, input [63:0] Flit, output reg pushack, input [2:0] Xcur, Ycur);
  
  
  reg [1:0] seq;
  reg [19:0] addr;
  reg [305:0] M [0:20000];
  reg [49:0] cnt;
  reg en;
  integer handle;
  integer desc;
  integer ID;
  integer i;
  integer temp;
  always @(*)
  begin
    if(endsim == 1)
    begin
      ID = Ycur*8 + Xcur;
      case (ID)
        0:  handle = $fopen("out/0.out"); 
        1:  handle = $fopen("out/1.out");  
        2:  handle = $fopen("out/2.out"); 
        3:  handle = $fopen("out/3.out"); 
        4:  handle = $fopen("out/4.out"); 
        5:  handle = $fopen("out/5.out"); 
        6:  handle = $fopen("out/6.out"); 
        7:  handle = $fopen("out/7.out"); 
        8:  handle = $fopen("out/8.out"); 
        9:  handle = $fopen("out/9.out"); 
        10: handle = $fopen("out/10.out"); 
        11: handle = $fopen("out/11.out"); 
        12: handle = $fopen("out/12.out"); 
        13: handle = $fopen("out/13.out"); 
        14: handle = $fopen("out/14.out"); 
        15: handle = $fopen("out/15.out"); 
        16: handle = $fopen("out/16.out"); 
        17: handle = $fopen("out/17.out"); 
        18: handle = $fopen("out/18.out"); 
        19: handle = $fopen("out/19.out"); 
        20: handle = $fopen("out/20.out"); 
        21: handle = $fopen("out/21.out"); 
        22: handle = $fopen("out/22.out"); 
        23: handle = $fopen("out/23.out"); 
        24: handle = $fopen("out/24.out"); 
        25: handle = $fopen("out/25.out"); 
        26: handle = $fopen("out/26.out"); 
        27: handle = $fopen("out/27.out"); 
        28: handle = $fopen("out/28.out"); 
        29: handle = $fopen("out/29.out"); 
        30: handle = $fopen("out/30.out"); 
        31: handle = $fopen("out/31.out"); 
        32: handle = $fopen("out/32.out"); 
        33: handle = $fopen("out/33.out"); 
        34: handle = $fopen("out/34.out"); 
        35: handle = $fopen("out/35.out"); 
        36: handle = $fopen("out/36.out"); 
        37: handle = $fopen("out/37.out"); 
        38: handle = $fopen("out/38.out"); 
        39: handle = $fopen("out/39.out"); 
        40: handle = $fopen("out/40.out"); 
        41: handle = $fopen("out/41.out"); 
        42: handle = $fopen("out/42.out"); 
        43: handle = $fopen("out/43.out"); 
        44: handle = $fopen("out/44.out"); 
        45: handle = $fopen("out/45.out"); 
        46: handle = $fopen("out/46.out"); 
        47: handle = $fopen("out/47.out"); 
        48: handle = $fopen("out/48.out"); 
        49: handle = $fopen("out/49.out"); 
        50: handle = $fopen("out/50.out"); 
        51: handle = $fopen("out/51.out"); 
        52: handle = $fopen("out/52.out"); 
        53: handle = $fopen("out/53.out"); 
        54: handle = $fopen("out/54.out"); 
        55: handle = $fopen("out/55.out"); 
        56: handle = $fopen("out/56.out"); 
        57: handle = $fopen("out/57.out"); 
        58: handle = $fopen("out/58.out"); 
        59: handle = $fopen("out/59.out"); 
        60: handle = $fopen("out/60.out"); 
        61: handle = $fopen("out/61.out"); 
        62: handle = $fopen("out/62.out"); 
        63: handle = $fopen("out/63.out"); 
      endcase
      for(i = 0; i < addr; i = i + 1)
      begin
    
        $fdisplay(handle,"%0d \t %b",M[i][305:256],M[i][255:192]);
      end
      $fclose(handle);
      #100000
      i = 0;
    end
  end
  
  always @(*)
  begin
    pushack = write;
  end
  
  always @(posedge clk)
  begin
    if(reset)
    begin
      en = 0;
      seq = 0;
      addr = 0;
      cnt = 50'h3ffffffffffff;
    end
    else
    begin
      cnt = cnt + 1;
    
      if(write == 1)
      begin
        if(seq == 2'b00)
        begin
          if(Flit[63:62] == 2'b11 && Xcur == 3)
          begin
            en = 1;
      
          end
          M[addr][305:256]= cnt;
          M[addr][255:192] = Flit;
          seq = seq + 1;
        end
        else if(seq == 2'b01)
        begin
          if(en == 1)
    
          M[addr][191:128] = Flit;
          seq = seq + 1;
        end
        else if(seq == 2'b10)
        begin
          if(en == 1)
     
          M[addr][127:64] = Flit;
          seq = seq + 1;
        end
        else if(seq == 2'b11)
        begin
          if(en == 1)
       
          M[addr][63:0] = Flit;
          seq = seq + 1;
          addr = addr + 1;
          en = 0;
        end
      end
    end
    
  end
  
  
endmodule
  module ProcessNode (input [2:0] Xcur, Ycur, input [63:0] ie, iw, in, is, input clk, reset, pushe, pushw, pushn, pushs,
                     estate, wstate, nstate, sstate, output [63:0] oe, ow, on, os, output writereqe, writereqw, writereqn, writereqs, 
                     ee, we, ne, se,
                     input weack, wwack, wnack, wsack, output pusheack, pushwack, pushnack, pushsack,
                     input [63:0] inject, input pushj, wjack, output writereqj, je, pushjack, output [63:0] eject);
  
	 
	 
	
  
  Router R(Xcur, Ycur, ie, iw, in, is, inject, clk, reset, pushe, pushw, pushn, pushs, pushj, estate, wstate, nstate, sstate, 1'b1, 
           oe, ow, on, os, eject, writereqe, writereqw, writereqn, writereqs, writereqj, ee, we, ne, se, je,
           weack, wwack, wnack, wsack, wjack, pusheack, pushwack, pushnack, pushsack, pushjack);  
          
  
  
  
endmodule
module Router (input [2:0] Xcur, Ycur, input [63:0] ie, iw, in, is, inject, input clk, reset, pushe, pushw, pushn, pushs, pushj,
               estate, wstate, nstate, sstate, ejectstate,
               output [63:0] oe, ow, on, os, eject, output writereqe, writereqw, writereqn, writereqs, writereqj, output reg ee, we, ne, se, je,
               input weack, wwack, wnack, wsack, wjack, output pusheack, pushwack, pushnack, pushsack, pushjack);
  
  wire [63:0] etemp, wtemp, ntemp, stemp, injecttemp;
  wire [63:0] etempo, wtempo, ntempo, stempo, injecttempo;
  
  wire eoen, een, evcg, evcf, ePW, ePWfail, evcgrant, eSTack, woen, wen, wvcg, wvcf, wPW, wPWfail, wvcgrant, wSTack,
       noen, nen, nvcg, nvcf, nPW, nPWfail, nvcgrant, nSTack, soen, sen, svcg, svcf, sPW, sPWfail, svcgrant, sSTack,
       joen, jen, jvcg, jvcf, jPW, jPWfail, jvcgrant, jSTack;
       
  wire alloce, allocw, allocn, allocs, allocj;
  wire pusheo, pushwo, pushno, pushso, pushjo;
  wire allocOrnote, allocOrnotw, allocOrnotn, allocOrnots, allocOrnotj;
  wire oeen, owen, onen, osen, ejecten;
  wire stoeen, stowen, stonen, stosen, stEjecten;
  wire eSTreq, wSTreq, nSTreq, sSTreq, ejectSTreq;
  wire epusho, wpusho, npusho, spusho, jpusho;
  reg oef, owf, onf, osf, ejectf;
  
  
  wire [2:0] eempl, eoutnum, wempl, woutnum, nempl, noutnum, sempl, soutnum, jempl, joutnum;
  wire [2:0] SE, SW, SN, SS, SEjec;
  wire [2:0] eemplo, wemplo, nemplo, semplo, jemplo;
  
  always @(*)
  begin
	if (reset)
		{ee, we, ne, se, je} = 5'b0;
	else
	begin
		{ee, we, ne, se, je} = 5'b0;
		if(eempl > 0)
		  ee = 1;
		if(wempl > 0)
		  we = 1;
		if(nempl > 0)
		  ne = 1;
		if(sempl > 0)
		  se = 1;
		if(jempl == 3'd4)
		  je = 1;
	end
  end
  
  always @(*)
  begin
	if (reset)
		{oef, owf, onf, osf, ejectf} = 5'b0;
	else
	begin
		{oef, owf, onf, osf, ejectf} = 5'b0;

		if(eemplo > 0)
		  oef = 1;
		if(wemplo > 0)
		  owf = 1;
		if(nemplo > 0)
		  onf = 1;
		if(semplo > 0)
		  osf = 1;
		if(jemplo > 0)
		  ejectf = 1;
	end
  end
       
  
  
  inputUnit inpute (etemp, een, eempl, eoutnum, ePW, evcg, evcf, epusho,
                      clk, reset, pushe, ePWfail, evcgrant, eSTack, ie, Xcur, Ycur, 3'b000, pusheack);
  
  inputUnit inputw (wtemp, wen, wempl, woutnum, wPW, wvcg, wvcf, wpusho,
                      clk, reset, pushw, wPWfail, wvcgrant, wSTack, iw, Xcur, Ycur, 3'b001, pushwack);
                      
  inputUnit inputn (ntemp, nen, nempl, noutnum, nPW, nvcg, nvcf, npusho,
                      clk, reset, pushn, nPWfail, nvcgrant, nSTack, in, Xcur, Ycur, 3'b010, pushnack);
  
  inputUnit inputs (stemp, sen, sempl, soutnum, sPW, svcg, svcf, spusho,
                      clk, reset, pushs, sPWfail, svcgrant, sSTack, is, Xcur, Ycur, 3'b011, pushsack);
                      
  inputUnit inputinject (injecttemp, jen, jempl, joutnum, jPW, jvcg, jvcf, jpusho,
                      clk, reset, pushj, jPWfail, jvcgrant, jSTack, inject, Xcur, Ycur, 3'b100, pushjack);
                      
  outengen oeg(pusheo, pushwo, pushno, pushso, pushjo, SE, SW, SN, SS, SEjec, epusho, wpusho, npusho, spusho, jpusho, reset);
 
  
  outputunit outpute 		(oe, writereqe, allocOrnote,  eemplo, clk, reset, pusheo, estate, alloce, etempo, weack);
  outputunit outputw 		(ow, writereqw, allocOrnotw,  wemplo, clk, reset, pushwo, wstate, allocw, wtempo, wwack);
  outputunit outputn 		(on, writereqn, allocOrnotn,  nemplo, clk, reset, pushno, nstate, allocn, ntempo, wnack);
  outputunit outputs 		(os, writereqs, allocOrnots,  semplo, clk, reset, pushso, sstate, allocs, stempo, wsack);
  outputunit outputeject 	(eject, writereqj, allocOrnotj,  jemplo, clk, reset, pushjo, ejectstate, allocj, injecttempo, wjack);
  
  Selectgen sg(SE, SW, SN, SS, SEjec, 
                evcgrant, wvcgrant, nvcgrant, svcgrant, jvcgrant, clk, reset, eoutnum, woutnum, noutnum, soutnum, joutnum);
                
  setAlloc sac(alloce, allocw, allocn, allocs, allocj, evcgrant, wvcgrant, nvcgrant, svcgrant, jvcgrant, reset, 
             eoutnum, woutnum, noutnum, soutnum, joutnum);
    
                
  CrossBar X(etempo, wtempo, ntempo, stempo, injecttempo, SE, SW, SN, SS, SEjec, etemp, wtemp, ntemp, stemp, injecttemp);
  
  VCAlloc vca(evcgrant, wvcgrant, nvcgrant, svcgrant, jvcgrant, clk, reset,
               eoutnum, woutnum, noutnum, soutnum, joutnum, oeen, owen, onen, osen, ejecten, een, wen, nen, sen, jen,
               evcf, wvcf, nvcf, svcf, jvcf);
               
  outputbufferavailablity oba(oeen, owen, onen, osen, ejecten, clk,
                                eemplo, wemplo, nemplo, semplo, jemplo, reset, allocOrnote, allocOrnotw, allocOrnotn, allocOrnots, allocOrnotj);
                                
  
  ST switchtravers(stoeen, stowen, stonen, stosen, stEjecten, eSTreq, wSTreq, nSTreq, sSTreq, ejectSTreq, oef, owf, onf, osf, ejectf); 
                                
                                
  STControler stcont(eSTreq, wSTreq, nSTreq, sSTreq, ejectSTreq, eSTack, wSTack, nSTack, sSTack, jSTack, clk, reset, evcgrant, wvcgrant, 
                       nvcgrant, svcgrant, jvcgrant, stoeen, stowen, stonen, stosen, stEjecten, 
                       eoutnum, woutnum, noutnum, soutnum, joutnum);
                       
endmodule
module RouteFunc (output reg [4:0] validout, status,  input [2:0] Xcur, Ycur, Xdest, Ydest, inchannel, input reset);
  
  /*
  0:E
  1:W
  2:N
  3:S
  4:Eject
  */
  
  always @(*)
  begin
	if (reset)
		{validout, status} = 10'b0;
	else
	begin
		{validout, status} = 10'b0;
		if(Xcur < Xdest)
		  validout[0] = 1;
		else if(Xcur > Xdest)
		  validout[1] = 1;
		else if(Xcur == Xdest)
		begin
		  if(Ycur < Ydest)
			validout[2] = 1;
		  else if(Ycur > Ydest)
			validout[3] = 1;
		  else
			validout[4] = 1;
		end
	end
  end
  
endmodule

module Selectgen (output reg [2:0] se, sw, sn, ss, seject, 
                   input eg, wg, ng, sg, injectg, clk, reset, input [2:0] ereq, wreq, nreq, sreq, injectreq);
  
  
  always @(posedge clk)
  begin
    if(reset)
    begin
      se = 3'b111;
      sw = 3'b111;
      sn = 3'b111;
      ss = 3'b111;
      seject = 3'b111;
    end
    else
    se = 3'd7;  
    sw = 3'd7;  
    sn = 3'd7;  
    ss = 3'd7;  
    seject = 3'd7;  
    begin
      if(eg == 1)
      begin
        case (ereq)
          3'b000: se = 3'b000;
          3'b001: sw = 3'b000;
          3'b010: sn = 3'b000;
          3'b011: ss = 3'b000;
          3'b100: seject = 3'b000;
        endcase
      end
      if(wg == 1)
      begin
        case (wreq)
          3'b000: se = 3'b001;
          3'b001: sw = 3'b001;
          3'b010: sn = 3'b001;
          3'b011: ss = 3'b001;
          3'b100: seject = 3'b001;
        endcase
      end
      if(ng == 1)
      begin
        case (nreq)
          3'b000: se = 3'b010;
          3'b001: sw = 3'b010;
          3'b010: sn = 3'b010;
          3'b011: ss = 3'b010;
          3'b100: seject = 3'b010;
        endcase
      end
      if(sg == 1)
      begin
        case (sreq)
          3'b000: se = 3'b011;
          3'b001: sw = 3'b011;
          3'b010: sn = 3'b011;
          3'b011: ss = 3'b011;
          3'b100: seject = 3'b011;
        endcase
      end
      if(injectg == 1)
      begin
        case (injectreq)
          3'b000: se = 3'b100;
          3'b001: sw = 3'b100;
          3'b010: sn = 3'b100;
          3'b011: ss = 3'b100;
          3'b100: seject = 3'b100;
        endcase
      end
    end
    
  end
  
endmodule
module setAlloc (output reg alloce, allocw, allocn, allocs, allocj, 
				  input evcgrant, wvcgrant, nvcgrant, svcgrant, jvcgrant,reset,
                  input [2:0] ereq, wreq, nreq, sreq, jreq);
                  
 
 
  always @(*)
  begin
	if (reset)
		{alloce, allocw, allocn, allocs, allocj} = 5'b0;
	else
	begin
		{alloce, allocw, allocn, allocs, allocj} = 5'b0;
		if(evcgrant == 1)
		begin
		  case (ereq)
			3'b000:
			  alloce = 1;
			3'b001:
			  allocw = 1;
			3'b010:
			  allocn = 1;
			3'b011:
			  allocs = 1;
			3'b100:
			  allocj = 1;
		  endcase
		end
		if(wvcgrant == 1)
		begin
		  case (wreq)
			3'b000:
			  alloce = 1;
			3'b001:
			  allocw = 1;
			3'b010:
			  allocn = 1;
			3'b011:
			  allocs = 1;
			3'b100:
			  allocj = 1;
		  endcase
		end
		if(nvcgrant == 1)
		begin
		  case (nreq)
			3'b000:
			  alloce = 1;
			3'b001:
			  allocw = 1;
			3'b010:
			  allocn = 1;
			3'b011:
			  allocs = 1;
			3'b100:
			  allocj = 1;
		  endcase
		end
		if(svcgrant == 1)
		begin
		  case (sreq)
			3'b000:
			  alloce = 1;
			3'b001:
			  allocw = 1;
			3'b010:
			  allocn = 1;
			3'b011:
			  allocs = 1;
			3'b100:
			  allocj = 1;
		  endcase
		end
		if(jvcgrant == 1)
		begin
		  case (jreq)
			3'b000:
			  alloce = 1;
			3'b001:
			  allocw = 1;
			3'b010:
			  allocn = 1;
			3'b011:
			  allocs = 1;
			3'b100:
			  allocj = 1;
		  endcase
		end
	end	
  end
  
endmodule
module ST (output oeen, owen, onen, osen, Ejecten, 
           input ereq, wreq, nreq, sreq, ejectreq, oef, owf, onf, osf, ejectf);
           

  and (oeen, ereq, oef);
  and (owen, wreq, owf);
  and (onen, nreq, onf);
  and (osen, sreq, osf);
  and (Ejecten, ejectreq, ejectf); 
  
endmodule

module STControler (output reg eSTreq, wSTreq, nSTreq, sSTreq, ejectSTreq, eack, wack, nack, sack, injectack,
                     input clk, reset, evcalloc, wvcalloc, nvcalloc, svcalloc, injectvcalloc, oeen, owen, onen, osen, Ejecten, 
                     input [2:0] eout, wout, nout, sout, injectout);
  
  
  always @(*)
  begin
	if( reset)
		{eSTreq, wSTreq, nSTreq, sSTreq, ejectSTreq} = 5'b0;
	else
	begin
		{eSTreq, wSTreq, nSTreq, sSTreq, ejectSTreq} = 5'b0;	
		if(evcalloc == 1)
		begin
		  case (eout)
			3'b000:
			  eSTreq = 1;
			3'b001:
			  wSTreq = 1;
			3'b010:
			  nSTreq = 1;
			3'b011:
			  sSTreq = 1;
			3'b100:
			  ejectSTreq = 1;      
			default:
			  {eSTreq, wSTreq, nSTreq, sSTreq, ejectSTreq} = 5'b0;
		  endcase
		end
		
		if(wvcalloc == 1)
		begin
		  case (wout)
			3'b000:
			  eSTreq = 1;
			3'b001:
			  wSTreq = 1;
			3'b010:
			  nSTreq = 1;
			3'b011:
			  sSTreq = 1;
			3'b100:
			  ejectSTreq = 1;      
			default:
			  {eSTreq, wSTreq, nSTreq, sSTreq, ejectSTreq} = 5'b0;
		  endcase
		end
		
		if(nvcalloc == 1)
		begin
		  case (nout)
			3'b000:
			  eSTreq = 1;
			3'b001:
			  wSTreq = 1;
			3'b010:
			  nSTreq = 1;
			3'b011:
			  sSTreq = 1;
			3'b100:
			  ejectSTreq = 1;      
			default:
			  {eSTreq, wSTreq, nSTreq, sSTreq, ejectSTreq} = 5'b0;
		  endcase
		end
		
		if(svcalloc == 1)
		begin
		  case (sout)
			3'b000:
			  eSTreq = 1;
			3'b001:
			  wSTreq = 1;
			3'b010:
			  nSTreq = 1;
			3'b011:
			  sSTreq = 1;
			3'b100:
			  ejectSTreq = 1;      
			default:
			  {eSTreq, wSTreq, nSTreq, sSTreq, ejectSTreq} = 5'b0;
		  endcase
		end
		
		if(injectvcalloc == 1)
		begin
		  case (injectout)
			3'b000:
			  eSTreq = 1;
			3'b001:
			  wSTreq = 1;
			3'b010:
			  nSTreq = 1;
			3'b011:
			  sSTreq = 1;
			3'b100:
			  ejectSTreq = 1;      
			default:
			  {eSTreq, wSTreq, nSTreq, sSTreq, ejectSTreq} = 5'b0;
		  endcase
		end
	end
  end
  
  
  always @(posedge clk)
  begin
	if( reset )
		{eack, wack, nack, sack, injectack} = 5'b0;
	else
	begin
		{eack, wack, nack, sack, injectack} = 5'b0;
		if(oeen == 1)
		begin
		  if(eout == 3'd0 && evcalloc)
			eack = 1;
		  else if(wout == 3'd0 && wvcalloc)
			wack = 1;
		  else if(nout == 3'd0 && nvcalloc)
			nack = 1;
		  else if(sout == 3'd0 && svcalloc)
			sack = 1;
		  else if(injectout == 3'd0 && injectvcalloc)
			injectack = 1;
		end
		if(owen == 1)
		begin
		  if(eout == 3'd1 && evcalloc)
			eack = 1;
		  else if(wout == 3'd1 && wvcalloc)
			wack = 1;
		  else if(nout == 3'd1 && nvcalloc)
			nack = 1;
		  else if(sout == 3'd1 && svcalloc)
			sack = 1;
		  else if(injectout == 3'd1 && injectvcalloc)
			injectack = 1;
		end
		if(onen == 1)
		begin
		  if(eout == 3'd2 && evcalloc)
			eack = 1;
		  else if(wout == 3'd2 && wvcalloc)
			wack = 1;
		  else if(nout == 3'd2 && nvcalloc)
			nack = 1;
		  else if(sout == 3'd2 && svcalloc)
			sack = 1;
		  else if(injectout == 3'd2 && injectvcalloc)
			injectack = 1;
		end
		if(osen == 1)
		begin
		  if(eout == 3'd3 && evcalloc)
			eack = 1;
		  else if(wout == 3'd3 && wvcalloc)
			wack = 1;
		  else if(nout == 3'd3 && nvcalloc)
			nack = 1;
		  else if(sout == 3'd3 && svcalloc)
			sack = 1;
		  else if(injectout == 3'd3 && injectvcalloc)
			injectack = 1;
		end
		if(Ejecten == 1)
		begin
      if(eout == 3'd4 && evcalloc)
        eack = 1;
      else if(wout == 3'd4 && wvcalloc)
        wack = 1;
      else if(nout == 3'd4 && nvcalloc)
        nack = 1;
      else if(sout == 3'd4 && svcalloc)
        sack = 1;
      else if(injectout == 3'd4 && injectvcalloc)
        injectack = 1;
    end
	end
  end
  
endmodule

module VCAlloc (output reg vcge, vcgw, vcgn, vcgs, vcginjec, input clk, reset,
                 input [2:0] Ereq, Wreq, Nreq, Sreq, Injectreq,
				 input oeen, owen, onen, osen, ejecten, 
				 input ieen, iwen, inen, isen, injecten,
				 vcef, vcwf, vcnf, vcsf, vcjf);
   
  reg ence, encw, encn, encs, encj;
  wire [2:0] counte, countw, countn, counts, countj;
  
  Counter ce(counte, reset, clk, ence);
  Counter cw(countw, reset, clk, encw);
  Counter cn(countn, reset, clk, encn);
  Counter cs(counts, reset, clk, encs);
  Counter cj(countj, reset, clk, encj);
  
  always @(posedge clk)
  begin
    if(reset)
    begin
      {vcge, vcgw, vcgn, vcgs, vcginjec} = 5'b0;
      {ence, encw, encn, encs, encj} = 5'b11111;
    end
    else
    begin
    if(vcef == 1)
    begin
      if(vcge == 1)
      begin  
        case (Ereq)
          3'b000: ence = 1;
          3'b001: encw = 1;
          3'b010: encn = 1;
          3'b011: encs = 1;
          3'b100: encj = 1; 
        endcase
        vcge = 0;
      end
    end
    if(vcwf == 1)
    begin
      if(vcgw == 1)
      begin  
        case (Wreq)
          3'b000: ence = 1;
          3'b001: encw = 1;
          3'b010: encn = 1;
          3'b011: encs = 1;
          3'b100: encj = 1;  
        endcase
        vcgw = 0;
      end
    end
    if(vcnf == 1)
    begin
      if(vcgn == 1)
      begin  
        case (Nreq)
          3'b000: ence = 1;
          3'b001: encw = 1;
          3'b010: encn = 1;
          3'b011: encs = 1;
          3'b100: encj = 1;  
        endcase
        vcgn = 0;
      end
    end
    if(vcsf == 1)
    begin
      if(vcgs == 1)
      begin  
        case (Sreq)
          3'b000: ence = 1;
          3'b001: encw = 1;
          3'b010: encn = 1;
          3'b011: encs = 1;
          3'b100: encj = 1;  
        endcase
        vcgs = 0;
      end
    end
    if(vcjf == 1)
    begin
      if(vcginjec == 1)
      begin  
        case (Injectreq)
          3'b000: ence = 1;
          3'b001: encw = 1;
          3'b010: encn = 1;
          3'b011: encs = 1;
          3'b100: encj = 1;  
        endcase
        vcginjec = 0;
      end
    end
      
    if(oeen == 1) 
    begin
      case (counte)
        3'b000:
        begin
          if(Ereq == 3'd0 && ieen)
          begin
            vcge = 1;
            ence = 0;
          end
          else if(Wreq == 3'd0 && iwen)
          begin
            vcgw = 1;
            ence = 0;
          end
          else if(Nreq == 3'd0 && inen)
          begin
            vcgn = 1;
            ence = 0;
          end
          else if(Sreq == 3'd0 && isen)
          begin
            vcgs = 1;
            ence = 0;
          end
          else if(Injectreq == 3'd0 && injecten)
          begin
            vcginjec = 1;
            ence = 0;
          end
        end
        3'b001:
        begin
          if(Wreq == 3'd0 && iwen)
          begin
            vcgw = 1;
            ence = 0;
          end
          else if(Nreq == 3'd0 && inen)
          begin
            vcgn = 1;
            ence = 0;
          end
          else if(Sreq == 3'd0 && isen)
          begin
            vcgs = 1;
            ence = 0;
          end
          else if(Injectreq == 3'd0 && injecten)
          begin
            vcginjec = 1;
            ence = 0;
          end
          else if(Ereq == 3'd0 && ieen)
          begin
            vcge = 1;
            ence = 0;
          end
        end
        3'b010:
        begin
          if(Nreq == 3'd0 && inen)
          begin
            vcgn = 1;
            ence = 0;
          end
          else if(Sreq == 3'd0 && isen)
          begin
            vcgs = 1;
            ence = 0;
          end
          else if(Injectreq == 3'd0 && injecten)
          begin
            vcginjec = 1;
            ence = 0;
          end
          else if(Ereq == 3'd0 && ieen)
          begin
            vcge = 1;
            ence = 0;
          end
          else if(Wreq == 3'd0 && iwen)
          begin
            vcgw = 1;
            ence = 0;
          end
        end
        3'b011:
        begin
          if(Sreq == 3'd0 && isen)
          begin
            vcgs = 1;
            ence = 0;
          end
          else if(Injectreq == 3'd0 && injecten)
          begin
            vcginjec = 1;
            ence = 0;
          end
          else if(Ereq == 3'd0 && ieen)
          begin
            vcge = 1;
            ence = 0;
          end
          else if(Wreq == 3'd0 && iwen)
          begin
            vcgw = 1;
            ence = 0;
          end
          else if(Nreq == 3'd0 && inen)
          begin
            vcgn = 1;
            ence = 0;
          end
        end
        3'b100:
        begin
          if(Injectreq == 3'd0 && injecten)
          begin
            vcginjec = 1;
            ence = 0;
          end
          else if(Ereq == 3'd0 && ieen)
          begin
            vcge = 1;
            ence = 0;
          end
          else if(Wreq == 3'd0 && iwen)
          begin
            vcgw = 1;
            ence = 0;
          end
          else if(Nreq == 3'd0 && inen)
          begin
            vcgn = 1;
            ence = 0;
          end
          else if(Sreq == 3'd0 && isen)
          begin
            vcgs = 1;
            ence = 0;
          end
        end
        default:
          {vcge, vcgw, vcgn, vcgs, vcginjec} = 5'b0;
      endcase
    end
    
    if(owen == 1)
    begin
      case (countw)
        3'b000:
        begin
          if(Ereq == 3'd1 && ieen)
          begin
            vcge = 1;
            encw = 0;
          end
          else if(Wreq == 3'd1 && iwen)
          begin
            vcgw = 1;
            encw = 0;
          end
          else if(Nreq == 3'd1 && inen)
          begin
            vcgn = 1;
            encw = 0;
          end
          else if(Sreq == 3'd1 && isen)
          begin
            vcgs = 1;
            encw = 0;
          end
          else if(Injectreq == 3'd1 && injecten)
          begin
            vcginjec = 1;
            encw = 0;
          end
        end
        3'b001:
        begin
          if(Wreq == 3'd1 && iwen)
          begin
            vcgw = 1;
            encw = 0;
          end
          else if(Nreq == 3'd1 && inen)
          begin
            vcgn = 1;
            encw = 0;
          end
          else if(Sreq == 3'd1 && isen)
          begin
            vcgs = 1;
            encw = 0;
          end
          else if(Injectreq == 3'd1 && injecten)
          begin
            vcginjec = 1;
            encw = 0;
          end
          else if(Ereq == 3'd1 && ieen)
          begin
            vcge = 1;
            encw = 0;
          end
        end
        3'b010:
        begin
          if(Nreq == 3'd1 && inen)
          begin
            vcgn = 1;
            encw = 0;
          end
          else if(Sreq == 3'd1 && isen)
          begin
            vcgs = 1;
            encw = 0;
          end
          else if(Injectreq == 3'd1 && injecten)
          begin
            vcginjec = 1;
            encw = 0;
          end
          else if(Ereq == 3'd1 && ieen)
          begin
            vcge = 1;
            encw = 0;
          end
          else if(Wreq == 3'd1 && iwen)
          begin
            vcgw = 1;
            encw = 0;
          end
        end
        3'b011:
        begin
          if(Sreq == 3'd1 && isen)
          begin
            vcgs = 1;
            encw = 0;
          end
          else if(Injectreq == 3'd1 && injecten)
          begin
            vcginjec = 1;
            encw = 0;
          end
          else if(Ereq == 3'd1 && ieen)
          begin
            vcge = 1;
            encw = 0;
          end
          else if(Wreq == 3'd1 && iwen)
          begin
            vcgw = 1;
            encw = 0;
          end
          else if(Nreq == 3'd1 && inen)
          begin
            vcgn = 1;
            encw = 0;
          end
        end
        3'b100:
        begin
          if(Injectreq == 3'd1 && injecten)
          begin
            vcginjec = 1;
            encw = 0;
          end
          else if(Ereq == 3'd1 && ieen)
          begin
            vcge = 1;
            encw = 0;
          end
          else if(Wreq == 3'd1 && iwen)
          begin
            vcgw = 1;
            encw = 0;
          end
          else if(Nreq == 3'd1 && inen)
          begin
            vcgn = 1;
            encw = 0;
          end
          else if(Sreq == 3'd1 && isen)
          begin
            vcgs = 1;
            encw = 0;
          end
        end
        default:
          {vcge, vcgw, vcgn, vcgs, vcginjec} = 5'b0;
      endcase
    end
    
    if(onen == 1)
    begin
      case (countn)
        3'b000:
        begin
          if(Ereq == 3'd2 && ieen)
          begin
            vcge = 1;
            encn = 0;
          end
          else if(Wreq == 3'd2 && iwen)
          begin
            vcgw = 1;
            encn = 0;
          end
          else if(Nreq == 3'd2 && inen)
          begin
            vcgn = 1;
            encn = 0;
          end
          else if(Sreq == 3'd2 && isen)
          begin
            vcgs = 1;
            encn = 0;
          end
          else if(Injectreq == 3'd2 && injecten)
          begin
            vcginjec = 1;
            encn = 0;
          end
        end
        3'b001:
        begin
          if(Wreq == 3'd2 && iwen)
          begin
            vcgw = 1;
            encn = 0;
          end
          else if(Nreq == 3'd2 && inen)
          begin
            vcgn = 1;
            encn = 0;
          end
          else if(Sreq == 3'd2 && isen)
          begin
            vcgs = 1;
            encn = 0;
          end
          else if(Injectreq == 3'd2 && injecten)
          begin
            vcginjec = 1;
            encn = 0;
          end
          else if(Ereq == 3'd2 && ieen)
          begin
            vcge = 1;
            encn = 0;
          end
        end
        3'b010:
        begin
          if(Nreq == 3'd2 && inen)
          begin
            vcgn = 1;
            encn = 0;
          end
          else if(Sreq == 3'd2 && isen)
          begin
            vcgs = 1;
            encn = 0;
          end
          else if(Injectreq == 3'd2 && injecten)
          begin
            vcginjec = 1;
            encn = 0;
          end
          else if(Ereq == 3'd2 && ieen)
          begin
            vcge = 1;
            encn = 0;
          end
          else if(Wreq == 3'd2 && iwen)
          begin
            vcgw = 1;
            encn = 0;
          end
        end
        3'b011:
        begin
          if(Sreq == 3'd2 && isen)
          begin
            vcgs = 1;
            encn = 0;
          end
          else if(Injectreq == 3'd2 && injecten)
          begin
            vcginjec = 1;
            encn = 0;
          end
          else if(Ereq == 3'd2 && ieen)
          begin
            vcge = 1;
            encn = 0;
          end
          else if(Wreq == 3'd2 && iwen)
          begin
            vcgw = 1;
            encn = 0;
          end
          else if(Nreq == 3'd2 && inen)
          begin
            vcgn = 1;
            encn = 0;
          end
        end
        3'b100:
        begin
          if(Injectreq == 3'd2 && injecten)
          begin
            vcginjec = 1;
            encn = 0;
          end
          else if(Ereq == 3'd2 && ieen)
          begin
            vcge = 1;
            encn = 0;
          end
          else if(Wreq == 3'd2 && iwen)
          begin
            vcgw = 1;
            encn = 0;
          end
          else if(Nreq == 3'd2 && inen)
          begin
            vcgn = 1;
            encn = 0;
          end
          else if(Sreq == 3'd2 && isen)
          begin
            vcgs = 1;
            encn = 0;
          end
        end
        default:
          {vcge, vcgw, vcgn, vcgs, vcginjec} = 5'b0;
      endcase
    end
    
    if(osen == 1)
    begin
      case (counts)
        3'b000:
        begin
          if(Ereq == 3'd3 && ieen)
          begin
            vcge = 1;
            encs = 0;
          end
          else if(Wreq == 3'd3 && iwen)
          begin
            vcgw = 1;
            encs = 0;
          end
          else if(Nreq == 3'd3 && inen)
          begin
            vcgn = 1;
            encs = 0;
          end
          else if(Sreq == 3'd3 && isen)
          begin
            vcgs = 1;
            encs = 0;
          end
          else if(Injectreq == 3'd3 && injecten)
          begin
            vcginjec = 1;
            encs = 0;
          end
        end
        3'b001:
        begin
          if(Wreq == 3'd3 && iwen)
          begin
            vcgw = 1;
            encs = 0;
          end
          else if(Nreq == 3'd3 && inen)
          begin
            vcgn = 1;
            encs = 0;
          end
          else if(Sreq == 3'd3 && isen)
          begin
            vcgs = 1;
            encs = 0;
          end
          else if(Injectreq == 3'd3 && injecten)
          begin
            vcginjec = 1;
            encs = 0;
          end
          else if(Ereq == 3'd3 && ieen)
          begin
            vcge = 1;
            encs = 0;
          end
        end
        3'b010:
        begin
          if(Nreq == 3'd3 && inen)
          begin
            vcgn = 1;
            encs = 0;
          end
          else if(Sreq == 3'd3 && isen)
          begin
            vcgs = 1;
            encs = 0;
          end
          else if(Injectreq == 3'd3 && injecten)
          begin
            vcginjec = 1;
            encs = 0;
          end
          else if(Ereq == 3'd3 && ieen)
          begin
            vcge = 1;
            encs = 0;
          end
          else if(Wreq == 3'd3 && iwen)
          begin
            vcgw = 1;
            encs = 0;
          end
        end
        3'b011:
        begin
          if(Sreq == 3'd3 && isen)
          begin
            vcgs = 1;
            encs = 0;
          end
          else if(Injectreq == 3'd3 && injecten)
          begin
            vcginjec = 1;
            encs = 0;
          end
          else if(Ereq == 3'd3 && ieen)
          begin
            vcge = 1;
            encs = 0;
          end
          else if(Wreq == 3'd3 && iwen)
          begin
            vcgw = 1;
            encs = 0;
          end
          else if(Nreq == 3'd3 && inen)
          begin
            vcgn = 1;
            encs = 0;
          end
        end
        3'b100:
        begin
          if(Injectreq == 3'd3 && injecten)
          begin
            vcginjec = 1;
            encs = 0;
          end
          else if(Ereq == 3'd3 && ieen)
          begin
            vcge = 1;
            encs = 0;
          end
          else if(Wreq == 3'd3 && iwen)
          begin
            vcgw = 1;
            encs = 0;
          end
          else if(Nreq == 3'd3 && inen)
          begin
            vcgn = 1;
            encs = 0;
          end
          else if(Sreq == 3'd3 && isen)
          begin
            vcgs = 1;
            encs = 0;
          end
        end
        default:
          {vcge, vcgw, vcgn, vcgs, vcginjec} = 5'b0;
      endcase
    end
    
    if(ejecten == 1)
    begin
      case (countj)
        3'b000:
        begin
          if(Ereq == 3'd4 && ieen)
          begin
            vcge = 1;
            encj = 0;
          end
          else if(Wreq == 3'd4 && iwen)
          begin
            vcgw = 1;
            encj = 0;
          end
          else if(Nreq == 3'd4 && inen)
          begin
            vcgn = 1;
            encj = 0;
          end
          else if(Sreq == 3'd4 && isen)
          begin
            vcgs = 1;
            encj = 0;
          end
          else if(Injectreq == 3'd4 && injecten)
          begin
            vcginjec = 1;
            encj = 0;
          end
        end
        3'b001:
        begin
          if(Wreq == 3'd4 && iwen)
          begin
            vcgw = 1;
            encj = 0;
          end
          else if(Nreq == 3'd4 && inen)
          begin
            vcgn = 1;
            encj = 0;
          end
          else if(Sreq == 3'd4 && isen)
          begin
            vcgs = 1;
            encj = 0;
          end
          else if(Injectreq == 3'd4 && injecten)
          begin
            vcginjec = 1;
            encj = 0;
          end
          else if(Ereq == 3'd4 && ieen)
          begin
            vcge = 1;
            encj = 0;
          end
        end
        3'b010:
        begin
          if(Nreq == 3'd4 && inen)
          begin
            vcgn = 1;
            encj = 0;
          end
          else if(Sreq == 3'd4 && isen)
          begin
            vcgs = 1;
            encj = 0;
          end
          else if(Injectreq == 3'd4 && injecten)
          begin
            vcginjec = 1;
            encj = 0;
          end
          else if(Ereq == 3'd4 && ieen)
          begin
            vcge = 1;
            encj = 0;
          end
          else if(Wreq == 3'd4 && iwen)
          begin
            vcgw = 1;
            encj = 0;
          end
        end
        3'b011:
        begin
          if(Sreq == 3'd4 && isen)
          begin
            vcgs = 1;
            encj = 0;
          end
          else if(Injectreq == 3'd4 && injecten)
          begin
            vcginjec = 1;
            encj = 0;
          end
          else if(Ereq == 3'd4 && ieen)
          begin
            vcge = 1;
            encj = 0;
          end
          else if(Wreq == 3'd4 && iwen)
          begin
            vcgw = 1;
            encj = 0;
          end
          else if(Nreq == 3'd4 && inen)
          begin
            vcgn = 1;
            encj = 0;
          end
        end
        3'b100:
        begin
          if(Injectreq == 3'd4 && injecten)
          begin
            vcginjec = 1;
            encj = 0;
          end
          else if(Ereq == 3'd4 && ieen)
          begin
            vcge = 1;
            encj = 0;
          end
          else if(Wreq == 3'd4 && iwen)
          begin
            vcgw = 1;
            encj = 0;
          end
          else if(Nreq == 3'd4 && inen)
          begin
            vcgn = 1;
            encj = 0;
          end
          else if(Sreq == 3'd4 && isen)
          begin
            vcgs = 1;
            encj = 0;
          end
        end
        default:
          {vcge, vcgw, vcgn, vcgs, vcginjec} = 5'b0;
      endcase
    end
    end
    
  end
endmodule


