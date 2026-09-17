`timescale 1ns / 1ps

module top(
input clk,rstn,
input [3:0] REQ,
output reg [3:0] GNT
    );
    reg[2:0] prstate;
    reg[2:0] nxtstate;
    
    parameter [2:0] Sideal = 3'b000;
    parameter [2:0]     S0 = 3'b001;
    parameter [2:0]     S1 = 3'b010;
    parameter [2:0]     S2 = 3'b011;
    parameter [2:0]     S3 = 3'b100;
    
    always @(posedge clk or negedge rstn)
    
    begin
    if(!rstn)
     prstate <= Sideal;
     else 
      prstate <=nxtstate;
     end
      
    always@(*)
    begin   
          case(prstate) 
            Sideal:
                     begin 
                         if(REQ[0])
                             nxtstate = S0;
                         else if (REQ[1])
                              nxtstate = S1;
                         else if (REQ[2])
                            nxtstate = S2;
                         else if (REQ[3])
                            nxtstate = S3;
                          else 
                             nxtstate =Sideal;
                     end 
               S0: 
                     begin   
                         if (REQ[1])
                            nxtstate = S1;
                         else if (REQ[2])
                            nxtstate = S2;
                         else if (REQ[3])
                              nxtstate = S3;
                         else if(REQ[0])
                             nxtstate =S0;
                         else 
                             nxtstate =Sideal;
                     end 
            
               S1: 
                     begin   
                          if (REQ[2])
                            nxtstate = S2;
                         else if (REQ[3])
                              nxtstate = S3;
                         else if(REQ[0])
                             nxtstate =S0;
                           else if (REQ[1])
                            nxtstate = S1;
                            else 
                             nxtstate =Sideal;
                     end 
               S2: 
                     begin   
                        if (REQ[3])
                              nxtstate = S3;
                         else if(REQ[0])
                             nxtstate =S0;
                           else if (REQ[1])
                            nxtstate = S1;
                            else if (REQ[2])
                            nxtstate = S2;
                            else 
                             nxtstate =Sideal;
                     end 
                 S3: 
                     begin   
                            if(REQ[0])
                             nxtstate =S0;
                           else if (REQ[1])
                            nxtstate = S1;
                            else if (REQ[2])
                            nxtstate = S2;
                            else if (REQ[3])
                              nxtstate = S3;
                            else 
                             nxtstate =Sideal;
                     end 
                    default: 
                     begin 
                         if(REQ[0])
                             nxtstate = S0;
                         else if (REQ[1])
                              nxtstate = S1;
                         else if (REQ[2])
                            nxtstate = S2;
                         else if (REQ[3])
                            nxtstate = S3;
                          else 
                             nxtstate =Sideal;
                    end
       endcase         
         
 end         
          
    always @(*)
     begin
        case (prstate)
        S0: GNT=4'b0001;
        S1: GNT=4'b0010;
        S2: GNT=4'b0011;
        S3: GNT=4'b0100;
        default: GNT=4'b0000;
        endcase
     end
    

    
endmodule 


