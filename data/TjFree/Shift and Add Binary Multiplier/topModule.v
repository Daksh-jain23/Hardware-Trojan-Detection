module adder(
    D,A,addout,cout
    );
    parameter m=8,n=8;
    input [m-1:0] D,A;
    output [m-1:0] addout;
    output cout;
    wire [m:0] addresult, data1, data2;
    assign data1 = {1'b0,D};
    assign data2 = {1'b0,A};
    assign addresult = data1+data2;
    assign addout = addresult[m-1:0];
    assign cout = addresult[m];
endmodule

module controller(clk,rst,lsb,loadcmd,addcmd,shiftcmd,outcmd);
    input clk, rst,lsb;
    output loadcmd,addcmd,shiftcmd,outcmd;
    reg loadcmd,addcmd,shiftcmd, outcmd;
    reg [2:0] state;
    reg start;
    integer count;
    parameter m=8;
    parameter n=8;
    parameter idle=3'b000, init=3'b001, test=3'b010, add=3'b011, shift=3'b100;
    always@(posedge clk or posedge rst)
        if (rst)
            begin
                state<=idle;
                count<=0;
                start<=1;
                outcmd<=0;
            end
        else 
            case (state)
                idle: begin
                    loadcmd<=0;
                    addcmd<=0;
                    shiftcmd<=0;
                    if (start) begin
                        state<=init;
                        outcmd<=0;
                    end
                    else begin
                        state<=idle;
                        outcmd<=1;
                    end
                end
                init: begin
                    loadcmd<=1;
                    addcmd<=0;
                    shiftcmd<=0;
                    outcmd<=0;
                    state<=test;
                end
                test: begin
                    loadcmd<=0;
                    addcmd<=0;
                    shiftcmd<=0;
                    outcmd<=0;
                    if (lsb) begin
                        state<=add;
                        end
                    else state<=shift;
                end 
                add: begin
                    loadcmd<=0;
                    addcmd<=1;
                    shiftcmd<=0;
                    outcmd<=0;
                    state<=shift;
                end
                shift: begin
                    loadcmd<=0;
                    addcmd<=0;
                    shiftcmd<=1;
                    outcmd<=0;
                    if (count<m) begin
                        state<=test;
                        count<=count+1;
                    end
                    else begin
                        count<=0;
                        state<=idle;
                        start<=0;
                    end
                end 
            endcase                
endmodule

module shifter(
    addout,cout,loadcmd,addcmd,shiftcmd,clk,rst,outcmd,Q,A,lsb,out   
 );
 parameter m=8,n=8;
 input [m-1:0] addout;
 input cout,loadcmd,addcmd,shiftcmd,clk,rst,outcmd;
 input [n-1:0] Q;
 output [m-1:0] A;
 output lsb;
 output reg [m+n-1:0] out; 
 reg [m+n:0] temp;
 reg addtemp;
 
 assign A = temp[m+n-1:n];
 assign lsb = temp[0];
 always@(posedge clk or posedge rst)
 begin
    if (rst)
    begin
        addtemp<=0;
        temp<=0;
    end
    else
    begin
        if (loadcmd)
        begin
            temp[m+n:n]<=0;
            temp[n-1:0]<=Q;
        end
        else if (addcmd)
            addtemp<=1;
        else if (shiftcmd && addtemp)
        begin
            temp<={1'b0, cout, addout, temp[n-1:1]};
            addtemp<=0;
        end
        else if (shiftcmd && !addtemp)
            temp<={1'b0, temp[m+n:1]}; 
    end
 end
 always@(outcmd)
 begin
    if (!outcmd)
        out<=0;
    else
        out<=temp[m+n-1:0];
 end
 endmodule

module top(clk, rst, D, Q, out);
parameter m=8, n=8;
input clk, rst;
input [m-1:0] D;
input [n-1:0] Q;
output [m+n-1:0] out;

wire cout,loadcmd,addcmd,shiftcmd,lsb,outcmd;
wire [m-1:0] A,addout;
adder adder(.D(D), .A(A), .addout(addout), .cout(cout));
shifter shifter(addout,cout,loadcmd,addcmd,shiftcmd,clk,rst,outcmd,Q,A,lsb,out);
controller controller(clk,rst,lsb,loadcmd,addcmd,shiftcmd,outcmd);
endmodule




