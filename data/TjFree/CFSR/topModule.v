module top ();
reg clk, rst;
reg[7:0] xq;
reg[7:0] xd;
reg[4:0] qcnt;

integer i;
integer out;
initial
begin
    clk = 0;
   forever #10 clk = ~clk;
end
initial begin
    rst = 0;
    # 50 rst = 1;
end
always @(posedge clk or
    negedge rst)
begin
    if (!rst)
    begin
        xq <= 'hed;
        qcnt <= 0;
        out = $fopen("top.vec","w");
    end
    else
    begin
        xq <= xd;
        qcnt <= qcnt + 1;
        $fdisplay(out, "Pass %d Shift value in hex %b", qcnt, xq);
    end
end
always @(*)
begin
    xd = xq;
    xd[7] = xq[0];
    for (i=0; i<7; i=i+1)
    begin
        xd[i] = xq[i+1];
    end
end
endmodule


