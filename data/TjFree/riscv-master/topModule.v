
module dcache
#(
     parameter AXIID           = 0
)
(
    
     input           clki
    ,input           rsti
    ,input  [ 31:0]  memaddri
    ,input  [ 31:0]  memdatawri
    ,input           memrdi
    ,input  [  3:0]  memwri
    ,input           memcacheablei
    ,input  [ 10:0]  memreqtagi
    ,input           meminvalidatei
    ,input           memwritebacki
    ,input           memflushi
    ,input           axiawreadyi
    ,input           axiwreadyi
    ,input           axibvalidi
    ,input  [  1:0]  axibrespi
    ,input  [  3:0]  axibidi
    ,input           axiarreadyi
    ,input           axirvalidi
    ,input  [ 31:0]  axirdatai
    ,input  [  1:0]  axirrespi
    ,input  [  3:0]  axiridi
    ,input           axirlasti

    
    ,output [ 31:0]  memdatardo
    ,output          memaccepto
    ,output          memacko
    ,output          memerroro
    ,output [ 10:0]  memresptago
    ,output          axiawvalido
    ,output [ 31:0]  axiawaddro
    ,output [  3:0]  axiawido
    ,output [  7:0]  axiawleno
    ,output [  1:0]  axiawbursto
    ,output          axiwvalido
    ,output [ 31:0]  axiwdatao
    ,output [  3:0]  axiwstrbo
    ,output          axiwlasto
    ,output          axibreadyo
    ,output          axiarvalido
    ,output [ 31:0]  axiaraddro
    ,output [  3:0]  axiarido
    ,output [  7:0]  axiarleno
    ,output [  1:0]  axiarbursto
    ,output          axirreadyo
);

wire           memuncachedinvalidatew;
wire           pmemcacheacceptw;
wire           memuncachedacceptw;
wire  [  7:0]  pmemcachelenw;
wire  [  3:0]  memcachedwrw;
wire  [ 31:0]  pmemcachereaddataw;
wire           memcachedinvalidatew;
wire           pmemuncachedackw;
wire  [  7:0]  pmemlenw;
wire           pmemuncachedacceptw;
wire           memcachedacceptw;
wire           pmemcacheackw;
wire  [ 31:0]  pmemcacheaddrw;
wire           pmemcacherdw;
wire           pmemerrorw;
wire  [ 31:0]  pmemaddrw;
wire  [ 10:0]  memcachedreqtagw;
wire           memuncachedackw;
wire           pmemackw;
wire  [ 31:0]  memuncacheddatawrw;
wire  [ 31:0]  pmemuncachedaddrw;
wire  [ 31:0]  memcacheddatardw;
wire  [ 31:0]  pmemuncachedreaddataw;
wire           memuncachedflushw;
wire           pmemuncachederrorw;
wire  [ 31:0]  memuncacheddatardw;
wire  [ 31:0]  pmemwritedataw;
wire  [  3:0]  pmemuncachedwrw;
wire           memcachedrdw;
wire  [ 10:0]  memcachedresptagw;
wire  [  7:0]  pmemuncachedlenw;
wire  [ 31:0]  memcacheddatawrw;
wire  [  3:0]  pmemwrw;
wire           pmemselectw;
wire           memcachedflushw;
wire           memuncachedcacheablew;
wire  [ 31:0]  memcachedaddrw;
wire           memuncachedwritebackw;
wire  [  3:0]  pmemcachewrw;
wire           pmemcacheerrorw;
wire  [ 10:0]  memuncachedreqtagw;
wire  [ 31:0]  pmemuncachedwritedataw;
wire  [ 10:0]  memuncachedresptagw;
wire           pmemrdw;
wire           memcachedcacheablew;
wire  [  3:0]  memuncachedwrw;
wire           memuncachederrorw;
wire           memuncachedrdw;
wire           pmemacceptw;
wire  [ 31:0]  pmemcachewritedataw;
wire           memcachederrorw;
wire  [ 31:0]  memuncachedaddrw;
wire           pmemuncachedrdw;
wire  [ 31:0]  pmemreaddataw;
wire           memcachedackw;
wire           memcachedwritebackw;


dcacheifpmem
uuncached
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.memaddri(memuncachedaddrw)
    ,.memdatawri(memuncacheddatawrw)
    ,.memrdi(memuncachedrdw)
    ,.memwri(memuncachedwrw)
    ,.memcacheablei(memuncachedcacheablew)
    ,.memreqtagi(memuncachedreqtagw)
    ,.meminvalidatei(memuncachedinvalidatew)
    ,.memwritebacki(memuncachedwritebackw)
    ,.memflushi(memuncachedflushw)
    ,.outportaccepti(pmemuncachedacceptw)
    ,.outportacki(pmemuncachedackw)
    ,.outporterrori(pmemuncachederrorw)
    ,.outportreaddatai(pmemuncachedreaddataw)

    
    ,.memdatardo(memuncacheddatardw)
    ,.memaccepto(memuncachedacceptw)
    ,.memacko(memuncachedackw)
    ,.memerroro(memuncachederrorw)
    ,.memresptago(memuncachedresptagw)
    ,.outportwro(pmemuncachedwrw)
    ,.outportrdo(pmemuncachedrdw)
    ,.outportleno(pmemuncachedlenw)
    ,.outportaddro(pmemuncachedaddrw)
    ,.outportwritedatao(pmemuncachedwritedataw)
);


dcachepmemmux
upmemmux
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.outportaccepti(pmemacceptw)
    ,.outportacki(pmemackw)
    ,.outporterrori(pmemerrorw)
    ,.outportreaddatai(pmemreaddataw)
    ,.selecti(pmemselectw)
    ,.inport0wri(pmemuncachedwrw)
    ,.inport0rdi(pmemuncachedrdw)
    ,.inport0leni(pmemuncachedlenw)
    ,.inport0addri(pmemuncachedaddrw)
    ,.inport0writedatai(pmemuncachedwritedataw)
    ,.inport1wri(pmemcachewrw)
    ,.inport1rdi(pmemcacherdw)
    ,.inport1leni(pmemcachelenw)
    ,.inport1addri(pmemcacheaddrw)
    ,.inport1writedatai(pmemcachewritedataw)

    
    ,.outportwro(pmemwrw)
    ,.outportrdo(pmemrdw)
    ,.outportleno(pmemlenw)
    ,.outportaddro(pmemaddrw)
    ,.outportwritedatao(pmemwritedataw)
    ,.inport0accepto(pmemuncachedacceptw)
    ,.inport0acko(pmemuncachedackw)
    ,.inport0erroro(pmemuncachederrorw)
    ,.inport0readdatao(pmemuncachedreaddataw)
    ,.inport1accepto(pmemcacheacceptw)
    ,.inport1acko(pmemcacheackw)
    ,.inport1erroro(pmemcacheerrorw)
    ,.inport1readdatao(pmemcachereaddataw)
);


dcachemux
umux
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.memaddri(memaddri)
    ,.memdatawri(memdatawri)
    ,.memrdi(memrdi)
    ,.memwri(memwri)
    ,.memcacheablei(memcacheablei)
    ,.memreqtagi(memreqtagi)
    ,.meminvalidatei(meminvalidatei)
    ,.memwritebacki(memwritebacki)
    ,.memflushi(memflushi)
    ,.memcacheddatardi(memcacheddatardw)
    ,.memcachedaccepti(memcachedacceptw)
    ,.memcachedacki(memcachedackw)
    ,.memcachederrori(memcachederrorw)
    ,.memcachedresptagi(memcachedresptagw)
    ,.memuncacheddatardi(memuncacheddatardw)
    ,.memuncachedaccepti(memuncachedacceptw)
    ,.memuncachedacki(memuncachedackw)
    ,.memuncachederrori(memuncachederrorw)
    ,.memuncachedresptagi(memuncachedresptagw)

    
    ,.memdatardo(memdatardo)
    ,.memaccepto(memaccepto)
    ,.memacko(memacko)
    ,.memerroro(memerroro)
    ,.memresptago(memresptago)
    ,.memcachedaddro(memcachedaddrw)
    ,.memcacheddatawro(memcacheddatawrw)
    ,.memcachedrdo(memcachedrdw)
    ,.memcachedwro(memcachedwrw)
    ,.memcachedcacheableo(memcachedcacheablew)
    ,.memcachedreqtago(memcachedreqtagw)
    ,.memcachedinvalidateo(memcachedinvalidatew)
    ,.memcachedwritebacko(memcachedwritebackw)
    ,.memcachedflusho(memcachedflushw)
    ,.memuncachedaddro(memuncachedaddrw)
    ,.memuncacheddatawro(memuncacheddatawrw)
    ,.memuncachedrdo(memuncachedrdw)
    ,.memuncachedwro(memuncachedwrw)
    ,.memuncachedcacheableo(memuncachedcacheablew)
    ,.memuncachedreqtago(memuncachedreqtagw)
    ,.memuncachedinvalidateo(memuncachedinvalidatew)
    ,.memuncachedwritebacko(memuncachedwritebackw)
    ,.memuncachedflusho(memuncachedflushw)
    ,.cacheactiveo(pmemselectw)
);


dcachecore
ucore
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.memaddri(memcachedaddrw)
    ,.memdatawri(memcacheddatawrw)
    ,.memrdi(memcachedrdw)
    ,.memwri(memcachedwrw)
    ,.memcacheablei(memcachedcacheablew)
    ,.memreqtagi(memcachedreqtagw)
    ,.meminvalidatei(memcachedinvalidatew)
    ,.memwritebacki(memcachedwritebackw)
    ,.memflushi(memcachedflushw)
    ,.outportaccepti(pmemcacheacceptw)
    ,.outportacki(pmemcacheackw)
    ,.outporterrori(pmemcacheerrorw)
    ,.outportreaddatai(pmemcachereaddataw)

    
    ,.memdatardo(memcacheddatardw)
    ,.memaccepto(memcachedacceptw)
    ,.memacko(memcachedackw)
    ,.memerroro(memcachederrorw)
    ,.memresptago(memcachedresptagw)
    ,.outportwro(pmemcachewrw)
    ,.outportrdo(pmemcacherdw)
    ,.outportleno(pmemcachelenw)
    ,.outportaddro(pmemcacheaddrw)
    ,.outportwritedatao(pmemcachewritedataw)
);


dcacheaxi
#(
     .AXIID(AXIID)
)
uaxi
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.outportawreadyi(axiawreadyi)
    ,.outportwreadyi(axiwreadyi)
    ,.outportbvalidi(axibvalidi)
    ,.outportbrespi(axibrespi)
    ,.outportbidi(axibidi)
    ,.outportarreadyi(axiarreadyi)
    ,.outportrvalidi(axirvalidi)
    ,.outportrdatai(axirdatai)
    ,.outportrrespi(axirrespi)
    ,.outportridi(axiridi)
    ,.outportrlasti(axirlasti)
    ,.inportwri(pmemwrw)
    ,.inportrdi(pmemrdw)
    ,.inportleni(pmemlenw)
    ,.inportaddri(pmemaddrw)
    ,.inportwritedatai(pmemwritedataw)

    
    ,.outportawvalido(axiawvalido)
    ,.outportawaddro(axiawaddro)
    ,.outportawido(axiawido)
    ,.outportawleno(axiawleno)
    ,.outportawbursto(axiawbursto)
    ,.outportwvalido(axiwvalido)
    ,.outportwdatao(axiwdatao)
    ,.outportwstrbo(axiwstrbo)
    ,.outportwlasto(axiwlasto)
    ,.outportbreadyo(axibreadyo)
    ,.outportarvalido(axiarvalido)
    ,.outportaraddro(axiaraddro)
    ,.outportarido(axiarido)
    ,.outportarleno(axiarleno)
    ,.outportarbursto(axiarbursto)
    ,.outportrreadyo(axirreadyo)
    ,.inportaccepto(pmemacceptw)
    ,.inportacko(pmemackw)
    ,.inporterroro(pmemerrorw)
    ,.inportreaddatao(pmemreaddataw)
);



endmodule

module dcacheaxi
#(
     parameter AXIID           = 0
)
(
    
     input           clki
    ,input           rsti
    ,input           outportawreadyi
    ,input           outportwreadyi
    ,input           outportbvalidi
    ,input  [  1:0]  outportbrespi
    ,input  [  3:0]  outportbidi
    ,input           outportarreadyi
    ,input           outportrvalidi
    ,input  [ 31:0]  outportrdatai
    ,input  [  1:0]  outportrrespi
    ,input  [  3:0]  outportridi
    ,input           outportrlasti
    ,input  [  3:0]  inportwri
    ,input           inportrdi
    ,input  [  7:0]  inportleni
    ,input  [ 31:0]  inportaddri
    ,input  [ 31:0]  inportwritedatai

    
    ,output          outportawvalido
    ,output [ 31:0]  outportawaddro
    ,output [  3:0]  outportawido
    ,output [  7:0]  outportawleno
    ,output [  1:0]  outportawbursto
    ,output          outportwvalido
    ,output [ 31:0]  outportwdatao
    ,output [  3:0]  outportwstrbo
    ,output          outportwlasto
    ,output          outportbreadyo
    ,output          outportarvalido
    ,output [ 31:0]  outportaraddro
    ,output [  3:0]  outportarido
    ,output [  7:0]  outportarleno
    ,output [  1:0]  outportarbursto
    ,output          outportrreadyo
    ,output          inportaccepto
    ,output          inportacko
    ,output          inporterroro
    ,output [ 31:0]  inportreaddatao
);




wire          bvalidw;
wire          rvalidw;
wire [1:0]    brespw;
wire [1:0]    rrespw;
wire          acceptw;

wire          resacceptw;
wire          reqacceptw;

wire          resvalidw;
wire          reqvalidw;
wire [77-1:0] reqw;

wire          reqpushw    = (inportrdi || inportwri != 4'b0);
wire [77-1:0] reqdatainw = {inportleni, inportrdi, inportwri, inportwritedatai, inportaddri};

dcacheaxififo
#( 
    .ADDRW(1),
    .DEPTH(2),
    .WIDTH(32+32+8+4+1)
)
ureq
(
    .clki(clki),
    .rsti(rsti),

    
    .dataini(reqdatainw),
    .pushi(reqpushw),
    .accepto(reqacceptw),

    
    .valido(reqvalidw),
    .dataouto(reqw),
    .popi(acceptw)
);

wire       reqcanissuew = reqvalidw & resacceptw;
wire       reqisreadw   = (reqcanissuew ? reqw[68] : 1'b0);
wire       reqiswritew  = (reqcanissuew ? ~reqw[68] : 1'b0);
wire [7:0] reqlenw       = reqw[76:69];

assign inportaccepto = reqacceptw;
assign inportacko    = bvalidw || rvalidw;
assign inporterroro  = bvalidw ? (brespw != 2'b0) : (rrespw != 2'b0);

reg  [7:0] reqcntq;

always @ (posedge clki or posedge rsti)
if (rsti)
    reqcntq <= 8'b0;
else if (reqiswritew && reqcntq == 8'd0 && reqlenw != 8'd0 && acceptw)
    reqcntq <= reqlenw - 8'd1;
else if (reqcntq != 8'd0 && reqiswritew && acceptw)
    reqcntq <= reqcntq - 8'd1;

wire reqlastw = (reqiswritew && reqlenw == 8'd0 && reqcntq == 8'd0);

wire respushw = (reqiswritew && reqlastw && acceptw) || (reqisreadw && acceptw);

wire resppopw = outportbvalidi || (outportrvalidi ? outportrlasti : 1'b0);

reg  [1:0] respoutstandingq;

always @ (posedge clki or posedge rsti)
if (rsti)
    respoutstandingq <= 2'b0;
else if ((respushw & resacceptw) & ~(resppopw & resvalidw))
    respoutstandingq <= respoutstandingq + 2'd1;
else if (~(respushw & resacceptw) & (resppopw & resvalidw))
    respoutstandingq <= respoutstandingq - 2'd1;

assign resvalidw   = (respoutstandingq != 2'd0);
assign resacceptw  = (respoutstandingq != 2'd2);

dcacheaxiaxi
uaxi
(
    .clki(clki),
    .rsti(rsti),

    .inportvalidi(reqcanissuew),
    .inportwritei(reqiswritew),
    .inportwdatai(reqw[63:32]),
    .inportwstrbi(reqw[67:64]),    
    .inportaddri({reqw[31:2], 2'b0}),
    .inportidi(AXIID),
    .inportleni(reqlenw),
    .inportbursti(2'b01),
    .inportaccepto(acceptw),

    .inportbreadyi(1'b1),
    .inportrreadyi(1'b1),
    .inportbvalido(bvalidw),
    .inportbrespo(brespw),
    .inportbido(),
    .inportrvalido(rvalidw),
    .inportrdatao(inportreaddatao),
    .inportrrespo(rrespw),
    .inportrido(),
    .inportrlasto(),

    .outportawvalido(outportawvalido),
    .outportawaddro(outportawaddro),
    .outportawido(outportawido),
    .outportawleno(outportawleno),
    .outportawbursto(outportawbursto),
    .outportwvalido(outportwvalido),
    .outportwdatao(outportwdatao),
    .outportwstrbo(outportwstrbo),
    .outportwlasto(outportwlasto),
    .outportbreadyo(outportbreadyo),
    .outportarvalido(outportarvalido),
    .outportaraddro(outportaraddro),
    .outportarido(outportarido),
    .outportarleno(outportarleno),
    .outportarbursto(outportarbursto),
    .outportrreadyo(outportrreadyo),
    .outportawreadyi(outportawreadyi),
    .outportwreadyi(outportwreadyi),
    .outportbvalidi(outportbvalidi),
    .outportbrespi(outportbrespi),
    .outportbidi(outportbidi),
    .outportarreadyi(outportarreadyi),
    .outportrvalidi(outportrvalidi),
    .outportrdatai(outportrdatai),
    .outportrrespi(outportrrespi),
    .outportridi(outportridi),
    .outportrlasti(outportrlasti)
);

endmodule


module dcacheaxififo
#(
    parameter WIDTH   = 8,
    parameter DEPTH   = 4,
    parameter ADDRW  = 2
)
(
    
     input               clki
    ,input               rsti
    ,input  [WIDTH-1:0]  dataini
    ,input               pushi
    ,input               popi

    
    ,output [WIDTH-1:0]  dataouto
    ,output              accepto
    ,output              valido
);

localparam COUNTW = ADDRW + 1;

reg [WIDTH-1:0]   ramq[DEPTH-1:0];
reg [ADDRW-1:0]  rdptrq;
reg [ADDRW-1:0]  wrptrq;
reg [COUNTW-1:0] countq;

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    countq   <= {(COUNTW) {1'b0}};
    rdptrq  <= {(ADDRW) {1'b0}};
    wrptrq  <= {(ADDRW) {1'b0}};
end
else
begin
    
    if (pushi & accepto)
    begin
        ramq[wrptrq] <= dataini;
        wrptrq        <= wrptrq + 1;
    end

    
    if (popi & valido)
        rdptrq      <= rdptrq + 1;

    
    if ((pushi & accepto) & ~(popi & valido))
        countq <= countq + 1;
    
    else if (~(pushi & accepto) & (popi & valido))
        countq <= countq - 1;
end

/* verilator lintoff WIDTH */
assign valido       = (countq != 0);
assign accepto      = (countq != DEPTH);
/* verilator linton WIDTH */

assign dataouto    = ramq[rdptrq];



endmodule

module dcacheaxiaxi
(
    
     input           clki
    ,input           rsti
    ,input           inportvalidi
    ,input           inportwritei
    ,input  [ 31:0]  inportaddri
    ,input  [  3:0]  inportidi
    ,input  [  7:0]  inportleni
    ,input  [  1:0]  inportbursti
    ,input  [ 31:0]  inportwdatai
    ,input  [  3:0]  inportwstrbi
    ,input           inportbreadyi
    ,input           inportrreadyi
    ,input           outportawreadyi
    ,input           outportwreadyi
    ,input           outportbvalidi
    ,input  [  1:0]  outportbrespi
    ,input  [  3:0]  outportbidi
    ,input           outportarreadyi
    ,input           outportrvalidi
    ,input  [ 31:0]  outportrdatai
    ,input  [  1:0]  outportrrespi
    ,input  [  3:0]  outportridi
    ,input           outportrlasti

    
    ,output          inportaccepto
    ,output          inportbvalido
    ,output [  1:0]  inportbrespo
    ,output [  3:0]  inportbido
    ,output          inportrvalido
    ,output [ 31:0]  inportrdatao
    ,output [  1:0]  inportrrespo
    ,output [  3:0]  inportrido
    ,output          inportrlasto
    ,output          outportawvalido
    ,output [ 31:0]  outportawaddro
    ,output [  3:0]  outportawido
    ,output [  7:0]  outportawleno
    ,output [  1:0]  outportawbursto
    ,output          outportwvalido
    ,output [ 31:0]  outportwdatao
    ,output [  3:0]  outportwstrbo
    ,output          outportwlasto
    ,output          outportbreadyo
    ,output          outportarvalido
    ,output [ 31:0]  outportaraddro
    ,output [  3:0]  outportarido
    ,output [  7:0]  outportarleno
    ,output [  1:0]  outportarbursto
    ,output          outportrreadyo
);



reg  [7:0] reqcntq;

always @ (posedge clki or posedge rsti)
if (rsti)
    reqcntq <= 8'b0;
else if (inportvalidi && inportwritei && inportaccepto)
begin
    if (reqcntq != 8'b0)
        reqcntq <= reqcntq - 8'd1;
    else
        reqcntq <= inportleni;
end

reg        validq;
reg [83:0] bufq;

always @ (posedge clki or posedge rsti)
if (rsti)
    validq <= 1'b0;
else if (inportvalidi && inportaccepto && ((outportawvalido && !outportawreadyi) || (outportwvalido && !outportwreadyi) || (outportarvalido && !outportarreadyi)))
    validq <= 1'b1;
else if ((!outportawvalido || outportawreadyi) && (!outportwvalido || outportwreadyi) && (!outportarvalido || outportarreadyi))
    validq <= 1'b0;

wire          inportvalidw = validq || inportvalidi;
wire          inportwritew = validq ? bufq[0:0]   : inportwritei;
wire [ 31:0]  inportaddrw  = validq ? bufq[32:1]  : inportaddri;
wire [  3:0]  inportidw    = validq ? bufq[36:33] : inportidi;
wire [  7:0]  inportlenw   = validq ? bufq[44:37] : inportleni;
wire [  1:0]  inportburstw = validq ? bufq[46:45] : inportbursti;
wire [ 31:0]  inportwdataw = validq ? bufq[78:47] : inportwdatai;
wire [  3:0]  inportwstrbw = validq ? bufq[82:79] : inportwstrbi;
wire          inportwlastw = validq ? bufq[83:83] : (inportleni == 8'd0 && reqcntq == 8'd0) || (reqcntq == 8'd1);

always @ (posedge clki or posedge rsti)
if (rsti)
    bufq <= 84'b0;
else
    bufq <= {inportwlastw, inportwstrbw, inportwdataw, inportburstw, inportlenw, inportidw, inportaddrw, inportwritew};

wire skidbusyw = validq;

reg awvalidq;
reg wvalidq;
reg wlastq;

wire wrcmdacceptedw  = (outportawvalido && outportawreadyi) || awvalidq;
wire wrdataacceptedw = (outportwvalido  && outportwreadyi)  || wvalidq;
wire wrdatalastw     = (wvalidq & wlastq) || (outportwvalido && outportwreadyi && outportwlasto);

always @ (posedge clki or posedge rsti)
if (rsti)
    awvalidq <= 1'b0;
else if (outportawvalido && outportawreadyi && (!wrdataacceptedw || !wrdatalastw))
    awvalidq <= 1'b1;
else if (wrdataacceptedw && wrdatalastw)
    awvalidq <= 1'b0;

always @ (posedge clki or posedge rsti)
if (rsti)
    wvalidq <= 1'b0;
else if (outportwvalido && outportwreadyi && !wrcmdacceptedw)
    wvalidq <= 1'b1;
else if (wrcmdacceptedw)
    wvalidq <= 1'b0;

always @ (posedge clki or posedge rsti)
if (rsti)
    wlastq <= 1'b0;
else if (outportwvalido && outportwreadyi)
    wlastq <= outportwlasto;

assign outportawvalido = (inportvalidw & inportwritew & ~awvalidq);
assign outportawaddro  = inportaddrw;
assign outportawido    = inportidw;
assign outportawleno   = inportlenw;
assign outportawbursto = inportburstw;

assign outportwvalido  = (inportvalidw & inportwritew & ~wvalidq);
assign outportwdatao   = inportwdataw;
assign outportwstrbo   = inportwstrbw;
assign outportwlasto   = inportwlastw;

assign inportbvalido   = outportbvalidi;
assign inportbrespo    = outportbrespi;
assign inportbido      = outportbidi;
assign outportbreadyo  = inportbreadyi;

assign outportarvalido = inportvalidw & ~inportwritew;
assign outportaraddro  = inportaddrw;
assign outportarido    = inportidw;
assign outportarleno   = inportlenw;
assign outportarbursto = inportburstw;
assign outportrreadyo  = inportrreadyi;

assign inportrvalido   = outportrvalidi;
assign inportrdatao    = outportrdatai;
assign inportrrespo    = outportrrespi;
assign inportrido      = outportridi;
assign inportrlasto    = outportrlasti;

assign inportaccepto   = !skidbusyw &&
                           ((outportawvalido && outportawreadyi) || 
                            (outportwvalido  && outportwreadyi)  ||
                            (outportarvalido && outportarreadyi));


endmodule

module dcachecore
(
    
     input           clki
    ,input           rsti
    ,input  [ 31:0]  memaddri
    ,input  [ 31:0]  memdatawri
    ,input           memrdi
    ,input  [  3:0]  memwri
    ,input           memcacheablei
    ,input  [ 10:0]  memreqtagi
    ,input           meminvalidatei
    ,input           memwritebacki
    ,input           memflushi
    ,input           outportaccepti
    ,input           outportacki
    ,input           outporterrori
    ,input  [ 31:0]  outportreaddatai

    
    ,output [ 31:0]  memdatardo
    ,output          memaccepto
    ,output          memacko
    ,output          memerroro
    ,output [ 10:0]  memresptago
    ,output [  3:0]  outportwro
    ,output          outportrdo
    ,output [  7:0]  outportleno
    ,output [ 31:0]  outportaddro
    ,output [ 31:0]  outportwritedatao
);



localparam DCACHENUMWAYS           = 2;

localparam DCACHENUMLINES          = 256;
localparam DCACHELINEADDRW        = 8;

localparam DCACHELINESIZEW        = 5;
localparam DCACHELINESIZE          = 32;
localparam DCACHELINEWORDS         = 8;

localparam DCACHETAGREQLINEL     = 5;  
localparam DCACHETAGREQLINEH     = 12; 
localparam DCACHETAGREQLINEW     = 8;  
`define DCACHETAGREQRNG          DCACHETAGREQLINEH:DCACHETAGREQLINEL

`define CACHETAGADDRRNG          18:0
localparam CACHETAGADDRBITS       = 19;
localparam CACHETAGDIRTYBIT       = CACHETAGADDRBITS + 0;
localparam CACHETAGVALIDBIT       = CACHETAGADDRBITS + 1;
localparam CACHETAGDATAW          = CACHETAGADDRBITS + 2;

localparam DCACHETAGCMPADDRL     = DCACHETAGREQLINEH + 1;
localparam DCACHETAGCMPADDRH     = 32-1;
localparam DCACHETAGCMPADDRW     = DCACHETAGCMPADDRH - DCACHETAGCMPADDRL + 1;
`define   DCACHETAGCMPADDRRNG   31:13


localparam STATEW           = 4;
localparam STATERESET       = 4'd0;
localparam STATEFLUSHADDR  = 4'd1;
localparam STATEFLUSH       = 4'd2;
localparam STATELOOKUP      = 4'd3;
localparam STATEREAD        = 4'd4;
localparam STATEWRITE       = 4'd5;
localparam STATEREFILL      = 4'd6;
localparam STATEEVICT       = 4'd7;
localparam STATEEVICTWAIT  = 4'd8;
localparam STATEINVALIDATE  = 4'd9;
localparam STATEWRITEBACK   = 4'd10;

reg [STATEW-1:0]           nextstater;
reg [STATEW-1:0]           stateq;

reg [31:0] memaddrmq;
reg [31:0] memdatamq;
reg [3:0]  memwrmq;
reg        memrdmq;
reg [10:0] memtagmq;
reg        meminvalmq;
reg        memwritebackmq;
reg        memflushmq;

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    memaddrmq      <= 32'b0;
    memdatamq      <= 32'b0;
    memwrmq        <= 4'b0;
    memrdmq        <= 1'b0;
    memtagmq       <= 11'b0;
    meminvalmq     <= 1'b0;
    memwritebackmq <= 1'b0;
    memflushmq     <= 1'b0;
end
else if (memaccepto)
begin
    memaddrmq      <= memaddri;
    memdatamq      <= memdatawri;
    memwrmq        <= memwri;
    memrdmq        <= memrdi;
    memtagmq       <= memreqtagi;
    meminvalmq     <= meminvalidatei;
    memwritebackmq <= memwritebacki;
    memflushmq     <= memflushi;
end
else if (memacko)
begin
    memaddrmq      <= 32'b0;
    memdatamq      <= 32'b0;
    memwrmq        <= 4'b0;
    memrdmq        <= 1'b0;
    memtagmq       <= 11'b0;
    meminvalmq     <= 1'b0;
    memwritebackmq <= 1'b0;
    memflushmq     <= 1'b0;
end

reg memacceptr;

always @ *
begin
    memacceptr = 1'b0;

    if (stateq == STATELOOKUP)
    begin
        
        if ((memrdmq || (memwrmq != 4'b0)) && !taghitanymw)
            memacceptr = 1'b0;
        
        else if ((|memwrmq) && memrdi && memaddri[31:2] == memaddrmq[31:2])
            memacceptr = 1'b0;
        else
            memacceptr = 1'b1;
    end
end

assign memaccepto = memacceptr;

wire [DCACHETAGCMPADDRW-1:0] reqaddrtagcmpmw = memaddrmq[`DCACHETAGCMPADDRRNG];

assign memresptago = memtagmq;

reg [0:0]  replacewayq;

wire  [  3:0]  pmemwrw;
wire           pmemrdw;
wire  [  7:0]  pmemlenw;
wire           pmemlastw;
wire  [ 31:0]  pmemaddrw;
wire  [ 31:0]  pmemwritedataw;
wire           pmemacceptw;
wire           pmemackw;
wire           pmemerrorw;
wire [ 31:0]   pmemreaddataw;

wire           evictwayw;
wire           tagdirtyanymw;
wire           taghitanddirtymw;

reg            flushingq;

reg [DCACHETAGREQLINEW-1:0] tagaddrxr;
reg [DCACHETAGREQLINEW-1:0] tagaddrmr;

always @ *
begin
    
    tagaddrxr = memaddri[`DCACHETAGREQRNG];

    
    if (stateq == STATELOOKUP && (nextstater == STATELOOKUP || nextstater == STATEWRITEBACK))
        tagaddrxr = memaddri[`DCACHETAGREQRNG];
    
    else if (flushingq)
        tagaddrxr = flushaddrq;
    else
        tagaddrxr = memaddrmq[`DCACHETAGREQRNG];        

    
    tagaddrmr = flushaddrq;

    
    if (flushingq || stateq == STATERESET)
        tagaddrmr = flushaddrq;
    
    else
        tagaddrmr = memaddrmq[`DCACHETAGREQRNG];
end

reg [CACHETAGDATAW-1:0] tagdatainmr;
always @ *
begin
    tagdatainmr = {(CACHETAGDATAW){1'b0}};

    
    if (stateq == STATEFLUSH || stateq == STATERESET || flushingq)
        tagdatainmr = {(CACHETAGDATAW){1'b0}};
    
    else if (stateq == STATEREFILL)
    begin
        tagdatainmr[CACHETAGVALIDBIT] = 1'b1;
        tagdatainmr[CACHETAGDIRTYBIT] = 1'b0;
        tagdatainmr[`CACHETAGADDRRNG] = memaddrmq[`DCACHETAGCMPADDRRNG];
    end
    
    else if (stateq == STATEINVALIDATE)
    begin
        tagdatainmr[CACHETAGVALIDBIT] = 1'b0;
        tagdatainmr[CACHETAGDIRTYBIT] = 1'b0;
        tagdatainmr[`CACHETAGADDRRNG] = memaddrmq[`DCACHETAGCMPADDRRNG];
    end
    
    else if (stateq == STATEEVICTWAIT)
    begin
        tagdatainmr[CACHETAGVALIDBIT] = 1'b1;
        tagdatainmr[CACHETAGDIRTYBIT] = 1'b0;
        tagdatainmr[`CACHETAGADDRRNG] = memaddrmq[`DCACHETAGCMPADDRRNG];
    end
    
    else if (stateq == STATEWRITE || (stateq == STATELOOKUP && (|memwrmq)))
    begin
        tagdatainmr[CACHETAGVALIDBIT] = 1'b1;
        tagdatainmr[CACHETAGDIRTYBIT] = 1'b1;
        tagdatainmr[`CACHETAGADDRRNG] = memaddrmq[`DCACHETAGCMPADDRRNG];
    end
end

reg tag0writemr;
always @ *
begin
    tag0writemr = 1'b0;

    
    if (stateq == STATERESET)
        tag0writemr = 1'b1;
    
    else if (stateq == STATEFLUSH)
        tag0writemr = !tagdirtyanymw;
    
    else if (stateq == STATELOOKUP && (|memwrmq))
        tag0writemr = tag0hitmw;
    
    else if (stateq == STATEWRITE)
        tag0writemr = (replacewayq == 0);
    
    else if (stateq == STATEEVICTWAIT && pmemackw)
        tag0writemr = (replacewayq == 0);
    
    else if (stateq == STATEREFILL)
        tag0writemr = pmemackw && pmemlastw && (replacewayq == 0);
    
    else if (stateq == STATEINVALIDATE)
        tag0writemr = tag0hitmw;
end

wire [CACHETAGDATAW-1:0] tag0dataoutmw;

dcachecoretagram
utag0
(
  .clk0i(clki),
  .rst0i(rsti),
  .clk1i(clki),
  .rst1i(rsti),

  
  .addr0i(tagaddrxr),
  .data0o(tag0dataoutmw),

  
  .addr1i(tagaddrmr),
  .data1i(tagdatainmr),
  .wr1i(tag0writemr)
);

wire                           tag0validmw     = tag0dataoutmw[CACHETAGVALIDBIT];
wire                           tag0dirtymw     = tag0dataoutmw[CACHETAGDIRTYBIT];
wire [CACHETAGADDRBITS-1:0] tag0addrbitsmw = tag0dataoutmw[`CACHETAGADDRRNG];

wire                           tag0hitmw = tag0validmw ? (tag0addrbitsmw == reqaddrtagcmpmw) : 1'b0;

reg tag1writemr;
always @ *
begin
    tag1writemr = 1'b0;

    
    if (stateq == STATERESET)
        tag1writemr = 1'b1;
    
    else if (stateq == STATEFLUSH)
        tag1writemr = !tagdirtyanymw;
    
    else if (stateq == STATELOOKUP && (|memwrmq))
        tag1writemr = tag1hitmw;
    
    else if (stateq == STATEWRITE)
        tag1writemr = (replacewayq == 1);
    
    else if (stateq == STATEEVICTWAIT && pmemackw)
        tag1writemr = (replacewayq == 1);
    
    else if (stateq == STATEREFILL)
        tag1writemr = pmemackw && pmemlastw && (replacewayq == 1);
    
    else if (stateq == STATEINVALIDATE)
        tag1writemr = tag1hitmw;
end

wire [CACHETAGDATAW-1:0] tag1dataoutmw;

dcachecoretagram
utag1
(
  .clk0i(clki),
  .rst0i(rsti),
  .clk1i(clki),
  .rst1i(rsti),

  
  .addr0i(tagaddrxr),
  .data0o(tag1dataoutmw),

  
  .addr1i(tagaddrmr),
  .data1i(tagdatainmr),
  .wr1i(tag1writemr)
);

wire                           tag1validmw     = tag1dataoutmw[CACHETAGVALIDBIT];
wire                           tag1dirtymw     = tag1dataoutmw[CACHETAGDIRTYBIT];
wire [CACHETAGADDRBITS-1:0] tag1addrbitsmw = tag1dataoutmw[`CACHETAGADDRRNG];

wire                           tag1hitmw = tag1validmw ? (tag1addrbitsmw == reqaddrtagcmpmw) : 1'b0;


wire taghitanymw = 1'b0
                   | tag0hitmw
                   | tag1hitmw
                    ;

assign taghitanddirtymw = 1'b0
                   | (tag0hitmw & tag0dirtymw)
                   | (tag1hitmw & tag1dirtymw)
                    ;

assign tagdirtyanymw = 1'b0
                   | (tag0validmw & tag0dirtymw)
                   | (tag1validmw & tag1dirtymw)
                    ;

localparam EVICTADDRW = 32 - DCACHELINESIZEW;
reg        evictwayr;
reg [31:0] evictdatar;
reg [EVICTADDRW-1:0] evictaddrr;
always @ *
begin
    evictwayr  = 1'b0;
    evictaddrr = flushingq ? {tag0addrbitsmw, flushaddrq} :
                                {tag0addrbitsmw, memaddrmq[`DCACHETAGREQRNG]};
    evictdatar = data0dataoutmw;

    case (replacewayq)
        1'd0:
        begin
            evictwayr  = tag0validmw && tag0dirtymw;
            evictaddrr = flushingq ? {tag0addrbitsmw, flushaddrq} :
                                        {tag0addrbitsmw, memaddrmq[`DCACHETAGREQRNG]};
            evictdatar = data0dataoutmw;
        end
        1'd1:
        begin
            evictwayr  = tag1validmw && tag1dirtymw;
            evictaddrr = flushingq ? {tag1addrbitsmw, flushaddrq} :
                                        {tag1addrbitsmw, memaddrmq[`DCACHETAGREQRNG]};
            evictdatar = data1dataoutmw;
        end
    endcase
end
assign                  evictwayw  = (flushingq || !taghitanymw) && evictwayr;
wire [EVICTADDRW-1:0] evictaddrw = evictaddrr;
wire [31:0]             evictdataw = evictdatar;

localparam CACHEDATAADDRW = DCACHELINEADDRW+DCACHELINESIZEW-2;


reg [CACHEDATAADDRW-1:0] dataaddrxr;
reg [CACHEDATAADDRW-1:0] dataaddrmr;
reg [CACHEDATAADDRW-1:0] datawriteaddrq;

always @ (posedge clki or posedge rsti)
if (rsti)
    datawriteaddrq <= {(CACHEDATAADDRW){1'b0}};
else if (stateq != STATEREFILL && nextstater == STATEREFILL)
    datawriteaddrq <= pmemaddrw[CACHEDATAADDRW+2-1:2];
else if (stateq != STATEEVICT && nextstater == STATEEVICT)
    datawriteaddrq <= dataaddrmr + 1;
else if (stateq == STATEREFILL && pmemackw)
    datawriteaddrq <= datawriteaddrq + 1;
else if (stateq == STATEEVICT && pmemacceptw)
    datawriteaddrq <= datawriteaddrq + 1;

always @ *
begin
    dataaddrxr = memaddri[CACHEDATAADDRW+2-1:2];
    dataaddrmr = memaddrmq[CACHEDATAADDRW+2-1:2];

    
    if (stateq == STATEREFILL || stateq == STATEEVICT)
    begin
        dataaddrxr = datawriteaddrq;
        dataaddrmr = dataaddrxr;
    end
    else if (stateq == STATEFLUSH || stateq == STATERESET)
    begin
        dataaddrxr = {flushaddrq, {(DCACHELINESIZEW-2){1'b0}}};
        dataaddrmr = dataaddrxr;
    end
    else if (stateq != STATEEVICT && nextstater == STATEEVICT)
    begin
        dataaddrxr = {memaddrmq[`DCACHETAGREQRNG], {(DCACHELINESIZEW-2){1'b0}}};
        dataaddrmr = dataaddrxr;
    end
    
    else if (stateq == STATEREAD)
    begin
        dataaddrxr = memaddrmq[CACHEDATAADDRW+2-1:2];
    end
    
    else
        dataaddrmr = memaddrmq[CACHEDATAADDRW+2-1:2];
end


reg [3:0] data0writemr;
always @ *
begin
    data0writemr = 4'b0;

    if (stateq == STATEREFILL)
        data0writemr = (pmemackw && replacewayq == 0) ? 4'b1111 : 4'b0000;
    else if (stateq == STATEWRITE || stateq == STATELOOKUP)
        data0writemr = memwrmq & {4{tag0hitmw}};
end

wire [31:0] data0dataoutmw;
wire [31:0] data0datainmw = (stateq == STATEREFILL) ? pmemreaddataw : memdatamq;

dcachecoredataram
udata0
(
  .clk0i(clki),
  .rst0i(rsti),
  .clk1i(clki),
  .rst1i(rsti),

  
  .addr0i(dataaddrxr),
  .data0i(32'b0),
  .wr0i(4'b0),
  .data0o(data0dataoutmw),

  
  .addr1i(dataaddrmr),
  .data1i(data0datainmw),
  .wr1i(data0writemr),
  .data1o()
);


reg [3:0] data1writemr;
always @ *
begin
    data1writemr = 4'b0;

    if (stateq == STATEREFILL)
        data1writemr = (pmemackw && replacewayq == 1) ? 4'b1111 : 4'b0000;
    else if (stateq == STATEWRITE || stateq == STATELOOKUP)
        data1writemr = memwrmq & {4{tag1hitmw}};
end

wire [31:0] data1dataoutmw;
wire [31:0] data1datainmw = (stateq == STATEREFILL) ? pmemreaddataw : memdatamq;

dcachecoredataram
udata1
(
  .clk0i(clki),
  .rst0i(rsti),
  .clk1i(clki),
  .rst1i(rsti),

  
  .addr0i(dataaddrxr),
  .data0i(32'b0),
  .wr0i(4'b0),
  .data0o(data1dataoutmw),

  
  .addr1i(dataaddrmr),
  .data1i(data1datainmw),
  .wr1i(data1writemr),
  .data1o()
);


reg [DCACHETAGREQLINEW-1:0] flushaddrq;

always @ (posedge clki or posedge rsti)
if (rsti)
    flushaddrq <= {(DCACHETAGREQLINEW){1'b0}};
else if ((stateq == STATERESET) || (stateq == STATEFLUSH && nextstater == STATEFLUSHADDR))
    flushaddrq <= flushaddrq + 1;
else if (stateq == STATELOOKUP)
    flushaddrq <= {(DCACHETAGREQLINEW){1'b0}};

always @ (posedge clki or posedge rsti)
if (rsti)
    flushingq <= 1'b0;
else if (stateq == STATELOOKUP && nextstater == STATEFLUSHADDR)
    flushingq <= 1'b1;
else if (stateq == STATEFLUSH && nextstater == STATELOOKUP)
    flushingq <= 1'b0;

reg flushlastq;
always @ (posedge clki or posedge rsti)
if (rsti)
    flushlastq <= 1'b0;
else if (stateq == STATELOOKUP)
    flushlastq <= 1'b0;
else if (flushaddrq == {(DCACHETAGREQLINEW){1'b1}})
    flushlastq <= 1'b1;

always @ (posedge clki or posedge rsti)
if (rsti)
    replacewayq <= 0;
else if (stateq == STATEWRITE || stateq == STATEREAD)
    replacewayq <= replacewayq + 1;
else if (flushingq && tagdirtyanymw && !evictwayw && stateq != STATEFLUSHADDR)
    replacewayq <= replacewayq + 1;
else if (stateq == STATEEVICTWAIT && nextstater == STATEFLUSHADDR)
    replacewayq <= 0;
else if (stateq == STATEFLUSH && nextstater == STATELOOKUP)
    replacewayq <= 0;
else if (stateq == STATELOOKUP && nextstater == STATEFLUSHADDR)
    replacewayq <= 0;
else if (stateq == STATEWRITEBACK)
begin
    case (1'b1)
    tag0hitmw: replacewayq <= 0;
    tag1hitmw: replacewayq <= 1;
    endcase
end

reg [31:0] datar;
always @ *
begin
    datar = data0dataoutmw;

    case (1'b1)
    tag0hitmw: datar = data0dataoutmw;
    tag1hitmw: datar = data1dataoutmw;
    endcase
end

assign memdatardo  = datar;

always @ *
begin
    nextstater = stateq;

    case (stateq)
    
    
    
    STATERESET :
    begin
        
        if (flushlastq)
            nextstater = STATELOOKUP;
    end
    
    
    
    STATEFLUSHADDR : nextstater = STATEFLUSH;
    
    
    
    STATEFLUSH :
    begin
        
        if (tagdirtyanymw)
        begin
            
            if (evictwayw)
                nextstater = STATEEVICT;
        end
        
        else if (flushlastq)
            nextstater = STATELOOKUP;
        else
            nextstater = STATEFLUSHADDR;
    end
    
    
    
    STATELOOKUP :
    begin
        
        if ((memrdmq || (memwrmq != 4'b0)) && !taghitanymw)
        begin
            
            if (evictwayw)
                nextstater = STATEEVICT;
            
            else
                nextstater = STATEREFILL;
        end
        
        else if (memwritebacki && memaccepto)
            nextstater = STATEWRITEBACK;
        
        else if (memflushi && memaccepto)
            nextstater = STATEFLUSHADDR;
        
        else if (meminvalidatei && memaccepto)
            nextstater = STATEINVALIDATE;
    end
    
    
    
    STATEREFILL :
    begin
        
        if (pmemackw && pmemlastw)
        begin
            
            if (memwrmq != 4'b0)
                nextstater = STATEWRITE;
            
            else
                nextstater = STATEREAD;
        end
    end
    
    
    
    STATEWRITE, STATEREAD :
    begin
        nextstater = STATELOOKUP;
    end
    
    
    
    STATEEVICT :
    begin
        
        if (pmemacceptw && pmemlastw)
            nextstater = STATEEVICTWAIT;
    end
    
    
    
    STATEEVICTWAIT :
    begin
        
        if (pmemackw && memwritebackmq)
            nextstater = STATELOOKUP;
        
        else if (pmemackw && flushingq)
            nextstater = STATEFLUSHADDR;
        
        else if (pmemackw)
            nextstater = STATEREFILL;
    end
    
    
    
    STATEWRITEBACK:
    begin
        
        if (taghitanddirtymw)
            nextstater = STATEEVICT;
        
        else
            nextstater = STATELOOKUP;
    end
    
    
    
    STATEINVALIDATE:
    begin
        nextstater = STATELOOKUP;
    end
    default:
        ;
   endcase
end

always @ (posedge clki or posedge rsti)
if (rsti)
    stateq   <= STATERESET;
else
    stateq   <= nextstater;

reg memackr;

always @ *
begin
    memackr = 1'b0;

    if (stateq == STATELOOKUP)
    begin
        
        if ((memrdmq || (memwrmq != 4'b0)) && taghitanymw)
            memackr = 1'b1;
        
        else if (memflushmq || meminvalmq || memwritebackmq)
            memackr = 1'b1;
    end
end

assign memacko = memackr;

reg pmemrdq;
reg pmemwr0q;

always @ (posedge clki or posedge rsti)
if (rsti)
    pmemrdq   <= 1'b0;
else if (pmemrdw)
    pmemrdq   <= ~pmemacceptw;

always @ (posedge clki or posedge rsti)
if (rsti)
    pmemwr0q   <= 1'b0;
else if (stateq != STATEEVICT && nextstater == STATEEVICT)
    pmemwr0q   <= 1'b1;
else if (pmemacceptw)
    pmemwr0q   <= 1'b0;

reg [7:0] pmemlenq;
always @ (posedge clki or posedge rsti)
if (rsti)
    pmemlenq   <= 8'b0;
else if (stateq != STATEEVICT && nextstater == STATEEVICT)
    pmemlenq   <= 8'd7;
else if (pmemrdw && pmemacceptw)
    pmemlenq   <= pmemlenw;
else if (stateq == STATEREFILL && pmemackw)
    pmemlenq   <= pmemlenq - 8'd1;
else if (stateq == STATEEVICT && pmemacceptw)
    pmemlenq   <= pmemlenq - 8'd1;

assign pmemlastw = (pmemlenq == 8'd0);

reg [31:0] pmemaddrq;

always @ (posedge clki or posedge rsti)
if (rsti)
    pmemaddrq   <= 32'b0;
else if (|pmemlenw && pmemacceptw)
    pmemaddrq   <= pmemaddrw + 32'd4;
else if (pmemacceptw)
    pmemaddrq   <= pmemaddrq + 32'd4;

reg [3:0]  pmemwrq;
reg [31:0] pmemwritedataq;

always @ (posedge clki or posedge rsti)
if (rsti)
    pmemwrq <= 4'b0;
else if ((|pmemwrw) && !pmemacceptw)
    pmemwrq <= pmemwrw;
else if (pmemacceptw)
    pmemwrq <= 4'b0;

always @ (posedge clki or posedge rsti)
if (rsti)
    pmemwritedataq <= 32'b0;
else if (!pmemacceptw)
    pmemwritedataq <= pmemwritedataw;

reg errorq;
always @ (posedge clki or posedge rsti)
if (rsti)
    errorq   <= 1'b0;
else if (pmemackw && pmemerrorw)
    errorq   <= 1'b1;
else if (memacko)
    errorq   <= 1'b0;

assign memerroro = errorq;

wire refillrequestw   = (stateq != STATEREFILL && nextstater == STATEREFILL);
wire evictrequestw    = (stateq == STATEEVICT) && (evictwayw || memwritebackmq);

assign pmemrdw         = (refillrequestw || pmemrdq);
assign pmemwrw         = (evictrequestw || (|pmemwrq)) ? 4'hF : 4'b0;
assign pmemaddrw       = (|pmemlenw) ? 
                           pmemrdw ? {memaddrmq[31:DCACHELINESIZEW], {(DCACHELINESIZEW){1'b0}}} :
                           {evictaddrw, {(DCACHELINESIZEW){1'b0}}} :
                           pmemaddrq;

assign pmemlenw        = (refillrequestw || pmemrdq || (stateq == STATEEVICT && pmemwr0q)) ? 8'd7 : 8'd0;
assign pmemwritedataw = (|pmemwrq) ? pmemwritedataq : evictdataw;

assign outportwro         = pmemwrw;
assign outportrdo         = pmemrdw;
assign outportleno        = pmemlenw;
assign outportaddro       = pmemaddrw;
assign outportwritedatao = pmemwritedataw;

assign pmemacceptw        = outportaccepti;
assign pmemackw           = outportacki;
assign pmemerrorw         = outporterrori;
assign pmemreaddataw     = outportreaddatai;

`ifdef verilator
/* verilator lintoff WIDTH */
reg [79:0] dbgstate;
always @ *
begin
    dbgstate = "-";

    case (stateq)
    STATERESET:
        dbgstate = "RESET";
    STATEFLUSHADDR:
        dbgstate = "FLUSHADDR";
    STATEFLUSH:
        dbgstate = "FLUSH";
    STATELOOKUP:
        dbgstate = "LOOKUP";
    STATEREAD:
        dbgstate = "READ";
    STATEWRITE:
        dbgstate = "WRITE";
    STATEREFILL:
        dbgstate = "REFILL";
    STATEEVICT:
        dbgstate = "EVICT";
    STATEEVICTWAIT:
        dbgstate = "EVICTWAIT";
    STATEINVALIDATE:
        dbgstate = "INVAL";
    STATEWRITEBACK:
        dbgstate = "WRITEBACK";
    default:
        ;
    endcase
end
/* verilator linton WIDTH */
`endif


endmodule

module dcachecoredataram
(
    
     input           clk0i
    ,input           rst0i
    ,input  [ 10:0]  addr0i
    ,input  [ 31:0]  data0i
    ,input  [  3:0]  wr0i
    ,input           clk1i
    ,input           rst1i
    ,input  [ 10:0]  addr1i
    ,input  [ 31:0]  data1i
    ,input  [  3:0]  wr1i

    
    ,output [ 31:0]  data0o
    ,output [ 31:0]  data1o
);



/* verilator lintoff MULTIDRIVEN */
reg [31:0]   ram [2047:0] /*verilator public*/;
/* verilator linton MULTIDRIVEN */

reg [31:0] ramread0q;
reg [31:0] ramread1q;


always @ (posedge clk0i)
begin
    if (wr0i[0])
        ram[addr0i][7:0] <= data0i[7:0];
    if (wr0i[1])
        ram[addr0i][15:8] <= data0i[15:8];
    if (wr0i[2])
        ram[addr0i][23:16] <= data0i[23:16];
    if (wr0i[3])
        ram[addr0i][31:24] <= data0i[31:24];

    ramread0q <= ram[addr0i];
end

always @ (posedge clk1i)
begin
    if (wr1i[0])
        ram[addr1i][7:0] <= data1i[7:0];
    if (wr1i[1])
        ram[addr1i][15:8] <= data1i[15:8];
    if (wr1i[2])
        ram[addr1i][23:16] <= data1i[23:16];
    if (wr1i[3])
        ram[addr1i][31:24] <= data1i[31:24];

    ramread1q <= ram[addr1i];
end

assign data0o = ramread0q;
assign data1o = ramread1q;



endmodule

module dcachecoretagram
(
    
     input           clk0i
    ,input           rst0i
    ,input  [  7:0]  addr0i
    ,input           clk1i
    ,input           rst1i
    ,input  [  7:0]  addr1i
    ,input  [ 20:0]  data1i
    ,input           wr1i

    
    ,output [ 20:0]  data0o
);



/* verilator lintoff MULTIDRIVEN */
reg [20:0]   ram [255:0] /*verilator public*/;
/* verilator linton MULTIDRIVEN */

reg [20:0] ramread0q;

always @ (posedge clk1i)
begin
    if (wr1i)
        ram[addr1i] = data1i;

    ramread0q = ram[addr0i];
end

assign data0o = ramread0q;


endmodule

module dcacheifpmem
(
    
     input           clki
    ,input           rsti
    ,input  [ 31:0]  memaddri
    ,input  [ 31:0]  memdatawri
    ,input           memrdi
    ,input  [  3:0]  memwri
    ,input           memcacheablei
    ,input  [ 10:0]  memreqtagi
    ,input           meminvalidatei
    ,input           memwritebacki
    ,input           memflushi
    ,input           outportaccepti
    ,input           outportacki
    ,input           outporterrori
    ,input  [ 31:0]  outportreaddatai

    
    ,output [ 31:0]  memdatardo
    ,output          memaccepto
    ,output          memacko
    ,output          memerroro
    ,output [ 10:0]  memresptago
    ,output [  3:0]  outportwro
    ,output          outportrdo
    ,output [  7:0]  outportleno
    ,output [ 31:0]  outportaddro
    ,output [ 31:0]  outportwritedatao
);






wire          resacceptw;
wire          reqacceptw;

wire          requestcompletew;

wire          reqpopw   = requestcompletew;
wire          reqvalidw;
wire [70-1:0] reqw;

wire          dropreqw   = meminvalidatei || memwritebacki || memflushi;
wire          requestw    = dropreqw || memrdi || memwri != 4'b0;

wire          reqpushw   = requestw && resacceptw;

dcacheifpmemfifo
#( 
    .WIDTH(32+32+4+1+1),
    .DEPTH(2),
    .ADDRW(1)
)
ureq
(
    .clki(clki),
    .rsti(rsti),

    
    .dataini({dropreqw, memrdi, memwri, memdatawri, memaddri}),
    .pushi(reqpushw),
    .accepto(reqacceptw),

    
    .valido(reqvalidw),
    .dataouto(reqw),
    .popi(reqpopw)
);

assign memaccepto = reqacceptw & resacceptw;

wire respushw = requestw && reqacceptw;

dcacheifpmemfifo
#( 
    .WIDTH(11),
    .DEPTH(2),
    .ADDRW(1)
)
uresp
(
    .clki(clki),
    .rsti(rsti),

    
    .dataini(memreqtagi),
    .pushi(respushw),
    .accepto(resacceptw),

    
    .valido(), 
    .dataouto(memresptago),
    .popi(memacko)
);

reg  requestpendingq;
wire requestinprogressw  = requestpendingq & !memacko;

wire reqisreadw          = ((reqvalidw & !requestinprogressw) ? reqw[68] : 1'b0);
wire reqiswritew         = ((reqvalidw & !requestinprogressw) ? ~reqw[68] : 1'b0);
wire reqisdropw          = ((reqvalidw & !requestinprogressw) ? reqw[69] : 1'b0);

assign outportwro         = reqiswritew ? reqw[67:64] : 4'b0;
assign outportrdo         = reqisreadw;
assign outportleno        = 8'd0;
assign outportaddro       = {reqw[31:2], 2'b0};
assign outportwritedatao = reqw[63:32];

assign requestcompletew   = reqisdropw || ((outportrdo || outportwro != 4'b0) && outportaccepti);

always @ (posedge clki or posedge rsti)
if (rsti)
    requestpendingq <= 1'b0;
else if (requestcompletew)
    requestpendingq <= 1'b1;
else if (memacko)
    requestpendingq <= 1'b0;

reg droppedq;

always @ (posedge clki or posedge rsti)
if (rsti)
    droppedq <= 1'b0;
else if (reqisdropw)
    droppedq <= 1'b1;
else
    droppedq <= 1'b0;

assign memacko     = droppedq || outportacki;
assign memdatardo = outportreaddatai;
assign memerroro   = outporterrori;


endmodule

module dcacheifpmemfifo
#(
    parameter WIDTH   = 8,
    parameter DEPTH   = 4,
    parameter ADDRW  = 2
)
(
    
     input               clki
    ,input               rsti
    ,input  [WIDTH-1:0]  dataini
    ,input               pushi
    ,input               popi

    
    ,output [WIDTH-1:0]  dataouto
    ,output              accepto
    ,output              valido
);

localparam COUNTW = ADDRW + 1;

reg [WIDTH-1:0]   ramq[DEPTH-1:0];
reg [ADDRW-1:0]  rdptrq;
reg [ADDRW-1:0]  wrptrq;
reg [COUNTW-1:0] countq;

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    countq   <= {(COUNTW) {1'b0}};
    rdptrq  <= {(ADDRW) {1'b0}};
    wrptrq  <= {(ADDRW) {1'b0}};
end
else
begin
    
    if (pushi & accepto)
    begin
        ramq[wrptrq] <= dataini;
        wrptrq        <= wrptrq + 1;
    end

    
    if (popi & valido)
        rdptrq      <= rdptrq + 1;

    
    if ((pushi & accepto) & ~(popi & valido))
        countq <= countq + 1;
    
    else if (~(pushi & accepto) & (popi & valido))
        countq <= countq - 1;
end

/* verilator lintoff WIDTH */
assign valido       = (countq != 0);
assign accepto      = (countq != DEPTH);
/* verilator linton WIDTH */

assign dataouto    = ramq[rdptrq];



endmodule

module dcachemux
(
    
     input           clki
    ,input           rsti
    ,input  [ 31:0]  memaddri
    ,input  [ 31:0]  memdatawri
    ,input           memrdi
    ,input  [  3:0]  memwri
    ,input           memcacheablei
    ,input  [ 10:0]  memreqtagi
    ,input           meminvalidatei
    ,input           memwritebacki
    ,input           memflushi
    ,input  [ 31:0]  memcacheddatardi
    ,input           memcachedaccepti
    ,input           memcachedacki
    ,input           memcachederrori
    ,input  [ 10:0]  memcachedresptagi
    ,input  [ 31:0]  memuncacheddatardi
    ,input           memuncachedaccepti
    ,input           memuncachedacki
    ,input           memuncachederrori
    ,input  [ 10:0]  memuncachedresptagi

    
    ,output [ 31:0]  memdatardo
    ,output          memaccepto
    ,output          memacko
    ,output          memerroro
    ,output [ 10:0]  memresptago
    ,output [ 31:0]  memcachedaddro
    ,output [ 31:0]  memcacheddatawro
    ,output          memcachedrdo
    ,output [  3:0]  memcachedwro
    ,output          memcachedcacheableo
    ,output [ 10:0]  memcachedreqtago
    ,output          memcachedinvalidateo
    ,output          memcachedwritebacko
    ,output          memcachedflusho
    ,output [ 31:0]  memuncachedaddro
    ,output [ 31:0]  memuncacheddatawro
    ,output          memuncachedrdo
    ,output [  3:0]  memuncachedwro
    ,output          memuncachedcacheableo
    ,output [ 10:0]  memuncachedreqtago
    ,output          memuncachedinvalidateo
    ,output          memuncachedwritebacko
    ,output          memuncachedflusho
    ,output          cacheactiveo
);



wire holdw;
reg  cacheaccessq;

assign memcachedaddro         = memaddri;
assign memcacheddatawro      = memdatawri;
assign memcachedrdo           = (memcacheablei & ~holdw) ? memrdi : 1'b0;
assign memcachedwro           = (memcacheablei & ~holdw) ? memwri : 4'b0;
assign memcachedcacheableo    = memcacheablei;
assign memcachedreqtago      = memreqtagi;
assign memcachedinvalidateo   = (memcacheablei & ~holdw) ? meminvalidatei : 1'b0;
assign memcachedwritebacko    = (memcacheablei & ~holdw) ? memwritebacki : 1'b0;
assign memcachedflusho        = (memcacheablei & ~holdw) ? memflushi : 1'b0;

assign memuncachedaddro       = memaddri;
assign memuncacheddatawro    = memdatawri;
assign memuncachedrdo         = (~memcacheablei & ~holdw) ? memrdi : 1'b0;
assign memuncachedwro         = (~memcacheablei & ~holdw) ? memwri : 4'b0;
assign memuncachedcacheableo  = memcacheablei;
assign memuncachedreqtago    = memreqtagi;
assign memuncachedinvalidateo = (~memcacheablei & ~holdw) ? meminvalidatei : 1'b0;
assign memuncachedwritebacko  = (~memcacheablei & ~holdw) ? memwritebacki : 1'b0;
assign memuncachedflusho      = (~memcacheablei & ~holdw) ? memflushi : 1'b0;

assign memaccepto              =(memcacheablei ? memcachedaccepti  : memuncachedaccepti) & !holdw;
assign memdatardo             = cacheaccessq ? memcacheddatardi  : memuncacheddatardi;
assign memacko                 = cacheaccessq ? memcachedacki      : memuncachedacki;
assign memerroro               = cacheaccessq ? memcachederrori    : memuncachederrori;
assign memresptago            = cacheaccessq ? memcachedresptagi : memuncachedresptagi;

wire      requestw              = memrdi | memwri != 4'b0 | memflushi | meminvalidatei | memwritebacki;

reg [4:0] pendingr;
reg [4:0] pendingq;
always @ *
begin
    pendingr = pendingq;

    if ((requestw && memaccepto) && !memacko)
        pendingr = pendingr + 5'd1;
    else if (!(requestw && memaccepto) && memacko)
        pendingr = pendingr - 5'd1;
end

always @ (posedge clki or posedge rsti)
if (rsti)
    pendingq <= 5'b0;
else
    pendingq <= pendingr;

always @ (posedge clki or posedge rsti)
if (rsti)
    cacheaccessq <= 1'b0;
else if (requestw && memaccepto)
    cacheaccessq <= memcacheablei;

assign holdw = (|pendingq) && (cacheaccessq != memcacheablei);

assign cacheactiveo = (|pendingq) ? cacheaccessq : memcacheablei;


endmodule

module dcachepmemmux
(
    
     input           clki
    ,input           rsti
    ,input           outportaccepti
    ,input           outportacki
    ,input           outporterrori
    ,input  [ 31:0]  outportreaddatai
    ,input           selecti
    ,input  [  3:0]  inport0wri
    ,input           inport0rdi
    ,input  [  7:0]  inport0leni
    ,input  [ 31:0]  inport0addri
    ,input  [ 31:0]  inport0writedatai
    ,input  [  3:0]  inport1wri
    ,input           inport1rdi
    ,input  [  7:0]  inport1leni
    ,input  [ 31:0]  inport1addri
    ,input  [ 31:0]  inport1writedatai

    
    ,output [  3:0]  outportwro
    ,output          outportrdo
    ,output [  7:0]  outportleno
    ,output [ 31:0]  outportaddro
    ,output [ 31:0]  outportwritedatao
    ,output          inport0accepto
    ,output          inport0acko
    ,output          inport0erroro
    ,output [ 31:0]  inport0readdatao
    ,output          inport1accepto
    ,output          inport1acko
    ,output          inport1erroro
    ,output [ 31:0]  inport1readdatao
);




reg [  3:0]  outportwrr;
reg          outportrdr;
reg [  7:0]  outportlenr;
reg [ 31:0]  outportaddrr;
reg [ 31:0]  outportwritedatar;
reg          selectq;

always @ *
begin
    case (selecti)
    1'd1:
    begin
        outportwrr          = inport1wri;
        outportrdr          = inport1rdi;
        outportlenr         = inport1leni;
        outportaddrr        = inport1addri;
        outportwritedatar  = inport1writedatai;
    end
    default:
    begin
        outportwrr          = inport0wri;
        outportrdr          = inport0rdi;
        outportlenr         = inport0leni;
        outportaddrr        = inport0addri;
        outportwritedatar  = inport0writedatai;
    end
    endcase
end

assign outportwro         = outportwrr;
assign outportrdo         = outportrdr;
assign outportleno        = outportlenr;
assign outportaddro       = outportaddrr;
assign outportwritedatao = outportwritedatar;

always @ (posedge clki or posedge rsti)
if (rsti)
    selectq <= 1'b0;
else
    selectq <= selecti;

assign inport0acko       = (selectq == 1'd0) && outportacki;
assign inport0erroro     = (selectq == 1'd0) && outporterrori;
assign inport0readdatao = outportreaddatai;
assign inport0accepto    = (selecti == 1'd0) && outportaccepti;
assign inport1acko       = (selectq == 1'd1) && outportacki;
assign inport1erroro     = (selectq == 1'd1) && outporterrori;
assign inport1readdatao = outportreaddatai;
assign inport1accepto    = (selecti == 1'd1) && outportaccepti;


endmodule

module dportaxi
(
    
     input           clki
    ,input           rsti
    ,input  [ 31:0]  memaddri
    ,input  [ 31:0]  memdatawri
    ,input           memrdi
    ,input  [  3:0]  memwri
    ,input           memcacheablei
    ,input  [ 10:0]  memreqtagi
    ,input           meminvalidatei
    ,input           memwritebacki
    ,input           memflushi
    ,input           axiawreadyi
    ,input           axiwreadyi
    ,input           axibvalidi
    ,input  [  1:0]  axibrespi
    ,input           axiarreadyi
    ,input           axirvalidi
    ,input  [ 31:0]  axirdatai
    ,input  [  1:0]  axirrespi

    
    ,output [ 31:0]  memdatardo
    ,output          memaccepto
    ,output          memacko
    ,output          memerroro
    ,output [ 10:0]  memresptago
    ,output          axiawvalido
    ,output [ 31:0]  axiawaddro
    ,output          axiwvalido
    ,output [ 31:0]  axiwdatao
    ,output [  3:0]  axiwstrbo
    ,output          axibreadyo
    ,output          axiarvalido
    ,output [ 31:0]  axiaraddro
    ,output          axirreadyo
);






wire          resacceptw;
wire          reqacceptw;

wire          writecompletew;
wire          readcompletew;

reg           requestpendingq;

wire          reqpopw   = readcompletew | writecompletew;
wire          reqvalidw;
wire [69-1:0] reqw;

wire          reqpushw   = (memrdi || memwri != 4'b0) && resacceptw;

dportaxififo
#( 
    .WIDTH(32+32+4+1),
    .DEPTH(2),
    .ADDRW(1)
)
ureq
(
    .clki(clki),
    .rsti(rsti),

    
    .dataini({memrdi, memwri, memdatawri, memaddri}),
    .pushi(reqpushw),
    .accepto(reqacceptw),

    
    .valido(reqvalidw),
    .dataouto(reqw),
    .popi(reqpopw)
);

assign memaccepto = reqacceptw & resacceptw;

wire respushw = (memrdi || memwri != 4'b0) && reqacceptw;

dportaxififo
#( 
    .WIDTH(11),
    .DEPTH(2),
    .ADDRW(1)
)
uresp
(
    .clki(clki),
    .rsti(rsti),

    
    .dataini(memreqtagi),
    .pushi(respushw),
    .accepto(resacceptw),

    
    .valido(), 
    .dataouto(memresptago),
    .popi(memacko)
);

assign memacko   = axibvalidi || axirvalidi;
assign memerroro = axibvalidi ? (axibrespi != 2'b0) : (axirrespi != 2'b0);

wire requestinprogressw = requestpendingq & !memacko;

wire reqisreadw  = ((reqvalidw & !requestinprogressw) ? reqw[68] : 1'b0);
wire reqiswritew = ((reqvalidw & !requestinprogressw) ? ~reqw[68] : 1'b0);

reg awvalidinhibitq;
reg wvalidinhibitq;

always @ (posedge clki or posedge rsti)
if (rsti)
    awvalidinhibitq <= 1'b0;
else if (axiawvalido && axiawreadyi && axiwvalido && !axiwreadyi)
    awvalidinhibitq <= 1'b1;
else if (axiwvalido && axiwreadyi)
    awvalidinhibitq <= 1'b0;

always @ (posedge clki or posedge rsti)
if (rsti)
    wvalidinhibitq <= 1'b0;
else if (axiwvalido && axiwreadyi && axiawvalido && !axiawreadyi)
    wvalidinhibitq <= 1'b1;
else if (axiawvalido && axiawreadyi)
    wvalidinhibitq <= 1'b0;

assign axiawvalido = reqiswritew && !awvalidinhibitq;
assign axiawaddro  = {reqw[31:2], 2'b0};
assign axiwvalido  = reqiswritew && !wvalidinhibitq;
assign axiwdatao   = reqw[63:32];
assign axiwstrbo   = reqw[67:64];

assign axibreadyo  = 1'b1;

assign writecompletew = (awvalidinhibitq || axiawreadyi) &&
                          (wvalidinhibitq || axiwreadyi) && reqiswritew;

assign axiarvalido = reqisreadw;
assign axiaraddro  = {reqw[31:2], 2'b0};

assign axirreadyo  = 1'b1;

assign memdatardo = axirdatai;

assign readcompletew = axiarvalido && axiarreadyi;

always @ (posedge clki or posedge rsti)
if (rsti)
    requestpendingq <= 1'b0;
else if (writecompletew || readcompletew)
    requestpendingq <= 1'b1;
else if (memacko)
    requestpendingq <= 1'b0;

endmodule

module dportaxififo
#(
    parameter WIDTH   = 8,
    parameter DEPTH   = 2,
    parameter ADDRW  = 1
)
(
    
     input               clki
    ,input               rsti
    ,input  [WIDTH-1:0]  dataini
    ,input               pushi
    ,input               popi

    
    ,output [WIDTH-1:0]  dataouto
    ,output              accepto
    ,output              valido
);

localparam COUNTW = ADDRW + 1;

reg [WIDTH-1:0]   ramq[DEPTH-1:0];
reg [ADDRW-1:0]  rdptrq;
reg [ADDRW-1:0]  wrptrq;
reg [COUNTW-1:0] countq;

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    countq   <= {(COUNTW) {1'b0}};
    rdptrq  <= {(ADDRW) {1'b0}};
    wrptrq  <= {(ADDRW) {1'b0}};
end
else
begin
    
    if (pushi & accepto)
    begin
        ramq[wrptrq] <= dataini;
        wrptrq        <= wrptrq + 1;
    end

    
    if (popi & valido)
        rdptrq      <= rdptrq + 1;

    
    if ((pushi & accepto) & ~(popi & valido))
        countq <= countq + 1;
    
    else if (~(pushi & accepto) & (popi & valido))
        countq <= countq - 1;
end

/* verilator lintoff WIDTH */
assign valido       = (countq != 0);
assign accepto      = (countq != DEPTH);
/* verilator linton WIDTH */

assign dataouto    = ramq[rdptrq];



endmodule

module dportmux
#(
     parameter TCMMEMBASE     = 0
)
(
    
     input           clki
    ,input           rsti
    ,input  [ 31:0]  memaddri
    ,input  [ 31:0]  memdatawri
    ,input           memrdi
    ,input  [  3:0]  memwri
    ,input           memcacheablei
    ,input  [ 10:0]  memreqtagi
    ,input           meminvalidatei
    ,input           memwritebacki
    ,input           memflushi
    ,input  [ 31:0]  memtcmdatardi
    ,input           memtcmaccepti
    ,input           memtcmacki
    ,input           memtcmerrori
    ,input  [ 10:0]  memtcmresptagi
    ,input  [ 31:0]  memextdatardi
    ,input           memextaccepti
    ,input           memextacki
    ,input           memexterrori
    ,input  [ 10:0]  memextresptagi

    
    ,output [ 31:0]  memdatardo
    ,output          memaccepto
    ,output          memacko
    ,output          memerroro
    ,output [ 10:0]  memresptago
    ,output [ 31:0]  memtcmaddro
    ,output [ 31:0]  memtcmdatawro
    ,output          memtcmrdo
    ,output [  3:0]  memtcmwro
    ,output          memtcmcacheableo
    ,output [ 10:0]  memtcmreqtago
    ,output          memtcminvalidateo
    ,output          memtcmwritebacko
    ,output          memtcmflusho
    ,output [ 31:0]  memextaddro
    ,output [ 31:0]  memextdatawro
    ,output          memextrdo
    ,output [  3:0]  memextwro
    ,output          memextcacheableo
    ,output [ 10:0]  memextreqtago
    ,output          memextinvalidateo
    ,output          memextwritebacko
    ,output          memextflusho
);



wire holdw;

/* verilator lintoff UNSIGNED */
wire tcmaccessw = (memaddri >= TCMMEMBASE && memaddri < (TCMMEMBASE + 32'd65536));
/* verilator linton UNSIGNED */

reg       tcmaccessq;
reg [4:0] pendingq;

assign memtcmaddro       = memaddri;
assign memtcmdatawro    = memdatawri;
assign memtcmrdo         = (tcmaccessw & ~holdw) ? memrdi : 1'b0;
assign memtcmwro         = (tcmaccessw & ~holdw) ? memwri : 4'b0;
assign memtcmcacheableo  = memcacheablei;
assign memtcmreqtago    = memreqtagi;
assign memtcminvalidateo = (tcmaccessw & ~holdw) ? meminvalidatei : 1'b0;
assign memtcmwritebacko  = (tcmaccessw & ~holdw) ? memwritebacki : 1'b0;
assign memtcmflusho      = (tcmaccessw & ~holdw) ? memflushi : 1'b0;

assign memextaddro       = memaddri;
assign memextdatawro    = memdatawri;
assign memextrdo         = (~tcmaccessw & ~holdw) ? memrdi : 1'b0;
assign memextwro         = (~tcmaccessw & ~holdw) ? memwri : 4'b0;
assign memextcacheableo  = memcacheablei;
assign memextreqtago    = memreqtagi;
assign memextinvalidateo = (~tcmaccessw & ~holdw) ? meminvalidatei : 1'b0;
assign memextwritebacko  = (~tcmaccessw & ~holdw) ? memwritebacki : 1'b0;
assign memextflusho      = (~tcmaccessw & ~holdw) ? memflushi : 1'b0;

assign memaccepto         =(tcmaccessw ? memtcmaccepti   : memextaccepti) & !holdw;
assign memdatardo        = tcmaccessq ? memtcmdatardi  : memextdatardi;
assign memacko            = tcmaccessq ? memtcmacki      : memextacki;
assign memerroro          = tcmaccessq ? memtcmerrori    : memexterrori;
assign memresptago       = tcmaccessq ? memtcmresptagi : memextresptagi;

wire   requestw            = memrdi || memwri != 4'b0 || memflushi || meminvalidatei || memwritebacki;

reg [4:0] pendingr;
always @ *
begin
    pendingr = pendingq;

    if ((requestw && memaccepto) && !memacko)
        pendingr = pendingr + 5'd1;
    else if (!(requestw && memaccepto) && memacko)
        pendingr = pendingr - 5'd1;
end

always @ (posedge clki or posedge rsti)
if (rsti)
    pendingq <= 5'b0;
else
    pendingq <= pendingr;

always @ (posedge clki or posedge rsti)
if (rsti)
    tcmaccessq <= 1'b0;
else if (requestw && memaccepto)
    tcmaccessq <= tcmaccessw;

assign holdw = (|pendingq) && (tcmaccessq != tcmaccessw);



endmodule

module icache
#(
     parameter AXIID           = 0
)
(
    
     input           clki
    ,input           rsti
    ,input           reqrdi
    ,input           reqflushi
    ,input           reqinvalidatei
    ,input  [ 31:0]  reqpci
    ,input           axiawreadyi
    ,input           axiwreadyi
    ,input           axibvalidi
    ,input  [  1:0]  axibrespi
    ,input  [  3:0]  axibidi
    ,input           axiarreadyi
    ,input           axirvalidi
    ,input  [ 31:0]  axirdatai
    ,input  [  1:0]  axirrespi
    ,input  [  3:0]  axiridi
    ,input           axirlasti

    
    ,output          reqaccepto
    ,output          reqvalido
    ,output          reqerroro
    ,output [ 31:0]  reqinsto
    ,output          axiawvalido
    ,output [ 31:0]  axiawaddro
    ,output [  3:0]  axiawido
    ,output [  7:0]  axiawleno
    ,output [  1:0]  axiawbursto
    ,output          axiwvalido
    ,output [ 31:0]  axiwdatao
    ,output [  3:0]  axiwstrbo
    ,output          axiwlasto
    ,output          axibreadyo
    ,output          axiarvalido
    ,output [ 31:0]  axiaraddro
    ,output [  3:0]  axiarido
    ,output [  7:0]  axiarleno
    ,output [  1:0]  axiarbursto
    ,output          axirreadyo
);



localparam ICACHENUMWAYS           = 2;

localparam ICACHENUMLINES          = 256;
localparam ICACHELINEADDRW        = 8;

localparam ICACHELINESIZEW        = 5;
localparam ICACHELINESIZE          = 32;
localparam ICACHELINEWORDS         = 8;

localparam ICACHETAGREQLINEL     = 5;  
localparam ICACHETAGREQLINEH     = 12; 
localparam ICACHETAGREQLINEW     = 8;  
`define ICACHETAGREQRNG          ICACHETAGREQLINEH:ICACHETAGREQLINEL

`define CACHETAGADDRRNG          18:0
localparam CACHETAGADDRBITS       = 19;
localparam CACHETAGVALIDBIT       = CACHETAGADDRBITS;
localparam CACHETAGDATAW          = CACHETAGVALIDBIT + 1;

localparam ICACHETAGCMPADDRL     = ICACHETAGREQLINEH + 1;
localparam ICACHETAGCMPADDRH     = 32-1;
localparam ICACHETAGCMPADDRW     = ICACHETAGCMPADDRH - ICACHETAGCMPADDRL + 1;
`define   ICACHETAGCMPADDRRNG   31:13


wire [ICACHETAGREQLINEW-1:0] reqlineaddrw  = reqpci[`ICACHETAGREQRNG];

localparam CACHEDATAADDRW = ICACHELINEADDRW+ICACHELINESIZEW-2;
wire [CACHEDATAADDRW-1:0] reqdataaddrw = reqpci[CACHEDATAADDRW+2-1:2];

localparam STATEW           = 2;
localparam STATEFLUSH       = 2'd0;
localparam STATELOOKUP      = 2'd1;
localparam STATEREFILL      = 2'd2;
localparam STATERELOOKUP    = 2'd3;


reg [STATEW-1:0]           nextstater;
reg [STATEW-1:0]           stateq;

reg                         invalidateq;

reg [0:0]  replacewayq;

reg lookupvalidq;

always @ (posedge clki or posedge rsti)
if (rsti)
    lookupvalidq <= 1'b0;
else if (reqrdi && reqaccepto)
    lookupvalidq <= 1'b1;
else if (reqvalido)
    lookupvalidq <= 1'b0;

reg [31:0] lookupaddrq;

always @ (posedge clki or posedge rsti)
if (rsti)
    lookupaddrq <= 32'b0;
else if (reqrdi && reqaccepto)
    lookupaddrq <= reqpci;

wire [ICACHETAGCMPADDRW-1:0] reqpctagcmpw = lookupaddrq[`ICACHETAGCMPADDRRNG];

reg [ICACHETAGREQLINEW-1:0] tagaddrr;

always @ *
begin
    tagaddrr = flushaddrq;

    
    if (stateq == STATEFLUSH)
        tagaddrr = flushaddrq;
    
    else if (stateq == STATEREFILL || stateq == STATERELOOKUP)
        tagaddrr = lookupaddrq[`ICACHETAGREQRNG];
    
    else
        tagaddrr = reqlineaddrw;
end

reg [CACHETAGDATAW-1:0] tagdatainr;
always @ *
begin
    tagdatainr = {(CACHETAGDATAW){1'b0}};

    
    if (stateq == STATEFLUSH)
        tagdatainr = {(CACHETAGDATAW){1'b0}};
    
    else if (stateq == STATEREFILL)
    begin
        tagdatainr[CACHETAGVALIDBIT] = 1'b1;
        tagdatainr[`CACHETAGADDRRNG] = lookupaddrq[`ICACHETAGCMPADDRRNG];
    end
end

reg tag0writer;
always @ *
begin
    tag0writer = 1'b0;

    
    if (stateq == STATEFLUSH)
        tag0writer = 1'b1;
    
    else if (stateq == STATEREFILL)
        tag0writer = axirvalidi && axirlasti && (replacewayq == 0);
end

wire [CACHETAGDATAW-1:0] tag0dataoutw;

icachetagram
utag0
(
  .clki(clki),
  .rsti(rsti),
  .addri(tagaddrr),
  .datai(tagdatainr),
  .wri(tag0writer),
  .datao(tag0dataoutw)
);

wire                           tag0validw     = tag0dataoutw[CACHETAGVALIDBIT];
wire [CACHETAGADDRBITS-1:0] tag0addrbitsw = tag0dataoutw[`CACHETAGADDRRNG];

wire                           tag0hitw = tag0validw ? (tag0addrbitsw == reqpctagcmpw) : 1'b0;

reg tag1writer;
always @ *
begin
    tag1writer = 1'b0;

    
    if (stateq == STATEFLUSH)
        tag1writer = 1'b1;
    
    else if (stateq == STATEREFILL)
        tag1writer = axirvalidi && axirlasti && (replacewayq == 1);
end

wire [CACHETAGDATAW-1:0] tag1dataoutw;

icachetagram
utag1
(
  .clki(clki),
  .rsti(rsti),
  .addri(tagaddrr),
  .datai(tagdatainr),
  .wri(tag1writer),
  .datao(tag1dataoutw)
);

wire                           tag1validw     = tag1dataoutw[CACHETAGVALIDBIT];
wire [CACHETAGADDRBITS-1:0] tag1addrbitsw = tag1dataoutw[`CACHETAGADDRRNG];

wire                           tag1hitw = tag1validw ? (tag1addrbitsw == reqpctagcmpw) : 1'b0;


wire taghitanyw = 1'b0
                   | tag0hitw
                   | tag1hitw
                    ;

reg [CACHEDATAADDRW-1:0] dataaddrr;
reg [CACHEDATAADDRW-1:0] datawriteaddrq;

always @ (posedge clki or posedge rsti)
if (rsti)
    datawriteaddrq <= {(CACHEDATAADDRW){1'b0}};
else if (stateq == STATELOOKUP && nextstater == STATEREFILL)
    datawriteaddrq <= axiaraddro[CACHEDATAADDRW+2-1:2];
else if (stateq == STATEREFILL && axirvalidi)
    datawriteaddrq <= datawriteaddrq + 1;

always @ *
begin
    dataaddrr = reqdataaddrw;

    
    if (stateq == STATEREFILL)
        dataaddrr = datawriteaddrq;
    
    else if (stateq == STATERELOOKUP)
        dataaddrr = lookupaddrq[CACHEDATAADDRW+2-1:2];
    
    else
        dataaddrr = reqdataaddrw;
end


reg data0writer;
always @ *
begin
    data0writer = axirvalidi && replacewayq == 0;
end

wire [31:0] data0dataoutw;

icachedataram
udata0
(
  .clki(clki),
  .rsti(rsti),
  .addri(dataaddrr),
  .datai(axirdatai),
  .wri(data0writer),
  .datao(data0dataoutw)
);

reg data1writer;
always @ *
begin
    data1writer = axirvalidi && replacewayq == 1;
end

wire [31:0] data1dataoutw;

icachedataram
udata1
(
  .clki(clki),
  .rsti(rsti),
  .addri(dataaddrr),
  .datai(axirdatai),
  .wri(data1writer),
  .datao(data1dataoutw)
);

reg [ICACHETAGREQLINEW-1:0] flushaddrq;

always @ (posedge clki or posedge rsti)
if (rsti)
    flushaddrq <= {(ICACHETAGREQLINEW){1'b0}};
else if (stateq == STATEFLUSH)
    flushaddrq <= flushaddrq + 1;
else if (reqinvalidatei && reqaccepto)
    flushaddrq <= reqlineaddrw;
else
    flushaddrq <= {(ICACHETAGREQLINEW){1'b0}};

always @ (posedge clki or posedge rsti)
if (rsti)
    replacewayq <= 0;
else if (axirvalidi && axirlasti)
    replacewayq <= replacewayq + 1;

assign reqvalido = lookupvalidq && ((stateq == STATELOOKUP) ? taghitanyw : 1'b0);

reg [31:0] instr;
always @ *
begin
    instr = data0dataoutw;

    case (1'b1)
    tag0hitw: instr = data0dataoutw;
    tag1hitw: instr = data1dataoutw;
    endcase
end

assign reqinsto    = instr;

always @ *
begin
    nextstater = stateq;

    case (stateq)
    
    
    
    STATEFLUSH :
    begin
        if (invalidateq)
            nextstater = STATELOOKUP;
        else if (flushaddrq == {(ICACHETAGREQLINEW){1'b1}})
            nextstater = STATELOOKUP;
    end
    
    
    
    STATELOOKUP :
    begin
        
        if (lookupvalidq && !taghitanyw)
            nextstater = STATEREFILL;
        
        else if (reqinvalidatei || reqflushi)
            nextstater = STATEFLUSH;
    end
    
    
    
    STATEREFILL :
    begin
        
        if (axirvalidi && axirlasti)
            nextstater = STATERELOOKUP;
    end
    
    
    
    STATERELOOKUP :
    begin
        nextstater = STATELOOKUP;
    end
    default:
        ;
   endcase
end

always @ (posedge clki or posedge rsti)
if (rsti)
    stateq   <= STATEFLUSH;
else
    stateq   <= nextstater;

assign reqaccepto = (stateq == STATELOOKUP && nextstater != STATEREFILL);

always @ (posedge clki or posedge rsti)
if (rsti)
    invalidateq   <= 1'b0;
else if (reqinvalidatei && reqaccepto)
    invalidateq   <= 1'b1;
else
    invalidateq   <= 1'b0;

reg axiarvalidq;
always @ (posedge clki or posedge rsti)
if (rsti)
    axiarvalidq   <= 1'b0;
else if (axiarvalido && !axiarreadyi)
    axiarvalidq   <= 1'b1;
else
    axiarvalidq   <= 1'b0;

reg axierrorq;
always @ (posedge clki or posedge rsti)
if (rsti)
    axierrorq   <= 1'b0;
else if (axirvalidi && axirreadyo && axirrespi != 2'b0)
    axierrorq   <= 1'b1;
else if (reqvalido)
    axierrorq   <= 1'b0;

assign reqerroro = axierrorq;

assign axiawvalido = 1'b0;
assign axiawaddro  = 32'b0;
assign axiawido    = 4'b0;
assign axiawleno   = 8'b0;
assign axiawbursto = 2'b0;
assign axiwvalido  = 1'b0;
assign axiwdatao   = 32'b0;
assign axiwstrbo   = 4'b0;
assign axiwlasto   = 1'b0;
assign axibreadyo  = 1'b0;

assign axiarvalido = (stateq == STATELOOKUP && nextstater == STATEREFILL) || axiarvalidq;
assign axiaraddro  = {lookupaddrq[31:ICACHELINESIZEW], {(ICACHELINESIZEW){1'b0}}};
assign axiarbursto = 2'd1; 
assign axiarido    = AXIID;
assign axiarleno   = 8'd7;
assign axirreadyo  = 1'b1;



endmodule

module icachedataram
(
    
     input           clki
    ,input           rsti
    ,input  [ 10:0]  addri
    ,input  [ 31:0]  datai
    ,input           wri

    
    ,output [ 31:0]  datao
);




reg [31:0]   ram [2047:0] /*verilator public*/;
reg [31:0]   ramreadq;

always @ (posedge clki)
begin
    if (wri)
        ram[addri] <= datai;
    ramreadq <= ram[addri];
end

assign datao = ramreadq;



endmodule

module icachetagram
(
    
     input           clki
    ,input           rsti
    ,input  [  7:0]  addri
    ,input  [ 19:0]  datai
    ,input           wri

    
    ,output [ 19:0]  datao
);




reg [19:0]   ram [255:0] /*verilator public*/;
reg [19:0]   ramreadq;

always @ (posedge clki)
begin
    if (wri)
        ram[addri] <= datai;
    ramreadq <= ram[addri];
end

assign datao = ramreadq;



endmodule
module riscvalu
(
    
     input  [  3:0]  aluopi
    ,input  [ 31:0]  aluai
    ,input  [ 31:0]  alubi

    
    ,output [ 31:0]  alupo
);

`include "riscvdefs.v"

reg [31:0]      resultr;

reg [31:16]     shiftrightfillr;
reg [31:0]      shiftright1r;
reg [31:0]      shiftright2r;
reg [31:0]      shiftright4r;
reg [31:0]      shiftright8r;

reg [31:0]      shiftleft1r;
reg [31:0]      shiftleft2r;
reg [31:0]      shiftleft4r;
reg [31:0]      shiftleft8r;

wire [31:0]     subresw = aluai - alubi;

always @ (aluopi or aluai or alubi or subresw)
begin
    shiftrightfillr = 16'b0;
    shiftright1r = 32'b0;
    shiftright2r = 32'b0;
    shiftright4r = 32'b0;
    shiftright8r = 32'b0;

    shiftleft1r = 32'b0;
    shiftleft2r = 32'b0;
    shiftleft4r = 32'b0;
    shiftleft8r = 32'b0;

    case (aluopi)
       
       
       
       `ALUSHIFTL :
       begin
            if (alubi[0] == 1'b1)
                shiftleft1r = {aluai[30:0],1'b0};
            else
                shiftleft1r = aluai;

            if (alubi[1] == 1'b1)
                shiftleft2r = {shiftleft1r[29:0],2'b00};
            else
                shiftleft2r = shiftleft1r;

            if (alubi[2] == 1'b1)
                shiftleft4r = {shiftleft2r[27:0],4'b0000};
            else
                shiftleft4r = shiftleft2r;

            if (alubi[3] == 1'b1)
                shiftleft8r = {shiftleft4r[23:0],8'b00000000};
            else
                shiftleft8r = shiftleft4r;

            if (alubi[4] == 1'b1)
                resultr = {shiftleft8r[15:0],16'b0000000000000000};
            else
                resultr = shiftleft8r;
       end
       
       
       
       `ALUSHIFTR, `ALUSHIFTRARITH:
       begin
            
            if (aluai[31] == 1'b1 && aluopi == `ALUSHIFTRARITH)
                shiftrightfillr = 16'b1111111111111111;
            else
                shiftrightfillr = 16'b0000000000000000;

            if (alubi[0] == 1'b1)
                shiftright1r = {shiftrightfillr[31], aluai[31:1]};
            else
                shiftright1r = aluai;

            if (alubi[1] == 1'b1)
                shiftright2r = {shiftrightfillr[31:30], shiftright1r[31:2]};
            else
                shiftright2r = shiftright1r;

            if (alubi[2] == 1'b1)
                shiftright4r = {shiftrightfillr[31:28], shiftright2r[31:4]};
            else
                shiftright4r = shiftright2r;

            if (alubi[3] == 1'b1)
                shiftright8r = {shiftrightfillr[31:24], shiftright4r[31:8]};
            else
                shiftright8r = shiftright4r;

            if (alubi[4] == 1'b1)
                resultr = {shiftrightfillr[31:16], shiftright8r[31:16]};
            else
                resultr = shiftright8r;
       end       
       
       
       
       `ALUADD : 
       begin
            resultr      = (aluai + alubi);
       end
       `ALUSUB : 
       begin
            resultr      = subresw;
       end
       
       
       
       `ALUAND : 
       begin
            resultr      = (aluai & alubi);
       end
       `ALUOR  : 
       begin
            resultr      = (aluai | alubi);
       end
       `ALUXOR : 
       begin
            resultr      = (aluai ^ alubi);
       end
       
       
       
       `ALULESSTHAN : 
       begin
            resultr      = (aluai < alubi) ? 32'h1 : 32'h0;
       end
       `ALULESSTHANSIGNED : 
       begin
            if (aluai[31] != alubi[31])
                resultr  = aluai[31] ? 32'h1 : 32'h0;
            else
                resultr  = subresw[31] ? 32'h1 : 32'h0;            
       end       
       default  : 
       begin
            resultr      = aluai;
       end
    endcase
end

assign alupo    = resultr;

endmodule

module riscvcore
#(
     parameter SUPPORTMULDIV   = 1
    ,parameter SUPPORTSUPER    = 0
    ,parameter SUPPORTMMU      = 0
    ,parameter SUPPORTLOADBYPASS = 1
    ,parameter SUPPORTMULBYPASS = 1
    ,parameter SUPPORTREGFILEXILINX = 0
    ,parameter EXTRADECODESTAGE = 0
    ,parameter MEMCACHEADDRMIN = 32'h80000000
    ,parameter MEMCACHEADDRMAX = 32'h8fffffff
)
(
    
     input           clki
    ,input           rsti
    ,input  [ 31:0]  memddatardi
    ,input           memdaccepti
    ,input           memdacki
    ,input           memderrori
    ,input  [ 10:0]  memdresptagi
    ,input           memiaccepti
    ,input           memivalidi
    ,input           memierrori
    ,input  [ 31:0]  memiinsti
    ,input           intri
    ,input  [ 31:0]  resetvectori
    ,input  [ 31:0]  cpuidi

    
    ,output [ 31:0]  memdaddro
    ,output [ 31:0]  memddatawro
    ,output          memdrdo
    ,output [  3:0]  memdwro
    ,output          memdcacheableo
    ,output [ 10:0]  memdreqtago
    ,output          memdinvalidateo
    ,output          memdwritebacko
    ,output          memdflusho
    ,output          memirdo
    ,output          memiflusho
    ,output          memiinvalidateo
    ,output [ 31:0]  memipco
);

wire           mmulsuwritebackw;
wire  [  1:0]  fetchinprivw;
wire  [  4:0]  mulopcoderdidxw;
wire           mmuflushw;
wire  [ 31:0]  lsuopcodepcw;
wire           fetchacceptw;
wire  [  4:0]  csropcoderdidxw;
wire  [ 31:0]  branchexecsourcew;
wire  [ 31:0]  csropcoderboperandw;
wire  [ 31:0]  writebackdivvaluew;
wire           csropcodevalidw;
wire           branchcsrrequestw;
wire  [ 31:0]  mmuifetchinstw;
wire  [ 31:0]  opcodepcw;
wire  [  4:0]  opcoderbidxw;
wire           mmulsuerrorw;
wire           mulopcodevalidw;
wire           mmumxrw;
wire  [  1:0]  branchdexecprivw;
wire           mmuifetchvalidw;
wire           csropcodeinvalidw;
wire  [  5:0]  csrwritebackexceptionw;
wire           fetchinstrmulw;
wire           branchexecisretw;
wire  [ 31:0]  csrwritebackexceptionaddrw;
wire  [  3:0]  mmulsuwrw;
wire           fetchinfaultw;
wire           branchrequestw;
wire  [ 31:0]  csropcodepcw;
wire           writebackmemvalidw;
wire  [  5:0]  csrresulte1exceptionw;
wire  [ 31:0]  branchcsrpcw;
wire  [ 31:0]  mmulsudatawrw;
wire           fetchfaultpagew;
wire  [ 10:0]  mmulsuresptagw;
wire  [ 10:0]  mmulsureqtagw;
wire  [ 31:0]  opcoderaoperandw;
wire           squashdecodew;
wire           fetchdecfaultpagew;
wire  [ 31:0]  mulopcodeopcodew;
wire           execholdw;
wire           fetchinstrinvalidw;
wire  [ 31:0]  branchpcw;
wire  [  4:0]  mulopcoderaidxw;
wire  [  4:0]  csropcoderbidxw;
wire           lsustallw;
wire           branchexecisnottakenw;
wire  [ 31:0]  branchexecpcw;
wire  [ 31:0]  opcodeopcodew;
wire  [ 31:0]  mulopcodepcw;
wire           branchdexecrequestw;
wire  [ 31:0]  mulopcoderaoperandw;
wire           branchexecistakenw;
wire           fetchdecfaultfetchw;
wire           fetchdecvalidw;
wire           fetchfaultfetchw;
wire           lsuopcodeinvalidw;
wire  [ 31:0]  mmulsuaddrw;
wire           mulholdw;
wire           mmuifetchacceptw;
wire           mmulsuackw;
wire  [ 31:0]  fetchpcw;
wire           mmuifetchinvalidatew;
wire  [ 31:0]  mulopcoderboperandw;
wire  [  1:0]  branchcsrprivw;
wire           branchexecrequestw;
wire  [ 31:0]  lsuopcoderaoperandw;
wire           divopcodevalidw;
wire  [  1:0]  branchprivw;
wire           mmulsurdw;
wire  [ 31:0]  fetchdecpcw;
wire           interruptinhibitw;
wire           mmuifetcherrorw;
wire  [  5:0]  writebackmemexceptionw;
wire           fetchinstrlsuw;
wire  [  1:0]  mmuprivdw;
wire  [  4:0]  opcoderaidxw;
wire  [ 31:0]  csropcoderaoperandw;
wire  [ 31:0]  writebackmemvaluew;
wire           writebackdivvalidw;
wire  [  4:0]  mulopcoderbidxw;
wire           opcodeinvalidw;
wire           fetchinstrbranchw;
wire  [ 31:0]  mmuifetchpcw;
wire           mmuifetchrdw;
wire           mmuifetchflushw;
wire  [  4:0]  lsuopcoderdidxw;
wire  [ 31:0]  lsuopcodeopcodew;
wire           mmuloadfaultw;
wire  [ 31:0]  mmusatpw;
wire  [ 31:0]  csrresulte1wdataw;
wire  [ 31:0]  opcoderboperandw;
wire           mmulsuinvalidatew;
wire           fetchdecacceptw;
wire  [  4:0]  csropcoderaidxw;
wire           ifencew;
wire           fetchinstrexecw;
wire  [  4:0]  opcoderdidxw;
wire  [ 31:0]  csrwritebackwdataw;
wire           csrwritebackwritew;
wire           takeinterruptw;
wire  [ 31:0]  csrresulte1valuew;
wire  [ 31:0]  branchdexecpcw;
wire           fetchvalidw;
wire  [ 11:0]  csrwritebackwaddrw;
wire           branchexecisjmpw;
wire           mmulsucacheablew;
wire           fetchinstrcsrw;
wire           lsuopcodevalidw;
wire  [ 31:0]  fetchdecinstrw;
wire           csrresulte1writew;
wire  [ 31:0]  csropcodeopcodew;
wire           fetchinstrdivw;
wire  [ 31:0]  fetchinstrw;
wire           mulopcodeinvalidw;
wire           fetchinstrrdvalidw;
wire  [ 31:0]  mmulsudatardw;
wire           execopcodevalidw;
wire  [ 31:0]  writebackmulvaluew;
wire           mmulsuflushw;
wire  [  4:0]  lsuopcoderbidxw;
wire           mmulsuacceptw;
wire  [ 31:0]  lsuopcoderboperandw;
wire           mmusumw;
wire  [ 31:0]  writebackexecvaluew;
wire  [  4:0]  lsuopcoderaidxw;
wire  [ 31:0]  csrwritebackexceptionpcw;
wire           mmustorefaultw;
wire           branchexeciscallw;


riscvexec
uexec
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.opcodevalidi(execopcodevalidw)
    ,.opcodeopcodei(opcodeopcodew)
    ,.opcodepci(opcodepcw)
    ,.opcodeinvalidi(opcodeinvalidw)
    ,.opcoderdidxi(opcoderdidxw)
    ,.opcoderaidxi(opcoderaidxw)
    ,.opcoderbidxi(opcoderbidxw)
    ,.opcoderaoperandi(opcoderaoperandw)
    ,.opcoderboperandi(opcoderboperandw)
    ,.holdi(execholdw)

    
    ,.branchrequesto(branchexecrequestw)
    ,.branchistakeno(branchexecistakenw)
    ,.branchisnottakeno(branchexecisnottakenw)
    ,.branchsourceo(branchexecsourcew)
    ,.branchiscallo(branchexeciscallw)
    ,.branchisreto(branchexecisretw)
    ,.branchisjmpo(branchexecisjmpw)
    ,.branchpco(branchexecpcw)
    ,.branchdrequesto(branchdexecrequestw)
    ,.branchdpco(branchdexecpcw)
    ,.branchdprivo(branchdexecprivw)
    ,.writebackvalueo(writebackexecvaluew)
);


riscvdecode
#(
     .EXTRADECODESTAGE(EXTRADECODESTAGE)
    ,.SUPPORTMULDIV(SUPPORTMULDIV)
)
udecode
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.fetchinvalidi(fetchdecvalidw)
    ,.fetchininstri(fetchdecinstrw)
    ,.fetchinpci(fetchdecpcw)
    ,.fetchinfaultfetchi(fetchdecfaultfetchw)
    ,.fetchinfaultpagei(fetchdecfaultpagew)
    ,.fetchoutaccepti(fetchacceptw)
    ,.squashdecodei(squashdecodew)

    
    ,.fetchinaccepto(fetchdecacceptw)
    ,.fetchoutvalido(fetchvalidw)
    ,.fetchoutinstro(fetchinstrw)
    ,.fetchoutpco(fetchpcw)
    ,.fetchoutfaultfetcho(fetchfaultfetchw)
    ,.fetchoutfaultpageo(fetchfaultpagew)
    ,.fetchoutinstrexeco(fetchinstrexecw)
    ,.fetchoutinstrlsuo(fetchinstrlsuw)
    ,.fetchoutinstrbrancho(fetchinstrbranchw)
    ,.fetchoutinstrmulo(fetchinstrmulw)
    ,.fetchoutinstrdivo(fetchinstrdivw)
    ,.fetchoutinstrcsro(fetchinstrcsrw)
    ,.fetchoutinstrrdvalido(fetchinstrrdvalidw)
    ,.fetchoutinstrinvalido(fetchinstrinvalidw)
);


riscvmmu
#(
     .MEMCACHEADDRMAX(MEMCACHEADDRMAX)
    ,.SUPPORTMMU(SUPPORTMMU)
    ,.MEMCACHEADDRMIN(MEMCACHEADDRMIN)
)
ummu
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.privdi(mmuprivdw)
    ,.sumi(mmusumw)
    ,.mxri(mmumxrw)
    ,.flushi(mmuflushw)
    ,.satpi(mmusatpw)
    ,.fetchinrdi(mmuifetchrdw)
    ,.fetchinflushi(mmuifetchflushw)
    ,.fetchininvalidatei(mmuifetchinvalidatew)
    ,.fetchinpci(mmuifetchpcw)
    ,.fetchinprivi(fetchinprivw)
    ,.fetchoutaccepti(memiaccepti)
    ,.fetchoutvalidi(memivalidi)
    ,.fetchouterrori(memierrori)
    ,.fetchoutinsti(memiinsti)
    ,.lsuinaddri(mmulsuaddrw)
    ,.lsuindatawri(mmulsudatawrw)
    ,.lsuinrdi(mmulsurdw)
    ,.lsuinwri(mmulsuwrw)
    ,.lsuincacheablei(mmulsucacheablew)
    ,.lsuinreqtagi(mmulsureqtagw)
    ,.lsuininvalidatei(mmulsuinvalidatew)
    ,.lsuinwritebacki(mmulsuwritebackw)
    ,.lsuinflushi(mmulsuflushw)
    ,.lsuoutdatardi(memddatardi)
    ,.lsuoutaccepti(memdaccepti)
    ,.lsuoutacki(memdacki)
    ,.lsuouterrori(memderrori)
    ,.lsuoutresptagi(memdresptagi)

    
    ,.fetchinaccepto(mmuifetchacceptw)
    ,.fetchinvalido(mmuifetchvalidw)
    ,.fetchinerroro(mmuifetcherrorw)
    ,.fetchininsto(mmuifetchinstw)
    ,.fetchoutrdo(memirdo)
    ,.fetchoutflusho(memiflusho)
    ,.fetchoutinvalidateo(memiinvalidateo)
    ,.fetchoutpco(memipco)
    ,.fetchinfaulto(fetchinfaultw)
    ,.lsuindatardo(mmulsudatardw)
    ,.lsuinaccepto(mmulsuacceptw)
    ,.lsuinacko(mmulsuackw)
    ,.lsuinerroro(mmulsuerrorw)
    ,.lsuinresptago(mmulsuresptagw)
    ,.lsuoutaddro(memdaddro)
    ,.lsuoutdatawro(memddatawro)
    ,.lsuoutrdo(memdrdo)
    ,.lsuoutwro(memdwro)
    ,.lsuoutcacheableo(memdcacheableo)
    ,.lsuoutreqtago(memdreqtago)
    ,.lsuoutinvalidateo(memdinvalidateo)
    ,.lsuoutwritebacko(memdwritebacko)
    ,.lsuoutflusho(memdflusho)
    ,.lsuinloadfaulto(mmuloadfaultw)
    ,.lsuinstorefaulto(mmustorefaultw)
);


riscvlsu
#(
     .MEMCACHEADDRMAX(MEMCACHEADDRMAX)
    ,.MEMCACHEADDRMIN(MEMCACHEADDRMIN)
)
ulsu
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.opcodevalidi(lsuopcodevalidw)
    ,.opcodeopcodei(lsuopcodeopcodew)
    ,.opcodepci(lsuopcodepcw)
    ,.opcodeinvalidi(lsuopcodeinvalidw)
    ,.opcoderdidxi(lsuopcoderdidxw)
    ,.opcoderaidxi(lsuopcoderaidxw)
    ,.opcoderbidxi(lsuopcoderbidxw)
    ,.opcoderaoperandi(lsuopcoderaoperandw)
    ,.opcoderboperandi(lsuopcoderboperandw)
    ,.memdatardi(mmulsudatardw)
    ,.memaccepti(mmulsuacceptw)
    ,.memacki(mmulsuackw)
    ,.memerrori(mmulsuerrorw)
    ,.memresptagi(mmulsuresptagw)
    ,.memloadfaulti(mmuloadfaultw)
    ,.memstorefaulti(mmustorefaultw)

    
    ,.memaddro(mmulsuaddrw)
    ,.memdatawro(mmulsudatawrw)
    ,.memrdo(mmulsurdw)
    ,.memwro(mmulsuwrw)
    ,.memcacheableo(mmulsucacheablew)
    ,.memreqtago(mmulsureqtagw)
    ,.meminvalidateo(mmulsuinvalidatew)
    ,.memwritebacko(mmulsuwritebackw)
    ,.memflusho(mmulsuflushw)
    ,.writebackvalido(writebackmemvalidw)
    ,.writebackvalueo(writebackmemvaluew)
    ,.writebackexceptiono(writebackmemexceptionw)
    ,.stallo(lsustallw)
);


riscvcsr
#(
     .SUPPORTSUPER(SUPPORTSUPER)
    ,.SUPPORTMULDIV(SUPPORTMULDIV)
)
ucsr
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.intri(intri)
    ,.opcodevalidi(csropcodevalidw)
    ,.opcodeopcodei(csropcodeopcodew)
    ,.opcodepci(csropcodepcw)
    ,.opcodeinvalidi(csropcodeinvalidw)
    ,.opcoderdidxi(csropcoderdidxw)
    ,.opcoderaidxi(csropcoderaidxw)
    ,.opcoderbidxi(csropcoderbidxw)
    ,.opcoderaoperandi(csropcoderaoperandw)
    ,.opcoderboperandi(csropcoderboperandw)
    ,.csrwritebackwritei(csrwritebackwritew)
    ,.csrwritebackwaddri(csrwritebackwaddrw)
    ,.csrwritebackwdatai(csrwritebackwdataw)
    ,.csrwritebackexceptioni(csrwritebackexceptionw)
    ,.csrwritebackexceptionpci(csrwritebackexceptionpcw)
    ,.csrwritebackexceptionaddri(csrwritebackexceptionaddrw)
    ,.cpuidi(cpuidi)
    ,.resetvectori(resetvectori)
    ,.interruptinhibiti(interruptinhibitw)

    
    ,.csrresulte1valueo(csrresulte1valuew)
    ,.csrresulte1writeo(csrresulte1writew)
    ,.csrresulte1wdatao(csrresulte1wdataw)
    ,.csrresulte1exceptiono(csrresulte1exceptionw)
    ,.branchcsrrequesto(branchcsrrequestw)
    ,.branchcsrpco(branchcsrpcw)
    ,.branchcsrprivo(branchcsrprivw)
    ,.takeinterrupto(takeinterruptw)
    ,.ifenceo(ifencew)
    ,.mmuprivdo(mmuprivdw)
    ,.mmusumo(mmusumw)
    ,.mmumxro(mmumxrw)
    ,.mmuflusho(mmuflushw)
    ,.mmusatpo(mmusatpw)
);


riscvmultiplier
umul
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.opcodevalidi(mulopcodevalidw)
    ,.opcodeopcodei(mulopcodeopcodew)
    ,.opcodepci(mulopcodepcw)
    ,.opcodeinvalidi(mulopcodeinvalidw)
    ,.opcoderdidxi(mulopcoderdidxw)
    ,.opcoderaidxi(mulopcoderaidxw)
    ,.opcoderbidxi(mulopcoderbidxw)
    ,.opcoderaoperandi(mulopcoderaoperandw)
    ,.opcoderboperandi(mulopcoderboperandw)
    ,.holdi(mulholdw)

    
    ,.writebackvalueo(writebackmulvaluew)
);


riscvdivider
udiv
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.opcodevalidi(divopcodevalidw)
    ,.opcodeopcodei(opcodeopcodew)
    ,.opcodepci(opcodepcw)
    ,.opcodeinvalidi(opcodeinvalidw)
    ,.opcoderdidxi(opcoderdidxw)
    ,.opcoderaidxi(opcoderaidxw)
    ,.opcoderbidxi(opcoderbidxw)
    ,.opcoderaoperandi(opcoderaoperandw)
    ,.opcoderboperandi(opcoderboperandw)

    
    ,.writebackvalido(writebackdivvalidw)
    ,.writebackvalueo(writebackdivvaluew)
);


riscvissue
#(
     .SUPPORTREGFILEXILINX(SUPPORTREGFILEXILINX)
    ,.SUPPORTLOADBYPASS(SUPPORTLOADBYPASS)
    ,.SUPPORTMULDIV(SUPPORTMULDIV)
    ,.SUPPORTMULBYPASS(SUPPORTMULBYPASS)
    ,.SUPPORTDUALISSUE(1)
)
uissue
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.fetchvalidi(fetchvalidw)
    ,.fetchinstri(fetchinstrw)
    ,.fetchpci(fetchpcw)
    ,.fetchfaultfetchi(fetchfaultfetchw)
    ,.fetchfaultpagei(fetchfaultpagew)
    ,.fetchinstrexeci(fetchinstrexecw)
    ,.fetchinstrlsui(fetchinstrlsuw)
    ,.fetchinstrbranchi(fetchinstrbranchw)
    ,.fetchinstrmuli(fetchinstrmulw)
    ,.fetchinstrdivi(fetchinstrdivw)
    ,.fetchinstrcsri(fetchinstrcsrw)
    ,.fetchinstrrdvalidi(fetchinstrrdvalidw)
    ,.fetchinstrinvalidi(fetchinstrinvalidw)
    ,.branchexecrequesti(branchexecrequestw)
    ,.branchexecistakeni(branchexecistakenw)
    ,.branchexecisnottakeni(branchexecisnottakenw)
    ,.branchexecsourcei(branchexecsourcew)
    ,.branchexeciscalli(branchexeciscallw)
    ,.branchexecisreti(branchexecisretw)
    ,.branchexecisjmpi(branchexecisjmpw)
    ,.branchexecpci(branchexecpcw)
    ,.branchdexecrequesti(branchdexecrequestw)
    ,.branchdexecpci(branchdexecpcw)
    ,.branchdexecprivi(branchdexecprivw)
    ,.branchcsrrequesti(branchcsrrequestw)
    ,.branchcsrpci(branchcsrpcw)
    ,.branchcsrprivi(branchcsrprivw)
    ,.writebackexecvaluei(writebackexecvaluew)
    ,.writebackmemvalidi(writebackmemvalidw)
    ,.writebackmemvaluei(writebackmemvaluew)
    ,.writebackmemexceptioni(writebackmemexceptionw)
    ,.writebackmulvaluei(writebackmulvaluew)
    ,.writebackdivvalidi(writebackdivvalidw)
    ,.writebackdivvaluei(writebackdivvaluew)
    ,.csrresulte1valuei(csrresulte1valuew)
    ,.csrresulte1writei(csrresulte1writew)
    ,.csrresulte1wdatai(csrresulte1wdataw)
    ,.csrresulte1exceptioni(csrresulte1exceptionw)
    ,.lsustalli(lsustallw)
    ,.takeinterrupti(takeinterruptw)

    
    ,.fetchaccepto(fetchacceptw)
    ,.branchrequesto(branchrequestw)
    ,.branchpco(branchpcw)
    ,.branchprivo(branchprivw)
    ,.execopcodevalido(execopcodevalidw)
    ,.lsuopcodevalido(lsuopcodevalidw)
    ,.csropcodevalido(csropcodevalidw)
    ,.mulopcodevalido(mulopcodevalidw)
    ,.divopcodevalido(divopcodevalidw)
    ,.opcodeopcodeo(opcodeopcodew)
    ,.opcodepco(opcodepcw)
    ,.opcodeinvalido(opcodeinvalidw)
    ,.opcoderdidxo(opcoderdidxw)
    ,.opcoderaidxo(opcoderaidxw)
    ,.opcoderbidxo(opcoderbidxw)
    ,.opcoderaoperando(opcoderaoperandw)
    ,.opcoderboperando(opcoderboperandw)
    ,.lsuopcodeopcodeo(lsuopcodeopcodew)
    ,.lsuopcodepco(lsuopcodepcw)
    ,.lsuopcodeinvalido(lsuopcodeinvalidw)
    ,.lsuopcoderdidxo(lsuopcoderdidxw)
    ,.lsuopcoderaidxo(lsuopcoderaidxw)
    ,.lsuopcoderbidxo(lsuopcoderbidxw)
    ,.lsuopcoderaoperando(lsuopcoderaoperandw)
    ,.lsuopcoderboperando(lsuopcoderboperandw)
    ,.mulopcodeopcodeo(mulopcodeopcodew)
    ,.mulopcodepco(mulopcodepcw)
    ,.mulopcodeinvalido(mulopcodeinvalidw)
    ,.mulopcoderdidxo(mulopcoderdidxw)
    ,.mulopcoderaidxo(mulopcoderaidxw)
    ,.mulopcoderbidxo(mulopcoderbidxw)
    ,.mulopcoderaoperando(mulopcoderaoperandw)
    ,.mulopcoderboperando(mulopcoderboperandw)
    ,.csropcodeopcodeo(csropcodeopcodew)
    ,.csropcodepco(csropcodepcw)
    ,.csropcodeinvalido(csropcodeinvalidw)
    ,.csropcoderdidxo(csropcoderdidxw)
    ,.csropcoderaidxo(csropcoderaidxw)
    ,.csropcoderbidxo(csropcoderbidxw)
    ,.csropcoderaoperando(csropcoderaoperandw)
    ,.csropcoderboperando(csropcoderboperandw)
    ,.csrwritebackwriteo(csrwritebackwritew)
    ,.csrwritebackwaddro(csrwritebackwaddrw)
    ,.csrwritebackwdatao(csrwritebackwdataw)
    ,.csrwritebackexceptiono(csrwritebackexceptionw)
    ,.csrwritebackexceptionpco(csrwritebackexceptionpcw)
    ,.csrwritebackexceptionaddro(csrwritebackexceptionaddrw)
    ,.execholdo(execholdw)
    ,.mulholdo(mulholdw)
    ,.interruptinhibito(interruptinhibitw)
);


riscvfetch
#(
     .SUPPORTMMU(SUPPORTMMU)
)
ufetch
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.fetchaccepti(fetchdecacceptw)
    ,.icacheaccepti(mmuifetchacceptw)
    ,.icachevalidi(mmuifetchvalidw)
    ,.icacheerrori(mmuifetcherrorw)
    ,.icacheinsti(mmuifetchinstw)
    ,.icachepagefaulti(fetchinfaultw)
    ,.fetchinvalidatei(ifencew)
    ,.branchrequesti(branchrequestw)
    ,.branchpci(branchpcw)
    ,.branchprivi(branchprivw)

    
    ,.fetchvalido(fetchdecvalidw)
    ,.fetchinstro(fetchdecinstrw)
    ,.fetchpco(fetchdecpcw)
    ,.fetchfaultfetcho(fetchdecfaultfetchw)
    ,.fetchfaultpageo(fetchdecfaultpagew)
    ,.icacherdo(mmuifetchrdw)
    ,.icacheflusho(mmuifetchflushw)
    ,.icacheinvalidateo(mmuifetchinvalidatew)
    ,.icachepco(mmuifetchpcw)
    ,.icacheprivo(fetchinprivw)
    ,.squashdecodeo(squashdecodew)
);



endmodule

module riscvcsr
#(
     parameter SUPPORTMULDIV   = 1
    ,parameter SUPPORTSUPER    = 1
)
(
    
     input           clki
    ,input           rsti
    ,input           intri
    ,input           opcodevalidi
    ,input  [ 31:0]  opcodeopcodei
    ,input  [ 31:0]  opcodepci
    ,input           opcodeinvalidi
    ,input  [  4:0]  opcoderdidxi
    ,input  [  4:0]  opcoderaidxi
    ,input  [  4:0]  opcoderbidxi
    ,input  [ 31:0]  opcoderaoperandi
    ,input  [ 31:0]  opcoderboperandi
    ,input           csrwritebackwritei
    ,input  [ 11:0]  csrwritebackwaddri
    ,input  [ 31:0]  csrwritebackwdatai
    ,input  [  5:0]  csrwritebackexceptioni
    ,input  [ 31:0]  csrwritebackexceptionpci
    ,input  [ 31:0]  csrwritebackexceptionaddri
    ,input  [ 31:0]  cpuidi
    ,input  [ 31:0]  resetvectori
    ,input           interruptinhibiti

    
    ,output [ 31:0]  csrresulte1valueo
    ,output          csrresulte1writeo
    ,output [ 31:0]  csrresulte1wdatao
    ,output [  5:0]  csrresulte1exceptiono
    ,output          branchcsrrequesto
    ,output [ 31:0]  branchcsrpco
    ,output [  1:0]  branchcsrprivo
    ,output          takeinterrupto
    ,output          ifenceo
    ,output [  1:0]  mmuprivdo
    ,output          mmusumo
    ,output          mmumxro
    ,output          mmuflusho
    ,output [ 31:0]  mmusatpo
);



`include "riscvdefs.v"

wire ecallw             = opcodevalidi && ((opcodeopcodei & `INSTECALLMASK)      == `INSTECALL);
wire ebreakw            = opcodevalidi && ((opcodeopcodei & `INSTEBREAKMASK)     == `INSTEBREAK);
wire eretw              = opcodevalidi && ((opcodeopcodei & `INSTERETMASK)       == `INSTERET);
wire [1:0] eretprivw   = opcodeopcodei[29:28];
wire csrrww             = opcodevalidi && ((opcodeopcodei & `INSTCSRRWMASK)      == `INSTCSRRW);
wire csrrsw             = opcodevalidi && ((opcodeopcodei & `INSTCSRRSMASK)      == `INSTCSRRS);
wire csrrcw             = opcodevalidi && ((opcodeopcodei & `INSTCSRRCMASK)      == `INSTCSRRC);
wire csrrwiw            = opcodevalidi && ((opcodeopcodei & `INSTCSRRWIMASK)     == `INSTCSRRWI);
wire csrrsiw            = opcodevalidi && ((opcodeopcodei & `INSTCSRRSIMASK)     == `INSTCSRRSI);
wire csrrciw            = opcodevalidi && ((opcodeopcodei & `INSTCSRRCIMASK)     == `INSTCSRRCI);
wire wfiw               = opcodevalidi && ((opcodeopcodei & `INSTWFIMASK)        == `INSTWFI);
wire fencew             = opcodevalidi && ((opcodeopcodei & `INSTFENCEMASK)      == `INSTFENCE);
wire sfencew            = opcodevalidi && ((opcodeopcodei & `INSTSFENCEMASK)     == `INSTSFENCE);
wire ifencew            = opcodevalidi && ((opcodeopcodei & `INSTIFENCEMASK)     == `INSTIFENCE);

wire [1:0]  currentprivw;
reg [1:0]   csrprivr;
reg         csrreadonlyr;
reg         csrwriter;
reg         setr;
reg         clrr;
reg         csrfaultr;

reg [31:0]  datar;

always @ *
begin
    setr           = csrrww | csrrsw | csrrwiw | csrrsiw;
    clrr           = csrrww | csrrcw | csrrwiw | csrrciw;

    csrprivr      = opcodeopcodei[29:28];
    csrreadonlyr  = (opcodeopcodei[31:30] == 2'd3);
    csrwriter     = (opcoderaidxi != 5'b0) | csrrww | csrrwiw;

    datar          = (csrrwiw | 
                       csrrsiw | 
                       csrrciw) ?
                            {27'b0, opcoderaidxi} : opcoderaoperandi;

    
    csrfaultr     = SUPPORTSUPER ? (opcodevalidi && (setr | clrr) && ((csrwriter && csrreadonlyr) || (currentprivw < csrprivr))) : 1'b0;
end

wire satpupdatew = (opcodevalidi && (setr || clrr) && csrwriter && (opcodeopcodei[31:20] == `CSRSATP));

wire timerirqw = 1'b0;

wire [31:0] misaw = SUPPORTMULDIV ? (`MISARV32 | `MISARVI | `MISARVM): (`MISARV32 | `MISARVI);

wire [31:0] csrrdataw;

wire        csrbranchw;
wire [31:0] csrtargetw;

wire [31:0] interruptw;
wire [31:0] statusregw;
wire [31:0] satpregw;

riscvcsrregfile
#( .SUPPORTMTIMECMP(1)
  ,.SUPPORTSUPER(SUPPORTSUPER) )
ucsrfile
(
     .clki(clki)
    ,.rsti(rsti)

    ,.extintri(intri)
    ,.timerintri(timerirqw)
    ,.cpuidi(cpuidi)
    ,.misai(misaw)

    
    ,.csrreni(opcodevalidi)
    ,.csrraddri(opcodeopcodei[31:20])
    ,.csrrdatao(csrrdataw)

    
    ,.exceptioni(csrwritebackexceptioni)
    ,.exceptionpci(csrwritebackexceptionpci)
    ,.exceptionaddri(csrwritebackexceptionaddri)

    
    ,.csrwaddri(csrwritebackwritei ? csrwritebackwaddri : 12'b0)
    ,.csrwdatai(csrwritebackwdatai)

    
    ,.csrbrancho(csrbranchw)
    ,.csrtargeto(csrtargetw)

    
    ,.privo(currentprivw)
    ,.statuso(statusregw)
    ,.satpo(satpregw)

    
    ,.interrupto(interruptw)
);

reg                     rdvalide1q;
reg [ 31:0]             rdresulte1q;
reg [ 31:0]             csrwdatae1q;
reg [`EXCEPTIONW-1:0]  exceptione1q;

wire                    eretfaultw = eretw && (currentprivw < eretprivw);

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    rdvalide1q   <= 1'b0;
    rdresulte1q  <= 32'b0;
    csrwdatae1q  <= 32'b0;
    exceptione1q  <= `EXCEPTIONW'b0;
end
else if (opcodevalidi)
begin
    rdvalide1q   <= (setr || clrr) && ~csrfaultr;

    
    
    if (opcodeinvalidi || csrfaultr || eretfaultw)
        rdresulte1q  <= opcodeopcodei;
    else    
        rdresulte1q  <= csrrdataw;

    
    if ((opcodeopcodei & `INSTECALLMASK) == `INSTECALL)
        exceptione1q  <= `EXCEPTIONECALL + {4'b0, currentprivw};
    
    else if (eretfaultw)
        exceptione1q  <= `EXCEPTIONILLEGALINSTRUCTION;
    else if ((opcodeopcodei & `INSTERETMASK) == `INSTERET)
        exceptione1q  <= `EXCEPTIONERETU + {4'b0, eretprivw};
    else if ((opcodeopcodei & `INSTEBREAKMASK) == `INSTEBREAK)
        exceptione1q  <= `EXCEPTIONBREAKPOINT;
    else if (opcodeinvalidi || csrfaultr)
        exceptione1q  <= `EXCEPTIONILLEGALINSTRUCTION;
    
    else if (satpupdatew || ifencew || sfencew)
        exceptione1q  <= `EXCEPTIONFENCE;
    else
        exceptione1q  <= `EXCEPTIONW'b0;

    
    if (setr && clrr)
        csrwdatae1q <= datar;
    else if (setr)
        csrwdatae1q <= csrrdataw | datar;
    else if (clrr)
        csrwdatae1q <= csrrdataw & ~datar;
end
else
begin
    rdvalide1q   <= 1'b0;
    rdresulte1q  <= 32'b0;
    csrwdatae1q  <= 32'b0;
    exceptione1q  <= `EXCEPTIONW'b0;
end

assign csrresulte1valueo     = rdresulte1q;
assign csrresulte1writeo     = rdvalide1q;
assign csrresulte1wdatao     = csrwdatae1q;
assign csrresulte1exceptiono = exceptione1q;

reg takeinterruptq;

always @ (posedge clki or posedge rsti)
if (rsti)
    takeinterruptq    <= 1'b0;
else
    takeinterruptq    <= (|interruptw) & ~interruptinhibiti;

assign takeinterrupto = takeinterruptq;

reg tlbflushq;

always @ (posedge clki or posedge rsti)
if (rsti)
    tlbflushq <= 1'b0;
else
    tlbflushq <= satpupdatew || sfencew;

reg ifenceq;

always @ (posedge clki or posedge rsti)
if (rsti)
    ifenceq    <= 1'b0;
else
    ifenceq    <= ifencew;

assign ifenceo = ifenceq;

reg        branchq;
reg [31:0] branchtargetq;
reg        resetq;

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    branchtargetq <= 32'b0;
    branchq        <= 1'b0;
    resetq         <= 1'b1;
end
else if (resetq)
begin
    branchtargetq <= resetvectori;
    branchq        <= 1'b1;
    resetq         <= 1'b0;
end
else
begin
    branchq        <= csrbranchw;
    branchtargetq <= csrtargetw;
end

assign branchcsrrequesto = branchq;
assign branchcsrpco      = branchtargetq;
assign branchcsrprivo    = satpregw[`SATPMODER] ? currentprivw : `PRIVMACHINE;

assign mmuprivdo     = statusregw[`SRMPRVR] ? statusregw[`SRMPPR] : currentprivw;
assign mmusatpo       = satpregw;
assign mmuflusho      = tlbflushq;
assign mmusumo        = statusregw[`SRSUMR];
assign mmumxro        = statusregw[`SRMXRR];

endmodule
module riscvcsrregfile
#(
     parameter SUPPORTMTIMECMP    = 1,
     parameter SUPPORTSUPER       = 0
)
(
     input           clki
    ,input           rsti

    ,input           extintri
    ,input           timerintri

    ,input [31:0]    cpuidi
    ,input [31:0]    misai

    ,input [5:0]     exceptioni
    ,input [31:0]    exceptionpci
    ,input [31:0]    exceptionaddri

    
    ,input           csrreni
    ,input  [11:0]   csrraddri
    ,output [31:0]   csrrdatao

    
    ,input  [11:0]   csrwaddri
    ,input  [31:0]   csrwdatai

    ,output          csrbrancho
    ,output [31:0]   csrtargeto

    
    ,output [1:0]    privo
    ,output [31:0]   statuso
    ,output [31:0]   satpo

    
    ,output [31:0]   interrupto
);

`include "riscvdefs.v"

reg [31:0]  csrmepcq;
reg [31:0]  csrmcauseq;
reg [31:0]  csrsrq;
reg [31:0]  csrmtvecq;
reg [31:0]  csrmipq;
reg [31:0]  csrmieq;
reg [1:0]   csrmprivq;
reg [31:0]  csrmcycleq;
reg [31:0]  csrmcyclehq;
reg [31:0]  csrmscratchq;
reg [31:0]  csrmtvalq;
reg [31:0]  csrmtimecmpq;
reg         csrmtimeieq;
reg [31:0]  csrmedelegq;
reg [31:0]  csrmidelegq;

reg [31:0]  csrsepcq;
reg [31:0]  csrstvecq;
reg [31:0]  csrscauseq;
reg [31:0]  csrstvalq;
reg [31:0]  csrsatpq;
reg [31:0]  csrsscratchq;

reg [31:0] irqpendingr;
reg [31:0] irqmaskedr;
reg [1:0]  irqprivr;

reg        menabledr;
reg [31:0] minterruptsr;
reg        senabledr;
reg [31:0] sinterruptsr;

always @ *
begin
    if (SUPPORTSUPER)
    begin
        irqpendingr   = (csrmipq & csrmieq);
        menabledr     = (csrmprivq < `PRIVMACHINE) || (csrmprivq == `PRIVMACHINE && csrsrq[`SRMIER]);
        senabledr     = (csrmprivq < `PRIVSUPER)   || (csrmprivq == `PRIVSUPER   && csrsrq[`SRSIER]);
        minterruptsr  = menabledr    ? (irqpendingr & ~csrmidelegq) : 32'b0;
        sinterruptsr  = senabledr    ? (irqpendingr &  csrmidelegq) : 32'b0;
        irqmaskedr    = (|minterruptsr) ? minterruptsr : sinterruptsr;
        irqprivr      = (|minterruptsr) ? `PRIVMACHINE : `PRIVSUPER;
    end
    else
    begin
        irqpendingr   = (csrmipq & csrmieq);
        irqmaskedr    = csrsrq[`SRMIER] ? irqpendingr : 32'b0;
        irqprivr      = `PRIVMACHINE;
    end
end

reg [1:0] irqprivq;
always @ (posedge clki or posedge rsti)
if (rsti)
    irqprivq <= `PRIVMACHINE;
else if (|irqmaskedr)
    irqprivq <= irqprivr;

assign interrupto = irqmaskedr;


reg csrmipupdq;

always @ (posedge clki or posedge rsti)
if (rsti)
    csrmipupdq <= 1'b0;
else if ((csrreni && csrraddri == `CSRMIP) || (csrreni && csrraddri == `CSRSIP))
    csrmipupdq <= 1'b1;
else if (csrwaddri == `CSRMIP || csrwaddri == `CSRSIP || (|exceptioni))
    csrmipupdq <= 1'b0;

wire buffermipw = (csrreni && csrraddri == `CSRMIP) | (csrreni && csrraddri == `CSRSIP) | csrmipupdq;

reg [31:0] rdatar;
always @ *
begin
    rdatar = 32'b0;

    case (csrraddri)
    
    `CSRMSCRATCH: rdatar = csrmscratchq & `CSRMSCRATCHMASK;
    `CSRMEPC:     rdatar = csrmepcq & `CSRMEPCMASK;
    `CSRMTVEC:    rdatar = csrmtvecq & `CSRMTVECMASK;
    `CSRMCAUSE:   rdatar = csrmcauseq & `CSRMCAUSEMASK;
    `CSRMTVAL:    rdatar = csrmtvalq & `CSRMTVALMASK;
    `CSRMSTATUS:  rdatar = csrsrq & `CSRMSTATUSMASK;
    `CSRMIP:      rdatar = csrmipq & `CSRMIPMASK;
    `CSRMIE:      rdatar = csrmieq & `CSRMIEMASK;
    `CSRMCYCLE,
    `CSRMTIME:    rdatar = csrmcycleq;
    `CSRMTIMEH:   rdatar = csrmcyclehq;
    `CSRMHARTID:  rdatar = cpuidi;
    `CSRMISA:     rdatar = misai;
    `CSRMEDELEG:  rdatar = SUPPORTSUPER ? (csrmedelegq & `CSRMEDELEGMASK) : 32'b0;
    `CSRMIDELEG:  rdatar = SUPPORTSUPER ? (csrmidelegq & `CSRMIDELEGMASK) : 32'b0;
    
    `CSRMTIMECMP: rdatar = SUPPORTMTIMECMP ? csrmtimecmpq : 32'b0;
    
    `CSRSSTATUS:  rdatar = SUPPORTSUPER ? (csrsrq       & `CSRSSTATUSMASK)  : 32'b0;
    `CSRSIP:      rdatar = SUPPORTSUPER ? (csrmipq      & `CSRSIPMASK)      : 32'b0;
    `CSRSIE:      rdatar = SUPPORTSUPER ? (csrmieq      & `CSRSIEMASK)      : 32'b0;
    `CSRSEPC:     rdatar = SUPPORTSUPER ? (csrsepcq     & `CSRSEPCMASK)     : 32'b0;
    `CSRSTVEC:    rdatar = SUPPORTSUPER ? (csrstvecq    & `CSRSTVECMASK)    : 32'b0;
    `CSRSCAUSE:   rdatar = SUPPORTSUPER ? (csrscauseq   & `CSRSCAUSEMASK)   : 32'b0;
    `CSRSTVAL:    rdatar = SUPPORTSUPER ? (csrstvalq    & `CSRSTVALMASK)    : 32'b0;
    `CSRSATP:     rdatar = SUPPORTSUPER ? (csrsatpq     & `CSRSATPMASK)     : 32'b0;
    `CSRSSCRATCH: rdatar = SUPPORTSUPER ? (csrsscratchq & `CSRSSCRATCHMASK) : 32'b0;
    default:       rdatar = 32'b0;
    endcase
end

assign csrrdatao = rdatar;
assign privo      = csrmprivq;
assign statuso    = csrsrq;
assign satpo      = csrsatpq;

reg [31:0]  csrmepcr;
reg [31:0]  csrmcauser;
reg [31:0]  csrmtvalr;
reg [31:0]  csrsrr;
reg [31:0]  csrmtvecr;
reg [31:0]  csrmipr;
reg [31:0]  csrmier;
reg [1:0]   csrmprivr;
reg [31:0]  csrmcycler;
reg [31:0]  csrmscratchr;
reg [31:0]  csrmtimecmpr;
reg         csrmtimeier;
reg [31:0]  csrmedelegr;
reg [31:0]  csrmidelegr;

reg [31:0]  csrmipnextq;
reg [31:0]  csrmipnextr;

reg [31:0]  csrsepcr;
reg [31:0]  csrstvecr;
reg [31:0]  csrscauser;
reg [31:0]  csrstvalr;
reg [31:0]  csrsatpr;
reg [31:0]  csrsscratchr;

wire isexceptionw = ((exceptioni & `EXCEPTIONTYPEMASK) == `EXCEPTIONEXCEPTION);
wire exceptionsw  = SUPPORTSUPER ? ((csrmprivq <= `PRIVSUPER) & isexceptionw & csrmedelegq[{1'b0, exceptioni[`EXCEPTIONSUBTYPER]}]) : 1'b0;

always @ *
begin
    
    csrmipnextr  = csrmipnextq;
    csrmepcr      = csrmepcq;
    csrsrr        = csrsrq;
    csrmcauser    = csrmcauseq;
    csrmtvalr     = csrmtvalq;
    csrmtvecr     = csrmtvecq;
    csrmipr       = csrmipq;
    csrmier       = csrmieq;
    csrmprivr     = csrmprivq;
    csrmscratchr  = csrmscratchq;
    csrmcycler    = csrmcycleq + 32'd1;
    csrmtimecmpr  = csrmtimecmpq;
    csrmtimeier  = csrmtimeieq;
    csrmedelegr   = csrmedelegq;
    csrmidelegr   = csrmidelegq;

    
    csrsepcr      = csrsepcq;
    csrstvecr     = csrstvecq;
    csrscauser    = csrscauseq;
    csrstvalr     = csrstvalq;
    csrsatpr      = csrsatpq;
    csrsscratchr  = csrsscratchq;

    
    if ((exceptioni & `EXCEPTIONTYPEMASK) == `EXCEPTIONINTERRUPT)
    begin
        
        if (irqprivq == `PRIVMACHINE)
        begin
            
            csrsrr[`SRMPIER] = csrsrr[`SRMIER];
            csrsrr[`SRMPPR]  = csrmprivq;

            
            csrsrr[`SRMIER]  = 1'b0;

            
            csrmprivr          = `PRIVMACHINE;

            
            csrmepcr           = exceptionpci;
            csrmtvalr          = 32'b0;

            
            if (interrupto[`IRQMSOFT])
                csrmcauser = `MCAUSEINTERRUPT + 32'd`IRQMSOFT;
            else if (interrupto[`IRQMTIMER])
                csrmcauser = `MCAUSEINTERRUPT + 32'd`IRQMTIMER;
            else if (interrupto[`IRQMEXT])
                csrmcauser = `MCAUSEINTERRUPT + 32'd`IRQMEXT;
        end
        
        else
        begin
            
            csrsrr[`SRSPIER] = csrsrr[`SRSIER];
            csrsrr[`SRSPPR]  = (csrmprivq == `PRIVSUPER);

            
            csrsrr[`SRSIER]  = 1'b0;

            
            csrmprivr  = `PRIVSUPER;

            
            csrsepcr   = exceptionpci;
            csrstvalr  = 32'b0;

            
            if (interrupto[`IRQSSOFT])
                csrscauser = `MCAUSEINTERRUPT + 32'd`IRQSSOFT;
            else if (interrupto[`IRQSTIMER])
                csrscauser = `MCAUSEINTERRUPT + 32'd`IRQSTIMER;
            else if (interrupto[`IRQSEXT])
                csrscauser = `MCAUSEINTERRUPT + 32'd`IRQSEXT;
        end
    end
    
    else if (exceptioni >= `EXCEPTIONERETU && exceptioni <= `EXCEPTIONERETM)
    begin
        
        if (exceptioni[1:0] == `PRIVMACHINE)
        begin
            
            csrmprivr          = csrsrr[`SRMPPR];

            
            csrsrr[`SRMIER]  = csrsrr[`SRMPIER];
            csrsrr[`SRMPIER] = 1'b1;

            
            csrsrr[`SRMPPR] = `SRMPPU;
        end
        
        else
        begin
            
            csrmprivr          = csrsrr[`SRSPPR] ? `PRIVSUPER : `PRIVUSER;

            
            csrsrr[`SRSIER]  = csrsrr[`SRSPIER];
            csrsrr[`SRSPIER] = 1'b1;

            
            csrsrr[`SRSPPR] = 1'b0;
        end
    end
    
    else if (isexceptionw && exceptionsw)
    begin
        
        csrsrr[`SRSPIER] = csrsrr[`SRSIER];
        csrsrr[`SRSPPR]  = (csrmprivq == `PRIVSUPER);

        
        csrsrr[`SRSIER]  = 1'b0;

        
        csrmprivr  = `PRIVSUPER;

        
        csrsepcr   = exceptionpci;

        
        case (exceptioni)
        `EXCEPTIONMISALIGNEDFETCH,
        `EXCEPTIONFAULTFETCH,
        `EXCEPTIONPAGEFAULTINST:     csrstvalr = exceptionpci;
        `EXCEPTIONILLEGALINSTRUCTION,
        `EXCEPTIONMISALIGNEDLOAD,
        `EXCEPTIONFAULTLOAD,
        `EXCEPTIONMISALIGNEDSTORE,
        `EXCEPTIONFAULTSTORE,
        `EXCEPTIONPAGEFAULTLOAD,
        `EXCEPTIONPAGEFAULTSTORE:    csrstvalr = exceptionaddri;
        default:                        csrstvalr = 32'b0;
        endcase

        
        csrscauser = {28'b0, exceptioni[3:0]};
    end
    
    else if (isexceptionw)
    begin
        
        csrsrr[`SRMPIER] = csrsrr[`SRMIER];
        csrsrr[`SRMPPR]  = csrmprivq;

        
        csrsrr[`SRMIER]  = 1'b0;

        
        csrmprivr  = `PRIVMACHINE;

        
        csrmepcr   = exceptionpci;

        
        case (exceptioni)
        `EXCEPTIONMISALIGNEDFETCH,
        `EXCEPTIONFAULTFETCH,
        `EXCEPTIONPAGEFAULTINST:     csrmtvalr = exceptionpci;
        `EXCEPTIONILLEGALINSTRUCTION,
        `EXCEPTIONMISALIGNEDLOAD,
        `EXCEPTIONFAULTLOAD,
        `EXCEPTIONMISALIGNEDSTORE,
        `EXCEPTIONFAULTSTORE,
        `EXCEPTIONPAGEFAULTLOAD,
        `EXCEPTIONPAGEFAULTSTORE:    csrmtvalr = exceptionaddri;
        default:                        csrmtvalr = 32'b0;
        endcase        

        
        csrmcauser = {28'b0, exceptioni[3:0]};
    end
    else
    begin
        case (csrwaddri)
        
        `CSRMSCRATCH: csrmscratchr = csrwdatai & `CSRMSCRATCHMASK;
        `CSRMEPC:     csrmepcr     = csrwdatai & `CSRMEPCMASK;
        `CSRMTVEC:    csrmtvecr    = csrwdatai & `CSRMTVECMASK;
        `CSRMCAUSE:   csrmcauser   = csrwdatai & `CSRMCAUSEMASK;
        `CSRMTVAL:    csrmtvalr    = csrwdatai & `CSRMTVALMASK;
        `CSRMSTATUS:  csrsrr       = csrwdatai & `CSRMSTATUSMASK;
        `CSRMIP:      csrmipr      = csrwdatai & `CSRMIPMASK;
        `CSRMIE:      csrmier      = csrwdatai & `CSRMIEMASK;
        `CSRMEDELEG:  csrmedelegr  = csrwdatai & `CSRMEDELEGMASK;
        `CSRMIDELEG:  csrmidelegr  = csrwdatai & `CSRMIDELEGMASK;
        
        `CSRMTIMECMP:
        begin
            csrmtimecmpr = csrwdatai & `CSRMTIMECMPMASK;
            csrmtimeier = 1'b1;
        end
        
        `CSRSEPC:     csrsepcr     = csrwdatai & `CSRSEPCMASK;
        `CSRSTVEC:    csrstvecr    = csrwdatai & `CSRSTVECMASK;
        `CSRSCAUSE:   csrscauser   = csrwdatai & `CSRSCAUSEMASK;
        `CSRSTVAL:    csrstvalr    = csrwdatai & `CSRSTVALMASK;
        `CSRSATP:     csrsatpr     = csrwdatai & `CSRSATPMASK;
        `CSRSSCRATCH: csrsscratchr = csrwdatai & `CSRSSCRATCHMASK;
        `CSRSSTATUS:  csrsrr       = (csrsrr & ~`CSRSSTATUSMASK) | (csrwdatai & `CSRSSTATUSMASK);
        `CSRSIP:      csrmipr      = (csrmipr & ~`CSRSIPMASK) | (csrwdatai & `CSRSIPMASK);
        `CSRSIE:      csrmier      = (csrmier & ~`CSRSIEMASK) | (csrwdatai & `CSRSIEMASK);
        default:
            ;
        endcase
    end
 
    
    
    if (extintri   &&  csrmidelegq[`SRIPMEIPR]) csrmipnextr[`SRIPSEIPR] = 1'b1;
    if (extintri   && ~csrmidelegq[`SRIPMEIPR]) csrmipnextr[`SRIPMEIPR] = 1'b1;
    if (timerintri &&  csrmidelegq[`SRIPMTIPR]) csrmipnextr[`SRIPSTIPR] = 1'b1;
    if (timerintri && ~csrmidelegq[`SRIPMTIPR]) csrmipnextr[`SRIPMTIPR] = 1'b1;

    
    if (SUPPORTMTIMECMP && csrmcycleq == csrmtimecmpq)
    begin
        if (csrmidelegq[`SRIPMTIPR])
            csrmipnextr[`SRIPSTIPR] = csrmtimeieq;
        else
            csrmipnextr[`SRIPMTIPR] = csrmtimeieq;
        csrmtimeier  = 1'b0;
    end

    csrmipr = csrmipr | csrmipnextr;
end

`ifdef verilator
`define HASSIMCTRL
`endif
`ifdef verilogsim
`define HASSIMCTRL
`endif

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    
    csrmepcq         <= 32'b0;
    csrsrq           <= 32'b0;
    csrmcauseq       <= 32'b0;
    csrmtvalq        <= 32'b0;
    csrmtvecq        <= 32'b0;
    csrmipq          <= 32'b0;
    csrmieq          <= 32'b0;
    csrmprivq        <= `PRIVMACHINE;
    csrmcycleq       <= 32'b0;
    csrmcyclehq     <= 32'b0;
    csrmscratchq     <= 32'b0;
    csrmtimecmpq     <= 32'b0;
    csrmtimeieq     <= 1'b0;
    csrmedelegq      <= 32'b0;
    csrmidelegq      <= 32'b0;

    
    csrsepcq         <= 32'b0;
    csrstvecq        <= 32'b0;
    csrscauseq       <= 32'b0;
    csrstvalq        <= 32'b0;
    csrsatpq         <= 32'b0;
    csrsscratchq     <= 32'b0;

    csrmipnextq     <= 32'b0;
end
else
begin
    
    csrmepcq         <= csrmepcr;
    csrsrq           <= csrsrr;
    csrmcauseq       <= csrmcauser;
    csrmtvalq        <= csrmtvalr;
    csrmtvecq        <= csrmtvecr;
    csrmipq          <= csrmipr;
    csrmieq          <= csrmier;
    csrmprivq        <= SUPPORTSUPER ? csrmprivr : `PRIVMACHINE;
    csrmcycleq       <= csrmcycler;
    csrmscratchq     <= csrmscratchr;
    csrmtimecmpq     <= SUPPORTMTIMECMP ? csrmtimecmpr : 32'b0;
    csrmtimeieq     <= SUPPORTMTIMECMP ? csrmtimeier : 1'b0;
    csrmedelegq      <= SUPPORTSUPER ? (csrmedelegr   & `CSRMEDELEGMASK) : 32'b0;
    csrmidelegq      <= SUPPORTSUPER ? (csrmidelegr   & `CSRMIDELEGMASK) : 32'b0;

    
    csrsepcq         <= SUPPORTSUPER ? (csrsepcr     & `CSRSEPCMASK)     : 32'b0;
    csrstvecq        <= SUPPORTSUPER ? (csrstvecr    & `CSRSTVECMASK)    : 32'b0;
    csrscauseq       <= SUPPORTSUPER ? (csrscauser   & `CSRSCAUSEMASK)   : 32'b0;
    csrstvalq        <= SUPPORTSUPER ? (csrstvalr    & `CSRSTVALMASK)    : 32'b0;
    csrsatpq         <= SUPPORTSUPER ? (csrsatpr     & `CSRSATPMASK)     : 32'b0;
    csrsscratchq     <= SUPPORTSUPER ? (csrsscratchr & `CSRSSCRATCHMASK) : 32'b0;

    csrmipnextq     <= buffermipw ? csrmipnextr : 32'b0;

    
    if (csrmcycleq == 32'hFFFFFFFF)
        csrmcyclehq <= csrmcyclehq + 32'd1;

`ifdef HASSIMCTRL
    
    if ((csrwaddri == `CSRDSCRATCH || csrwaddri == `CSRSIMCTRL) && ~(|exceptioni))
    begin
        case (csrwdatai & 32'hFF000000)
        `CSRSIMCTRLEXIT:
        begin
            
            $finish;
            $finish;
        end
        `CSRSIMCTRLPUTC:
        begin
            $write("%c", csrwdatai[7:0]);
        end
        endcase
    end
`endif
end

reg        branchr;
reg [31:0] branchtargetr;

always @ *
begin
    branchr        = 1'b0;
    branchtargetr = 32'b0;

    
    if (exceptioni == `EXCEPTIONINTERRUPT)
    begin
        branchr        = 1'b1;
        branchtargetr = (irqprivq == `PRIVMACHINE) ? csrmtvecq : csrstvecq;
    end
    
    else if (exceptioni >= `EXCEPTIONERETU && exceptioni <= `EXCEPTIONERETM)
    begin
        
        if (exceptioni[1:0] == `PRIVMACHINE)
        begin    
            branchr        = 1'b1;
            branchtargetr = csrmepcq;
        end
        
        else
        begin
            branchr        = 1'b1;
            branchtargetr = csrsepcq;
        end
    end
    
    else if (isexceptionw && exceptionsw)
    begin
        branchr        = 1'b1;
        branchtargetr = csrstvecq;
    end
    
    else if (isexceptionw)
    begin
        branchr        = 1'b1;
        branchtargetr = csrmtvecq;
    end
    
    else if (exceptioni == `EXCEPTIONFENCE)
    begin
        branchr        = 1'b1;
        branchtargetr = exceptionpci + 32'd4;
    end
end

assign csrbrancho = branchr;
assign csrtargeto = branchtargetr;

`ifdef verilator
function [31:0] getmcycle; /*verilator public*/
begin
    getmcycle = csrmcycleq;
end
endfunction
`endif

endmodule

module riscvdecode
#(
     parameter SUPPORTMULDIV   = 1
    ,parameter EXTRADECODESTAGE = 0
)
(
    
     input           clki
    ,input           rsti
    ,input           fetchinvalidi
    ,input  [ 31:0]  fetchininstri
    ,input  [ 31:0]  fetchinpci
    ,input           fetchinfaultfetchi
    ,input           fetchinfaultpagei
    ,input           fetchoutaccepti
    ,input           squashdecodei

    
    ,output          fetchinaccepto
    ,output          fetchoutvalido
    ,output [ 31:0]  fetchoutinstro
    ,output [ 31:0]  fetchoutpco
    ,output          fetchoutfaultfetcho
    ,output          fetchoutfaultpageo
    ,output          fetchoutinstrexeco
    ,output          fetchoutinstrlsuo
    ,output          fetchoutinstrbrancho
    ,output          fetchoutinstrmulo
    ,output          fetchoutinstrdivo
    ,output          fetchoutinstrcsro
    ,output          fetchoutinstrrdvalido
    ,output          fetchoutinstrinvalido
);



wire        enablemuldivw     = SUPPORTMULDIV;

generate
if (EXTRADECODESTAGE)
begin
    wire [31:0] fetchininstrw = (fetchinfaultpagei | fetchinfaultfetchi) ? 32'b0 : fetchininstri;
    reg [66:0]  bufferq;

    always @(posedge clki or posedge rsti)
    if (rsti)
        bufferq <= 67'b0;
    else if (squashdecodei)
        bufferq <= 67'b0;
    else if (fetchoutaccepti || !fetchoutvalido)
        bufferq <= {fetchinvalidi, fetchinfaultpagei, fetchinfaultfetchi, fetchininstrw, fetchinpci};

    assign {fetchoutvalido,
            fetchoutfaultpageo,
            fetchoutfaultfetcho,
            fetchoutinstro,
            fetchoutpco} = bufferq;

    riscvdecoder
    udec
    (
         .validi(fetchoutvalido)
        ,.fetchfaulti(fetchoutfaultpageo | fetchoutfaultfetcho)
        ,.enablemuldivi(enablemuldivw)
        ,.opcodei(fetchoutinstro)

        ,.invalido(fetchoutinstrinvalido)
        ,.execo(fetchoutinstrexeco)
        ,.lsuo(fetchoutinstrlsuo)
        ,.brancho(fetchoutinstrbrancho)
        ,.mulo(fetchoutinstrmulo)
        ,.divo(fetchoutinstrdivo)
        ,.csro(fetchoutinstrcsro)
        ,.rdvalido(fetchoutinstrrdvalido)
    );

    assign fetchinaccepto        = fetchoutaccepti;
end
else
begin
    wire [31:0] fetchininstrw = (fetchinfaultpagei | fetchinfaultfetchi) ? 32'b0 : fetchininstri;

    riscvdecoder
    udec
    (
         .validi(fetchinvalidi)
        ,.fetchfaulti(fetchinfaultfetchi | fetchinfaultpagei)
        ,.enablemuldivi(enablemuldivw)
        ,.opcodei(fetchoutinstro)

        ,.invalido(fetchoutinstrinvalido)
        ,.execo(fetchoutinstrexeco)
        ,.lsuo(fetchoutinstrlsuo)
        ,.brancho(fetchoutinstrbrancho)
        ,.mulo(fetchoutinstrmulo)
        ,.divo(fetchoutinstrdivo)
        ,.csro(fetchoutinstrcsro)
        ,.rdvalido(fetchoutinstrrdvalido)
    );

    
    assign fetchoutvalido        = fetchinvalidi;
    assign fetchoutpco           = fetchinpci;
    assign fetchoutinstro        = fetchininstrw;
    assign fetchoutfaultpageo   = fetchinfaultpagei;
    assign fetchoutfaultfetcho  = fetchinfaultfetchi;

    assign fetchinaccepto        = fetchoutaccepti;
end
endgenerate


endmodule
`include "riscvdefs.v"

module riscvdecoder
(
     input                        validi
    ,input                        fetchfaulti
    ,input                        enablemuldivi
    ,input  [31:0]                opcodei

    ,output                       invalido
    ,output                       execo
    ,output                       lsuo
    ,output                       brancho
    ,output                       mulo
    ,output                       divo
    ,output                       csro
    ,output                       rdvalido
);

wire invalidw =    validi && 
                   ~(((opcodei & `INSTANDIMASK) == `INSTANDI)             ||
                    ((opcodei & `INSTADDIMASK) == `INSTADDI)              ||
                    ((opcodei & `INSTSLTIMASK) == `INSTSLTI)              ||
                    ((opcodei & `INSTSLTIUMASK) == `INSTSLTIU)            ||
                    ((opcodei & `INSTORIMASK) == `INSTORI)                ||
                    ((opcodei & `INSTXORIMASK) == `INSTXORI)              ||
                    ((opcodei & `INSTSLLIMASK) == `INSTSLLI)              ||
                    ((opcodei & `INSTSRLIMASK) == `INSTSRLI)              ||
                    ((opcodei & `INSTSRAIMASK) == `INSTSRAI)              ||
                    ((opcodei & `INSTLUIMASK) == `INSTLUI)                ||
                    ((opcodei & `INSTAUIPCMASK) == `INSTAUIPC)            ||
                    ((opcodei & `INSTADDMASK) == `INSTADD)                ||
                    ((opcodei & `INSTSUBMASK) == `INSTSUB)                ||
                    ((opcodei & `INSTSLTMASK) == `INSTSLT)                ||
                    ((opcodei & `INSTSLTUMASK) == `INSTSLTU)              ||
                    ((opcodei & `INSTXORMASK) == `INSTXOR)                ||
                    ((opcodei & `INSTORMASK) == `INSTOR)                  ||
                    ((opcodei & `INSTANDMASK) == `INSTAND)                ||
                    ((opcodei & `INSTSLLMASK) == `INSTSLL)                ||
                    ((opcodei & `INSTSRLMASK) == `INSTSRL)                ||
                    ((opcodei & `INSTSRAMASK) == `INSTSRA)                ||
                    ((opcodei & `INSTJALMASK) == `INSTJAL)                ||
                    ((opcodei & `INSTJALRMASK) == `INSTJALR)              ||
                    ((opcodei & `INSTBEQMASK) == `INSTBEQ)                ||
                    ((opcodei & `INSTBNEMASK) == `INSTBNE)                ||
                    ((opcodei & `INSTBLTMASK) == `INSTBLT)                ||
                    ((opcodei & `INSTBGEMASK) == `INSTBGE)                ||
                    ((opcodei & `INSTBLTUMASK) == `INSTBLTU)              ||
                    ((opcodei & `INSTBGEUMASK) == `INSTBGEU)              ||
                    ((opcodei & `INSTLBMASK) == `INSTLB)                  ||
                    ((opcodei & `INSTLHMASK) == `INSTLH)                  ||
                    ((opcodei & `INSTLWMASK) == `INSTLW)                  ||
                    ((opcodei & `INSTLBUMASK) == `INSTLBU)                ||
                    ((opcodei & `INSTLHUMASK) == `INSTLHU)                ||
                    ((opcodei & `INSTLWUMASK) == `INSTLWU)                ||
                    ((opcodei & `INSTSBMASK) == `INSTSB)                  ||
                    ((opcodei & `INSTSHMASK) == `INSTSH)                  ||
                    ((opcodei & `INSTSWMASK) == `INSTSW)                  ||
                    ((opcodei & `INSTECALLMASK) == `INSTECALL)            ||
                    ((opcodei & `INSTEBREAKMASK) == `INSTEBREAK)          ||
                    ((opcodei & `INSTERETMASK) == `INSTERET)              ||
                    ((opcodei & `INSTCSRRWMASK) == `INSTCSRRW)            ||
                    ((opcodei & `INSTCSRRSMASK) == `INSTCSRRS)            ||
                    ((opcodei & `INSTCSRRCMASK) == `INSTCSRRC)            ||
                    ((opcodei & `INSTCSRRWIMASK) == `INSTCSRRWI)          ||
                    ((opcodei & `INSTCSRRSIMASK) == `INSTCSRRSI)          ||
                    ((opcodei & `INSTCSRRCIMASK) == `INSTCSRRCI)          ||
                    ((opcodei & `INSTWFIMASK) == `INSTWFI)                ||
                    ((opcodei & `INSTFENCEMASK) == `INSTFENCE)            ||
                    ((opcodei & `INSTIFENCEMASK) == `INSTIFENCE)          ||
                    ((opcodei & `INSTSFENCEMASK) == `INSTSFENCE)          ||
                    (enablemuldivi && (opcodei & `INSTMULMASK) == `INSTMUL)       ||
                    (enablemuldivi && (opcodei & `INSTMULHMASK) == `INSTMULH)     ||
                    (enablemuldivi && (opcodei & `INSTMULHSUMASK) == `INSTMULHSU) ||
                    (enablemuldivi && (opcodei & `INSTMULHUMASK) == `INSTMULHU)   ||
                    (enablemuldivi && (opcodei & `INSTDIVMASK) == `INSTDIV)       ||
                    (enablemuldivi && (opcodei & `INSTDIVUMASK) == `INSTDIVU)     ||
                    (enablemuldivi && (opcodei & `INSTREMMASK) == `INSTREM)       ||
                    (enablemuldivi && (opcodei & `INSTREMUMASK) == `INSTREMU));

assign invalido = invalidw;

assign rdvalido = ((opcodei & `INSTJALRMASK) == `INSTJALR)     ||
                    ((opcodei & `INSTJALMASK) == `INSTJAL)       ||
                    ((opcodei & `INSTLUIMASK) == `INSTLUI)       ||
                    ((opcodei & `INSTAUIPCMASK) == `INSTAUIPC)   ||
                    ((opcodei & `INSTADDIMASK) == `INSTADDI)     ||
                    ((opcodei & `INSTSLLIMASK) == `INSTSLLI)     ||
                    ((opcodei & `INSTSLTIMASK) == `INSTSLTI)     ||
                    ((opcodei & `INSTSLTIUMASK) == `INSTSLTIU)   ||
                    ((opcodei & `INSTXORIMASK) == `INSTXORI)     ||
                    ((opcodei & `INSTSRLIMASK) == `INSTSRLI)     ||
                    ((opcodei & `INSTSRAIMASK) == `INSTSRAI)     ||
                    ((opcodei & `INSTORIMASK) == `INSTORI)       ||
                    ((opcodei & `INSTANDIMASK) == `INSTANDI)     ||
                    ((opcodei & `INSTADDMASK) == `INSTADD)       ||
                    ((opcodei & `INSTSUBMASK) == `INSTSUB)       ||
                    ((opcodei & `INSTSLLMASK) == `INSTSLL)       ||
                    ((opcodei & `INSTSLTMASK) == `INSTSLT)       ||
                    ((opcodei & `INSTSLTUMASK) == `INSTSLTU)     ||
                    ((opcodei & `INSTXORMASK) == `INSTXOR)       ||
                    ((opcodei & `INSTSRLMASK) == `INSTSRL)       ||
                    ((opcodei & `INSTSRAMASK) == `INSTSRA)       ||
                    ((opcodei & `INSTORMASK) == `INSTOR)         ||
                    ((opcodei & `INSTANDMASK) == `INSTAND)       ||
                    ((opcodei & `INSTLBMASK) == `INSTLB)         ||
                    ((opcodei & `INSTLHMASK) == `INSTLH)         ||
                    ((opcodei & `INSTLWMASK) == `INSTLW)         ||
                    ((opcodei & `INSTLBUMASK) == `INSTLBU)       ||
                    ((opcodei & `INSTLHUMASK) == `INSTLHU)       ||
                    ((opcodei & `INSTLWUMASK) == `INSTLWU)       ||
                    ((opcodei & `INSTMULMASK) == `INSTMUL)       ||
                    ((opcodei & `INSTMULHMASK) == `INSTMULH)     ||
                    ((opcodei & `INSTMULHSUMASK) == `INSTMULHSU) ||
                    ((opcodei & `INSTMULHUMASK) == `INSTMULHU)   ||
                    ((opcodei & `INSTDIVMASK) == `INSTDIV)       ||
                    ((opcodei & `INSTDIVUMASK) == `INSTDIVU)     ||
                    ((opcodei & `INSTREMMASK) == `INSTREM)       ||
                    ((opcodei & `INSTREMUMASK) == `INSTREMU)     ||
                    ((opcodei & `INSTCSRRWMASK) == `INSTCSRRW)   ||
                    ((opcodei & `INSTCSRRSMASK) == `INSTCSRRS)   ||
                    ((opcodei & `INSTCSRRCMASK) == `INSTCSRRC)   ||
                    ((opcodei & `INSTCSRRWIMASK) == `INSTCSRRWI) ||
                    ((opcodei & `INSTCSRRSIMASK) == `INSTCSRRSI) ||
                    ((opcodei & `INSTCSRRCIMASK) == `INSTCSRRCI);

assign execo =     ((opcodei & `INSTANDIMASK) == `INSTANDI)  ||
                    ((opcodei & `INSTADDIMASK) == `INSTADDI)  ||
                    ((opcodei & `INSTSLTIMASK) == `INSTSLTI)  ||
                    ((opcodei & `INSTSLTIUMASK) == `INSTSLTIU)||
                    ((opcodei & `INSTORIMASK) == `INSTORI)    ||
                    ((opcodei & `INSTXORIMASK) == `INSTXORI)  ||
                    ((opcodei & `INSTSLLIMASK) == `INSTSLLI)  ||
                    ((opcodei & `INSTSRLIMASK) == `INSTSRLI)  ||
                    ((opcodei & `INSTSRAIMASK) == `INSTSRAI)  ||
                    ((opcodei & `INSTLUIMASK) == `INSTLUI)    ||
                    ((opcodei & `INSTAUIPCMASK) == `INSTAUIPC)||
                    ((opcodei & `INSTADDMASK) == `INSTADD)    ||
                    ((opcodei & `INSTSUBMASK) == `INSTSUB)    ||
                    ((opcodei & `INSTSLTMASK) == `INSTSLT)    ||
                    ((opcodei & `INSTSLTUMASK) == `INSTSLTU)  ||
                    ((opcodei & `INSTXORMASK) == `INSTXOR)    ||
                    ((opcodei & `INSTORMASK) == `INSTOR)      ||
                    ((opcodei & `INSTANDMASK) == `INSTAND)    ||
                    ((opcodei & `INSTSLLMASK) == `INSTSLL)    ||
                    ((opcodei & `INSTSRLMASK) == `INSTSRL)    ||
                    ((opcodei & `INSTSRAMASK) == `INSTSRA);

assign lsuo =      ((opcodei & `INSTLBMASK) == `INSTLB)   ||
                    ((opcodei & `INSTLHMASK) == `INSTLH)   ||
                    ((opcodei & `INSTLWMASK) == `INSTLW)   ||
                    ((opcodei & `INSTLBUMASK) == `INSTLBU) ||
                    ((opcodei & `INSTLHUMASK) == `INSTLHU) ||
                    ((opcodei & `INSTLWUMASK) == `INSTLWU) ||
                    ((opcodei & `INSTSBMASK) == `INSTSB)   ||
                    ((opcodei & `INSTSHMASK) == `INSTSH)   ||
                    ((opcodei & `INSTSWMASK) == `INSTSW);

assign brancho =   ((opcodei & `INSTJALMASK) == `INSTJAL)   ||
                    ((opcodei & `INSTJALRMASK) == `INSTJALR) ||
                    ((opcodei & `INSTBEQMASK) == `INSTBEQ)   ||
                    ((opcodei & `INSTBNEMASK) == `INSTBNE)   ||
                    ((opcodei & `INSTBLTMASK) == `INSTBLT)   ||
                    ((opcodei & `INSTBGEMASK) == `INSTBGE)   ||
                    ((opcodei & `INSTBLTUMASK) == `INSTBLTU) ||
                    ((opcodei & `INSTBGEUMASK) == `INSTBGEU);

assign mulo =      enablemuldivi &&
                    (((opcodei & `INSTMULMASK) == `INSTMUL)    ||
                    ((opcodei & `INSTMULHMASK) == `INSTMULH)   ||
                    ((opcodei & `INSTMULHSUMASK) == `INSTMULHSU) ||
                    ((opcodei & `INSTMULHUMASK) == `INSTMULHU));

assign divo =      enablemuldivi &&
                    (((opcodei & `INSTDIVMASK) == `INSTDIV) ||
                    ((opcodei & `INSTDIVUMASK) == `INSTDIVU) ||
                    ((opcodei & `INSTREMMASK) == `INSTREM) ||
                    ((opcodei & `INSTREMUMASK) == `INSTREMU));

assign csro =      ((opcodei & `INSTECALLMASK) == `INSTECALL)            ||
                    ((opcodei & `INSTEBREAKMASK) == `INSTEBREAK)          ||
                    ((opcodei & `INSTERETMASK) == `INSTERET)              ||
                    ((opcodei & `INSTCSRRWMASK) == `INSTCSRRW)            ||
                    ((opcodei & `INSTCSRRSMASK) == `INSTCSRRS)            ||
                    ((opcodei & `INSTCSRRCMASK) == `INSTCSRRC)            ||
                    ((opcodei & `INSTCSRRWIMASK) == `INSTCSRRWI)          ||
                    ((opcodei & `INSTCSRRSIMASK) == `INSTCSRRSI)          ||
                    ((opcodei & `INSTCSRRCIMASK) == `INSTCSRRCI)          ||
                    ((opcodei & `INSTWFIMASK) == `INSTWFI)                ||
                    ((opcodei & `INSTFENCEMASK) == `INSTFENCE)            ||
                    ((opcodei & `INSTIFENCEMASK) == `INSTIFENCE)          ||
                    ((opcodei & `INSTSFENCEMASK) == `INSTSFENCE)          ||
                    invalidw || fetchfaulti;

endmodule
`define ALUNONE                                4'b0000
`define ALUSHIFTL                              4'b0001
`define ALUSHIFTR                              4'b0010
`define ALUSHIFTRARITH                        4'b0011
`define ALUADD                                 4'b0100
`define ALUSUB                                 4'b0110
`define ALUAND                                 4'b0111
`define ALUOR                                  4'b1000
`define ALUXOR                                 4'b1001
`define ALULESSTHAN                           4'b1010
`define ALULESSTHANSIGNED                    4'b1011

`define INSTANDI 32'h7013
`define INSTANDIMASK 32'h707f

`define INSTADDI 32'h13
`define INSTADDIMASK 32'h707f

`define INSTSLTI 32'h2013
`define INSTSLTIMASK 32'h707f

`define INSTSLTIU 32'h3013
`define INSTSLTIUMASK 32'h707f

`define INSTORI 32'h6013
`define INSTORIMASK 32'h707f

`define INSTXORI 32'h4013
`define INSTXORIMASK 32'h707f

`define INSTSLLI 32'h1013
`define INSTSLLIMASK 32'hfc00707f

`define INSTSRLI 32'h5013
`define INSTSRLIMASK 32'hfc00707f

`define INSTSRAI 32'h40005013
`define INSTSRAIMASK 32'hfc00707f

`define INSTLUI 32'h37
`define INSTLUIMASK 32'h7f

`define INSTAUIPC 32'h17
`define INSTAUIPCMASK 32'h7f

`define INSTADD 32'h33
`define INSTADDMASK 32'hfe00707f

`define INSTSUB 32'h40000033
`define INSTSUBMASK 32'hfe00707f

`define INSTSLT 32'h2033
`define INSTSLTMASK 32'hfe00707f

`define INSTSLTU 32'h3033
`define INSTSLTUMASK 32'hfe00707f

`define INSTXOR 32'h4033
`define INSTXORMASK 32'hfe00707f

`define INSTOR 32'h6033
`define INSTORMASK 32'hfe00707f

`define INSTAND 32'h7033
`define INSTANDMASK 32'hfe00707f

`define INSTSLL 32'h1033
`define INSTSLLMASK 32'hfe00707f

`define INSTSRL 32'h5033
`define INSTSRLMASK 32'hfe00707f

`define INSTSRA 32'h40005033
`define INSTSRAMASK 32'hfe00707f

`define INSTJAL 32'h6f
`define INSTJALMASK 32'h7f

`define INSTJALR 32'h67
`define INSTJALRMASK 32'h707f

`define INSTBEQ 32'h63
`define INSTBEQMASK 32'h707f

`define INSTBNE 32'h1063
`define INSTBNEMASK 32'h707f

`define INSTBLT 32'h4063
`define INSTBLTMASK 32'h707f

`define INSTBGE 32'h5063
`define INSTBGEMASK 32'h707f

`define INSTBLTU 32'h6063
`define INSTBLTUMASK 32'h707f

`define INSTBGEU 32'h7063
`define INSTBGEUMASK 32'h707f

`define INSTLB 32'h3
`define INSTLBMASK 32'h707f

`define INSTLH 32'h1003
`define INSTLHMASK 32'h707f

`define INSTLW 32'h2003
`define INSTLWMASK 32'h707f

`define INSTLBU 32'h4003
`define INSTLBUMASK 32'h707f

`define INSTLHU 32'h5003
`define INSTLHUMASK 32'h707f

`define INSTLWU 32'h6003
`define INSTLWUMASK 32'h707f

`define INSTSB 32'h23
`define INSTSBMASK 32'h707f

`define INSTSH 32'h1023
`define INSTSHMASK 32'h707f

`define INSTSW 32'h2023
`define INSTSWMASK 32'h707f

`define INSTECALL 32'h73
`define INSTECALLMASK 32'hffffffff

`define INSTEBREAK 32'h100073
`define INSTEBREAKMASK 32'hffffffff

`define INSTERET 32'h200073
`define INSTERETMASK 32'hcfffffff

`define INSTCSRRW 32'h1073
`define INSTCSRRWMASK 32'h707f

`define INSTCSRRS 32'h2073
`define INSTCSRRSMASK 32'h707f

`define INSTCSRRC 32'h3073
`define INSTCSRRCMASK 32'h707f

`define INSTCSRRWI 32'h5073
`define INSTCSRRWIMASK 32'h707f

`define INSTCSRRSI 32'h6073
`define INSTCSRRSIMASK 32'h707f

`define INSTCSRRCI 32'h7073
`define INSTCSRRCIMASK 32'h707f

`define INSTMUL 32'h2000033
`define INSTMULMASK 32'hfe00707f

`define INSTMULH 32'h2001033
`define INSTMULHMASK 32'hfe00707f

`define INSTMULHSU 32'h2002033
`define INSTMULHSUMASK 32'hfe00707f

`define INSTMULHU 32'h2003033
`define INSTMULHUMASK 32'hfe00707f

`define INSTDIV 32'h2004033
`define INSTDIVMASK 32'hfe00707f

`define INSTDIVU 32'h2005033
`define INSTDIVUMASK 32'hfe00707f

`define INSTREM 32'h2006033
`define INSTREMMASK 32'hfe00707f

`define INSTREMU 32'h2007033
`define INSTREMUMASK 32'hfe00707f

`define INSTWFI 32'h10500073
`define INSTWFIMASK 32'hffff8fff

`define INSTFENCE 32'hf
`define INSTFENCEMASK 32'h707f

`define INSTSFENCE 32'h12000073
`define INSTSFENCEMASK 32'hfe007fff

`define INSTIFENCE 32'h100f
`define INSTIFENCEMASK 32'h707f

`define PRIVUSER         2'd0
`define PRIVSUPER        2'd1
`define PRIVMACHINE      2'd3

`define IRQSSOFT   1
`define IRQMSOFT   3
`define IRQSTIMER  5
`define IRQMTIMER  7
`define IRQSEXT    9
`define IRQMEXT    11
`define IRQMIN      (`IRQSSOFT)
`define IRQMAX      (`IRQMEXT + 1)
`define IRQMASK     ((1 << `IRQMEXT)   | (1 << `IRQSEXT)   |                       (1 << `IRQMTIMER) | (1 << `IRQSTIMER) |                       (1 << `IRQMSOFT)  | (1 << `IRQSSOFT))

`define SRIPMSIPR      `IRQMSOFT
`define SRIPMTIPR      `IRQMTIMER
`define SRIPMEIPR      `IRQMEXT
`define SRIPSSIPR      `IRQSSOFT
`define SRIPSTIPR      `IRQSTIMER
`define SRIPSEIPR      `IRQSEXT

`define CSRDSCRATCH       12'h7b2
`define CSRSIMCTRL       12'h8b2
`define CSRSIMCTRLMASK  32'hFFFFFFFF
    `define CSRSIMCTRLEXIT (0 << 24)
    `define CSRSIMCTRLPUTC (1 << 24)

`define CSRMSTATUS       12'h300
`define CSRMSTATUSMASK  32'hFFFFFFFF
`define CSRMISA          12'h301
`define CSRMISAMASK     32'hFFFFFFFF
    `define MISARV32     32'h40000000
    `define MISARVI      32'h00000100
    `define MISARVE      32'h00000010
    `define MISARVM      32'h00001000
    `define MISARVA      32'h00000001
    `define MISARVF      32'h00000020
    `define MISARVD      32'h00000008
    `define MISARVC      32'h00000004
    `define MISARVS      32'h00040000
    `define MISARVU      32'h00100000
`define CSRMEDELEG       12'h302
`define CSRMEDELEGMASK  32'h0000FFFF
`define CSRMIDELEG       12'h303
`define CSRMIDELEGMASK  32'h0000FFFF
`define CSRMIE           12'h304
`define CSRMIEMASK      `IRQMASK
`define CSRMTVEC         12'h305
`define CSRMTVECMASK    32'hFFFFFFFF
`define CSRMSCRATCH      12'h340
`define CSRMSCRATCHMASK 32'hFFFFFFFF
`define CSRMEPC          12'h341
`define CSRMEPCMASK     32'hFFFFFFFF
`define CSRMCAUSE        12'h342
`define CSRMCAUSEMASK   32'h8000000F
`define CSRMTVAL         12'h343
`define CSRMTVALMASK    32'hFFFFFFFF
`define CSRMIP           12'h344
`define CSRMIPMASK      `IRQMASK
`define CSRMCYCLE        12'hc00
`define CSRMCYCLEMASK   32'hFFFFFFFF
`define CSRMTIME         12'hc01
`define CSRMTIMEMASK    32'hFFFFFFFF
`define CSRMTIMEH        12'hc81
`define CSRMTIMEHMASK   32'hFFFFFFFF
`define CSRMHARTID       12'hF14
`define CSRMHARTIDMASK  32'hFFFFFFFF

`define CSRMTIMECMP        12'h7c0
`define CSRMTIMECMPMASK   32'hFFFFFFFF

`define CSRSSTATUS       12'h100
`define CSRSSTATUSMASK  `SRSMODEMASK
`define CSRSIE           12'h104
`define CSRSIEMASK      ((1 << `IRQSEXT) | (1 << `IRQSTIMER) | (1 << `IRQSSOFT))
`define CSRSTVEC         12'h105
`define CSRSTVECMASK    32'hFFFFFFFF
`define CSRSSCRATCH      12'h140
`define CSRSSCRATCHMASK 32'hFFFFFFFF
`define CSRSEPC          12'h141
`define CSRSEPCMASK     32'hFFFFFFFF
`define CSRSCAUSE        12'h142
`define CSRSCAUSEMASK   32'h8000000F
`define CSRSTVAL         12'h143
`define CSRSTVALMASK    32'hFFFFFFFF
`define CSRSIP           12'h144
`define CSRSIPMASK      ((1 << `IRQSEXT) | (1 << `IRQSTIMER) | (1 << `IRQSSOFT))
`define CSRSATP          12'h180
`define CSRSATPMASK     32'hFFFFFFFF

`define CSRDFLUSH            12'h3a0 
`define CSRDFLUSHMASK       32'hFFFFFFFF
`define CSRDWRITEBACK        12'h3a1 
`define CSRDWRITEBACKMASK   32'hFFFFFFFF
`define CSRDINVALIDATE       12'h3a2 
`define CSRDINVALIDATEMASK  32'hFFFFFFFF

`define SRUIE         (1 << 0)
`define SRUIER       0
`define SRSIE         (1 << 1)
`define SRSIER       1
`define SRMIE         (1 << 3)
`define SRMIER       3
`define SRUPIE        (1 << 4)
`define SRUPIER      4
`define SRSPIE        (1 << 5)
`define SRSPIER      5
`define SRMPIE        (1 << 7)
`define SRMPIER      7
`define SRSPP         (1 << 8)
`define SRSPPR       8

`define SRMPPSHIFT   11
`define SRMPPMASK    2'h3
`define SRMPPR       12:11
`define SRMPPU       `PRIVUSER
`define SRMPPS       `PRIVSUPER
`define SRMPPM       `PRIVMACHINE

`define SRSUMR        18
`define SRSUM          (1 << `SRSUMR)

`define SRMPRVR       17
`define SRMPRV         (1 << `SRMPRVR)

`define SRMXRR        19
`define SRMXR          (1 << `SRMXRR)

`define SRSMODEMASK   (`SRUIE | `SRSIE | `SRUPIE | `SRSPIE | `SRSPP | `SRSUM)

`define SATPPPNR        19:0 
`define SATPASIDR       30:22
`define SATPMODER       31

`define MMULEVELS        2
`define MMUPTIDXBITS     10
`define MMUPTESIZE       4
`define MMUPGSHIFT       (`MMUPTIDXBITS + 2)
`define MMUPGSIZE        (1 << `MMUPGSHIFT)
`define MMUVPNBITS      (`MMUPTIDXBITS * `MMULEVELS)
`define MMUPPNBITS      (32 - `MMUPGSHIFT)
`define MMUVABITS       (`MMUVPNBITS + `MMUPGSHIFT)

`define PAGEPRESENT      0
`define PAGEREAD         1
`define PAGEWRITE        2
`define PAGEEXEC         3
`define PAGEUSER         4
`define PAGEGLOBAL       5
`define PAGEACCESSED     6
`define PAGEDIRTY        7
`define PAGESOFT         9:8

`define PAGEFLAGS       10'h3FF

`define PAGEPFNSHIFT   10
`define PAGESIZE        4096

`define EXCEPTIONW                        6
`define EXCEPTIONMISALIGNEDFETCH         6'h10
`define EXCEPTIONFAULTFETCH              6'h11
`define EXCEPTIONILLEGALINSTRUCTION      6'h12
`define EXCEPTIONBREAKPOINT               6'h13
`define EXCEPTIONMISALIGNEDLOAD          6'h14
`define EXCEPTIONFAULTLOAD               6'h15
`define EXCEPTIONMISALIGNEDSTORE         6'h16
`define EXCEPTIONFAULTSTORE              6'h17
`define EXCEPTIONECALL                    6'h18
`define EXCEPTIONECALLU                  6'h18
`define EXCEPTIONECALLS                  6'h19
`define EXCEPTIONECALLH                  6'h1a
`define EXCEPTIONECALLM                  6'h1b
`define EXCEPTIONPAGEFAULTINST          6'h1c
`define EXCEPTIONPAGEFAULTLOAD          6'h1d
`define EXCEPTIONPAGEFAULTSTORE         6'h1f
`define EXCEPTIONEXCEPTION                6'h10
`define EXCEPTIONINTERRUPT                6'h20
`define EXCEPTIONERETU                   6'h30
`define EXCEPTIONERETS                   6'h31
`define EXCEPTIONERETH                   6'h32
`define EXCEPTIONERETM                   6'h33
`define EXCEPTIONFENCE                    6'h34
`define EXCEPTIONTYPEMASK                6'h30
`define EXCEPTIONSUBTYPER                3:0

`define MCAUSEINT                      31
`define MCAUSEMISALIGNEDFETCH         ((0 << `MCAUSEINT) | 0)
`define MCAUSEFAULTFETCH              ((0 << `MCAUSEINT) | 1)
`define MCAUSEILLEGALINSTRUCTION      ((0 << `MCAUSEINT) | 2)
`define MCAUSEBREAKPOINT               ((0 << `MCAUSEINT) | 3)
`define MCAUSEMISALIGNEDLOAD          ((0 << `MCAUSEINT) | 4)
`define MCAUSEFAULTLOAD               ((0 << `MCAUSEINT) | 5)
`define MCAUSEMISALIGNEDSTORE         ((0 << `MCAUSEINT) | 6)
`define MCAUSEFAULTSTORE              ((0 << `MCAUSEINT) | 7)
`define MCAUSEECALLU                  ((0 << `MCAUSEINT) | 8)
`define MCAUSEECALLS                  ((0 << `MCAUSEINT) | 9)
`define MCAUSEECALLH                  ((0 << `MCAUSEINT) | 10)
`define MCAUSEECALLM                  ((0 << `MCAUSEINT) | 11)
`define MCAUSEPAGEFAULTINST          ((0 << `MCAUSEINT) | 12)
`define MCAUSEPAGEFAULTLOAD          ((0 << `MCAUSEINT) | 13)
`define MCAUSEPAGEFAULTSTORE         ((0 << `MCAUSEINT) | 15)
`define MCAUSEINTERRUPT                (1 << `MCAUSEINT)

`define RISCVREGNOFIRST   13'd0
`define RISCVREGNOGPR0    13'd0
`define RISCVREGNOGPR31   13'd31
`define RISCVREGNOPC      13'd32
`define RISCVREGNOCSR0    13'd65
`define RISCVREGNOCSR4095 (`RISCVREGNOCSR0 +  13'd4095)
`define RISCVREGNOPRIV    13'd4161

module riscvdivider
(
    
     input           clki
    ,input           rsti
    ,input           opcodevalidi
    ,input  [ 31:0]  opcodeopcodei
    ,input  [ 31:0]  opcodepci
    ,input           opcodeinvalidi
    ,input  [  4:0]  opcoderdidxi
    ,input  [  4:0]  opcoderaidxi
    ,input  [  4:0]  opcoderbidxi
    ,input  [ 31:0]  opcoderaoperandi
    ,input  [ 31:0]  opcoderboperandi

    
    ,output          writebackvalido
    ,output [ 31:0]  writebackvalueo
);



`include "riscvdefs.v"

reg          validq;
reg  [31:0]  wbresultq;

wire instdivw         = (opcodeopcodei & `INSTDIVMASK) == `INSTDIV;
wire instdivuw        = (opcodeopcodei & `INSTDIVUMASK) == `INSTDIVU;
wire instremw         = (opcodeopcodei & `INSTREMMASK) == `INSTREM;
wire instremuw        = (opcodeopcodei & `INSTREMUMASK) == `INSTREMU;

wire divreminstw     = ((opcodeopcodei & `INSTDIVMASK) == `INSTDIV)  || 
                          ((opcodeopcodei & `INSTDIVUMASK) == `INSTDIVU) ||
                          ((opcodeopcodei & `INSTREMMASK) == `INSTREM)  ||
                          ((opcodeopcodei & `INSTREMUMASK) == `INSTREMU);

wire signedoperationw = ((opcodeopcodei & `INSTDIVMASK) == `INSTDIV) || ((opcodeopcodei & `INSTREMMASK) == `INSTREM);
wire divoperationw    = ((opcodeopcodei & `INSTDIVMASK) == `INSTDIV) || ((opcodeopcodei & `INSTDIVUMASK) == `INSTDIVU);

reg [31:0] dividendq;
reg [62:0] divisorq;
reg [31:0] quotientq;
reg [31:0] qmaskq;
reg        divinstq;
reg        divbusyq;
reg        invertresq;

wire divstartw    = opcodevalidi & divreminstw;
wire divcompletew = !(|qmaskq) & divbusyq;

always @(posedge clki or posedge rsti)
if (rsti)
begin
    divbusyq     <= 1'b0;
    dividendq     <= 32'b0;
    divisorq      <= 63'b0;
    invertresq   <= 1'b0;
    quotientq     <= 32'b0;
    qmaskq       <= 32'b0;
    divinstq     <= 1'b0;
end
else if (divstartw)
begin

    divbusyq     <= 1'b1;
    divinstq     <= divoperationw;

    if (signedoperationw && opcoderaoperandi[31])
        dividendq <= -opcoderaoperandi;
    else
        dividendq <= opcoderaoperandi;

    if (signedoperationw && opcoderboperandi[31])
        divisorq <= {-opcoderboperandi, 31'b0};
    else
        divisorq <= {opcoderboperandi, 31'b0};

    invertresq  <= (((opcodeopcodei & `INSTDIVMASK) == `INSTDIV) && (opcoderaoperandi[31] != opcoderboperandi[31]) && |opcoderboperandi) || 
                     (((opcodeopcodei & `INSTREMMASK) == `INSTREM) && opcoderaoperandi[31]);

    quotientq     <= 32'b0;
    qmaskq       <= 32'h80000000;
end
else if (divcompletew)
begin
    divbusyq <= 1'b0;
end
else if (divbusyq)
begin
    if (divisorq <= {31'b0, dividendq})
    begin
        dividendq <= dividendq - divisorq[31:0];
        quotientq <= quotientq | qmaskq;
    end

    divisorq <= {1'b0, divisorq[62:1]};
    qmaskq  <= {1'b0, qmaskq[31:1]};
end

reg [31:0] divresultr;
always @ *
begin
    divresultr = 32'b0;

    if (divinstq)
        divresultr = invertresq ? -quotientq : quotientq;
    else
        divresultr = invertresq ? -dividendq : dividendq;
end

always @(posedge clki or posedge rsti)
if (rsti)
    validq <= 1'b0;
else
    validq <= divcompletew;

always @(posedge clki or posedge rsti)
if (rsti)
    wbresultq <= 32'b0;
else if (divcompletew)
    wbresultq <= divresultr;

assign writebackvalido = validq;
assign writebackvalueo  = wbresultq;



endmodule

module riscvexec
(
    
     input           clki
    ,input           rsti
    ,input           opcodevalidi
    ,input  [ 31:0]  opcodeopcodei
    ,input  [ 31:0]  opcodepci
    ,input           opcodeinvalidi
    ,input  [  4:0]  opcoderdidxi
    ,input  [  4:0]  opcoderaidxi
    ,input  [  4:0]  opcoderbidxi
    ,input  [ 31:0]  opcoderaoperandi
    ,input  [ 31:0]  opcoderboperandi
    ,input           holdi

    
    ,output          branchrequesto
    ,output          branchistakeno
    ,output          branchisnottakeno
    ,output [ 31:0]  branchsourceo
    ,output          branchiscallo
    ,output          branchisreto
    ,output          branchisjmpo
    ,output [ 31:0]  branchpco
    ,output          branchdrequesto
    ,output [ 31:0]  branchdpco
    ,output [  1:0]  branchdprivo
    ,output [ 31:0]  writebackvalueo
);



`include "riscvdefs.v"

reg [31:0]  imm20r;
reg [31:0]  imm12r;
reg [31:0]  bimmr;
reg [31:0]  jimm20r;
reg [4:0]   shamtr;

always @ *
begin
    imm20r     = {opcodeopcodei[31:12], 12'b0};
    imm12r     = {{20{opcodeopcodei[31]}}, opcodeopcodei[31:20]};
    bimmr      = {{19{opcodeopcodei[31]}}, opcodeopcodei[31], opcodeopcodei[7], opcodeopcodei[30:25], opcodeopcodei[11:8], 1'b0};
    jimm20r    = {{12{opcodeopcodei[31]}}, opcodeopcodei[19:12], opcodeopcodei[20], opcodeopcodei[30:25], opcodeopcodei[24:21], 1'b0};
    shamtr     = opcodeopcodei[24:20];
end

reg [3:0]  alufuncr;
reg [31:0] aluinputar;
reg [31:0] aluinputbr;

always @ *
begin
    alufuncr     = `ALUNONE;
    aluinputar  = 32'b0;
    aluinputbr  = 32'b0;

    if ((opcodeopcodei & `INSTADDMASK) == `INSTADD) 
    begin
        alufuncr     = `ALUADD;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = opcoderboperandi;
    end
    else if ((opcodeopcodei & `INSTANDMASK) == `INSTAND) 
    begin
        alufuncr     = `ALUAND;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = opcoderboperandi;
    end
    else if ((opcodeopcodei & `INSTORMASK) == `INSTOR) 
    begin
        alufuncr     = `ALUOR;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = opcoderboperandi;
    end
    else if ((opcodeopcodei & `INSTSLLMASK) == `INSTSLL) 
    begin
        alufuncr     = `ALUSHIFTL;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = opcoderboperandi;
    end
    else if ((opcodeopcodei & `INSTSRAMASK) == `INSTSRA) 
    begin
        alufuncr     = `ALUSHIFTRARITH;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = opcoderboperandi;
    end
    else if ((opcodeopcodei & `INSTSRLMASK) == `INSTSRL) 
    begin
        alufuncr     = `ALUSHIFTR;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = opcoderboperandi;
    end
    else if ((opcodeopcodei & `INSTSUBMASK) == `INSTSUB) 
    begin
        alufuncr     = `ALUSUB;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = opcoderboperandi;
    end
    else if ((opcodeopcodei & `INSTXORMASK) == `INSTXOR) 
    begin
        alufuncr     = `ALUXOR;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = opcoderboperandi;
    end
    else if ((opcodeopcodei & `INSTSLTMASK) == `INSTSLT) 
    begin
        alufuncr     = `ALULESSTHANSIGNED;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = opcoderboperandi;
    end
    else if ((opcodeopcodei & `INSTSLTUMASK) == `INSTSLTU) 
    begin
        alufuncr     = `ALULESSTHAN;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = opcoderboperandi;
    end
    else if ((opcodeopcodei & `INSTADDIMASK) == `INSTADDI) 
    begin
        alufuncr     = `ALUADD;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = imm12r;
    end
    else if ((opcodeopcodei & `INSTANDIMASK) == `INSTANDI) 
    begin
        alufuncr     = `ALUAND;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = imm12r;
    end
    else if ((opcodeopcodei & `INSTSLTIMASK) == `INSTSLTI) 
    begin
        alufuncr     = `ALULESSTHANSIGNED;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = imm12r;
    end
    else if ((opcodeopcodei & `INSTSLTIUMASK) == `INSTSLTIU) 
    begin
        alufuncr     = `ALULESSTHAN;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = imm12r;
    end
    else if ((opcodeopcodei & `INSTORIMASK) == `INSTORI) 
    begin
        alufuncr     = `ALUOR;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = imm12r;
    end
    else if ((opcodeopcodei & `INSTXORIMASK) == `INSTXORI) 
    begin
        alufuncr     = `ALUXOR;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = imm12r;
    end
    else if ((opcodeopcodei & `INSTSLLIMASK) == `INSTSLLI) 
    begin
        alufuncr     = `ALUSHIFTL;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = {27'b0, shamtr};
    end
    else if ((opcodeopcodei & `INSTSRLIMASK) == `INSTSRLI) 
    begin
        alufuncr     = `ALUSHIFTR;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = {27'b0, shamtr};
    end
    else if ((opcodeopcodei & `INSTSRAIMASK) == `INSTSRAI) 
    begin
        alufuncr     = `ALUSHIFTRARITH;
        aluinputar  = opcoderaoperandi;
        aluinputbr  = {27'b0, shamtr};
    end
    else if ((opcodeopcodei & `INSTLUIMASK) == `INSTLUI) 
    begin
        aluinputar  = imm20r;
    end
    else if ((opcodeopcodei & `INSTAUIPCMASK) == `INSTAUIPC) 
    begin
        alufuncr     = `ALUADD;
        aluinputar  = opcodepci;
        aluinputbr  = imm20r;
    end     
    else if (((opcodeopcodei & `INSTJALMASK) == `INSTJAL) || ((opcodeopcodei & `INSTJALRMASK) == `INSTJALR)) 
    begin
        alufuncr     = `ALUADD;
        aluinputar  = opcodepci;
        aluinputbr  = 32'd4;
    end
end


wire [31:0]  alupw;
riscvalu
ualu
(
    .aluopi(alufuncr),
    .aluai(aluinputar),
    .alubi(aluinputbr),
    .alupo(alupw)
);

reg [31:0] resultq;
always @ (posedge clki or posedge rsti)
if (rsti)
    resultq  <= 32'b0;
else if (~holdi)
    resultq <= alupw;

assign writebackvalueo  = resultq;

function [0:0] lessthansigned;
    input  [31:0] x;
    input  [31:0] y;
    reg [31:0] v;
begin
    v = (x - y);
    if (x[31] != y[31])
        lessthansigned = x[31];
    else
        lessthansigned = v[31];
end
endfunction

function [0:0] greaterthansigned;
    input  [31:0] x;
    input  [31:0] y;
    reg [31:0] v;
begin
    v = (y - x);
    if (x[31] != y[31])
        greaterthansigned = y[31];
    else
        greaterthansigned = v[31];
end
endfunction

reg        branchr;
reg        branchtakenr;
reg [31:0] branchtargetr;
reg        branchcallr;
reg        branchretr;
reg        branchjmpr;

always @ *
begin
    branchr        = 1'b0;
    branchtakenr  = 1'b0;
    branchcallr   = 1'b0;
    branchretr    = 1'b0;
    branchjmpr    = 1'b0;

    
    branchtargetr = opcodepci + bimmr;

    if ((opcodeopcodei & `INSTJALMASK) == `INSTJAL) 
    begin
        branchr        = 1'b1;
        branchtakenr  = 1'b1;
        branchtargetr = opcodepci + jimm20r;
        branchcallr   = (opcoderdidxi == 5'd1); 
        branchjmpr    = 1'b1;
    end
    else if ((opcodeopcodei & `INSTJALRMASK) == `INSTJALR) 
    begin
        branchr            = 1'b1;
        branchtakenr      = 1'b1;
        branchtargetr     = opcoderaoperandi + imm12r;
        branchtargetr[0]  = 1'b0;
        branchretr        = (opcoderaidxi == 5'd1 && imm12r[11:0] == 12'b0); 
        branchcallr       = ~branchretr && (opcoderdidxi == 5'd1); 
        branchjmpr        = ~(branchcallr | branchretr);
    end
    else if ((opcodeopcodei & `INSTBEQMASK) == `INSTBEQ) 
    begin
        branchr      = 1'b1;
        branchtakenr= (opcoderaoperandi == opcoderboperandi);
    end
    else if ((opcodeopcodei & `INSTBNEMASK) == `INSTBNE) 
    begin
        branchr      = 1'b1;    
        branchtakenr= (opcoderaoperandi != opcoderboperandi);
    end
    else if ((opcodeopcodei & `INSTBLTMASK) == `INSTBLT) 
    begin
        branchr      = 1'b1;
        branchtakenr= lessthansigned(opcoderaoperandi, opcoderboperandi);
    end
    else if ((opcodeopcodei & `INSTBGEMASK) == `INSTBGE) 
    begin
        branchr      = 1'b1;    
        branchtakenr= greaterthansigned(opcoderaoperandi,opcoderboperandi) | (opcoderaoperandi == opcoderboperandi);
    end
    else if ((opcodeopcodei & `INSTBLTUMASK) == `INSTBLTU) 
    begin
        branchr      = 1'b1;    
        branchtakenr= (opcoderaoperandi < opcoderboperandi);
    end
    else if ((opcodeopcodei & `INSTBGEUMASK) == `INSTBGEU) 
    begin
        branchr      = 1'b1;
        branchtakenr= (opcoderaoperandi >= opcoderboperandi);
    end
end

reg        branchtakenq;
reg        branchntakenq;
reg [31:0] pcxq;
reg [31:0] pcmq;
reg        branchcallq;
reg        branchretq;
reg        branchjmpq;

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    branchtakenq   <= 1'b0;
    branchntakenq  <= 1'b0;
    pcxq           <= 32'b0;
    pcmq           <= 32'b0;
    branchcallq    <= 1'b0;
    branchretq     <= 1'b0;
    branchjmpq     <= 1'b0;
end
else if (opcodevalidi)
begin
    branchtakenq   <= branchr && opcodevalidi & branchtakenr;
    branchntakenq  <= branchr && opcodevalidi & ~branchtakenr;
    pcxq           <= branchtakenr ? branchtargetr : opcodepci + 32'd4;
    branchcallq    <= branchr && opcodevalidi && branchcallr;
    branchretq     <= branchr && opcodevalidi && branchretr;
    branchjmpq     <= branchr && opcodevalidi && branchjmpr;
    pcmq           <= opcodepci;
end

assign branchrequesto   = branchtakenq | branchntakenq;
assign branchistakeno  = branchtakenq;
assign branchisnottakeno = branchntakenq;
assign branchsourceo    = pcmq;
assign branchpco        = pcxq;
assign branchiscallo   = branchcallq;
assign branchisreto    = branchretq;
assign branchisjmpo    = branchjmpq;

assign branchdrequesto = (branchr && opcodevalidi && branchtakenr);
assign branchdpco      = branchtargetr;
assign branchdprivo    = 2'b0; 



endmodule

module riscvfetch
#(
     parameter SUPPORTMMU      = 1
)
(
    
     input           clki
    ,input           rsti
    ,input           fetchaccepti
    ,input           icacheaccepti
    ,input           icachevalidi
    ,input           icacheerrori
    ,input  [ 31:0]  icacheinsti
    ,input           icachepagefaulti
    ,input           fetchinvalidatei
    ,input           branchrequesti
    ,input  [ 31:0]  branchpci
    ,input  [  1:0]  branchprivi

    
    ,output          fetchvalido
    ,output [ 31:0]  fetchinstro
    ,output [ 31:0]  fetchpco
    ,output          fetchfaultfetcho
    ,output          fetchfaultpageo
    ,output          icacherdo
    ,output          icacheflusho
    ,output          icacheinvalidateo
    ,output [ 31:0]  icachepco
    ,output [  1:0]  icacheprivo
    ,output          squashdecodeo
);



`include "riscvdefs.v"

reg         activeq;

wire        icachebusyw;
wire        stallw       = !fetchaccepti || icachebusyw || !icacheaccepti;

reg         branchq;
reg [31:0]  branchpcq;
reg [1:0]   branchprivq;

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    branchq       <= 1'b0;
    branchpcq    <= 32'b0;
    branchprivq  <= `PRIVMACHINE;
end
else if (branchrequesti)
begin
    branchq       <= 1'b1;
    branchpcq    <= branchpci;
    branchprivq  <= branchprivi;
end
else if (icacherdo && icacheaccepti)
begin
    branchq       <= 1'b0;
    branchpcq    <= 32'b0;
end

wire        branchw      = branchq;
wire [31:0] branchpcw   = branchpcq;
wire [1:0]  branchprivw = branchprivq;

assign squashdecodeo    = branchrequesti;

always @ (posedge clki or posedge rsti)
if (rsti)
    activeq    <= 1'b0;
else if (branchw && ~stallw)
    activeq    <= 1'b1;

reg stallq;

always @ (posedge clki or posedge rsti)
if (rsti)
    stallq    <= 1'b0;
else
    stallq    <= stallw;

reg icachefetchq;
reg icacheinvalidateq;

always @ (posedge clki or posedge rsti)
if (rsti)
    icachefetchq <= 1'b0;
else if (icacherdo && icacheaccepti)
    icachefetchq <= 1'b1;
else if (icachevalidi)
    icachefetchq <= 1'b0;

always @ (posedge clki or posedge rsti)
if (rsti)
    icacheinvalidateq <= 1'b0;
else if (icacheinvalidateo && !icacheaccepti)
    icacheinvalidateq <= 1'b1;
else
    icacheinvalidateq <= 1'b0;

reg [31:0]  pcfq;
reg [31:0]  pcdq;

wire [31:0] icachepcw;
wire [1:0]  icacheprivw;
wire        fetchrespdropw;

always @ (posedge clki or posedge rsti)
if (rsti)
    pcfq  <= 32'b0;
else if (branchw && ~stallw)
    pcfq  <= branchpcw;
else if (!stallw)
    pcfq  <= {icachepcw[31:2],2'b0} + 32'd4;

reg [1:0] privfq;
reg       branchdq;

always @ (posedge clki or posedge rsti)
if (rsti)
    privfq  <= `PRIVMACHINE;
else if (branchw && ~stallw)
    privfq  <= branchprivw;

always @ (posedge clki or posedge rsti)
if (rsti)
    branchdq  <= 1'b0;
else if (branchw && ~stallw)
    branchdq  <= 1'b1;
else if (!stallw)
    branchdq  <= 1'b0;

assign icachepcw       = pcfq;
assign icacheprivw     = privfq;
assign fetchrespdropw = branchw | branchdq;

always @ (posedge clki or posedge rsti)
if (rsti)
    pcdq <= 32'b0;
else if (icacherdo && icacheaccepti)
    pcdq <= icachepcw;

assign icacherdo         = activeq & fetchaccepti & !icachebusyw;
assign icachepco         = {icachepcw[31:2],2'b0};
assign icacheprivo       = icacheprivw;
assign icacheflusho      = fetchinvalidatei | icacheinvalidateq;
assign icacheinvalidateo = 1'b0;

assign icachebusyw       =  icachefetchq && !icachevalidi;

reg [65:0]  skidbufferq;
reg         skidvalidq;

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    skidbufferq  <= 66'b0;
    skidvalidq   <= 1'b0;
end 
else if (fetchvalido && !fetchaccepti)
begin
    skidvalidq  <= 1'b1;
    skidbufferq <= {fetchfaultpageo, fetchfaultfetcho, fetchpco, fetchinstro};
end
else
begin
    skidvalidq  <= 1'b0;
    skidbufferq <= 66'b0;
end

assign fetchvalido       = (icachevalidi || skidvalidq) & !fetchrespdropw;
assign fetchpco          = skidvalidq ? skidbufferq[63:32] : {pcdq[31:2],2'b0};
assign fetchinstro       = skidvalidq ? skidbufferq[31:0]  : icacheinsti;

assign fetchfaultfetcho = skidvalidq ? skidbufferq[64] : icacheerrori;
assign fetchfaultpageo  = skidvalidq ? skidbufferq[65] : icachepagefaulti;



endmodule

module riscvissue
#(
     parameter SUPPORTMULDIV   = 1
    ,parameter SUPPORTDUALISSUE = 1
    ,parameter SUPPORTLOADBYPASS = 1
    ,parameter SUPPORTMULBYPASS = 1
    ,parameter SUPPORTREGFILEXILINX = 0
)
(
    
     input           clki
    ,input           rsti
    ,input           fetchvalidi
    ,input  [ 31:0]  fetchinstri
    ,input  [ 31:0]  fetchpci
    ,input           fetchfaultfetchi
    ,input           fetchfaultpagei
    ,input           fetchinstrexeci
    ,input           fetchinstrlsui
    ,input           fetchinstrbranchi
    ,input           fetchinstrmuli
    ,input           fetchinstrdivi
    ,input           fetchinstrcsri
    ,input           fetchinstrrdvalidi
    ,input           fetchinstrinvalidi
    ,input           branchexecrequesti
    ,input           branchexecistakeni
    ,input           branchexecisnottakeni
    ,input  [ 31:0]  branchexecsourcei
    ,input           branchexeciscalli
    ,input           branchexecisreti
    ,input           branchexecisjmpi
    ,input  [ 31:0]  branchexecpci
    ,input           branchdexecrequesti
    ,input  [ 31:0]  branchdexecpci
    ,input  [  1:0]  branchdexecprivi
    ,input           branchcsrrequesti
    ,input  [ 31:0]  branchcsrpci
    ,input  [  1:0]  branchcsrprivi
    ,input  [ 31:0]  writebackexecvaluei
    ,input           writebackmemvalidi
    ,input  [ 31:0]  writebackmemvaluei
    ,input  [  5:0]  writebackmemexceptioni
    ,input  [ 31:0]  writebackmulvaluei
    ,input           writebackdivvalidi
    ,input  [ 31:0]  writebackdivvaluei
    ,input  [ 31:0]  csrresulte1valuei
    ,input           csrresulte1writei
    ,input  [ 31:0]  csrresulte1wdatai
    ,input  [  5:0]  csrresulte1exceptioni
    ,input           lsustalli
    ,input           takeinterrupti

    
    ,output          fetchaccepto
    ,output          branchrequesto
    ,output [ 31:0]  branchpco
    ,output [  1:0]  branchprivo
    ,output          execopcodevalido
    ,output          lsuopcodevalido
    ,output          csropcodevalido
    ,output          mulopcodevalido
    ,output          divopcodevalido
    ,output [ 31:0]  opcodeopcodeo
    ,output [ 31:0]  opcodepco
    ,output          opcodeinvalido
    ,output [  4:0]  opcoderdidxo
    ,output [  4:0]  opcoderaidxo
    ,output [  4:0]  opcoderbidxo
    ,output [ 31:0]  opcoderaoperando
    ,output [ 31:0]  opcoderboperando
    ,output [ 31:0]  lsuopcodeopcodeo
    ,output [ 31:0]  lsuopcodepco
    ,output          lsuopcodeinvalido
    ,output [  4:0]  lsuopcoderdidxo
    ,output [  4:0]  lsuopcoderaidxo
    ,output [  4:0]  lsuopcoderbidxo
    ,output [ 31:0]  lsuopcoderaoperando
    ,output [ 31:0]  lsuopcoderboperando
    ,output [ 31:0]  mulopcodeopcodeo
    ,output [ 31:0]  mulopcodepco
    ,output          mulopcodeinvalido
    ,output [  4:0]  mulopcoderdidxo
    ,output [  4:0]  mulopcoderaidxo
    ,output [  4:0]  mulopcoderbidxo
    ,output [ 31:0]  mulopcoderaoperando
    ,output [ 31:0]  mulopcoderboperando
    ,output [ 31:0]  csropcodeopcodeo
    ,output [ 31:0]  csropcodepco
    ,output          csropcodeinvalido
    ,output [  4:0]  csropcoderdidxo
    ,output [  4:0]  csropcoderaidxo
    ,output [  4:0]  csropcoderbidxo
    ,output [ 31:0]  csropcoderaoperando
    ,output [ 31:0]  csropcoderboperando
    ,output          csrwritebackwriteo
    ,output [ 11:0]  csrwritebackwaddro
    ,output [ 31:0]  csrwritebackwdatao
    ,output [  5:0]  csrwritebackexceptiono
    ,output [ 31:0]  csrwritebackexceptionpco
    ,output [ 31:0]  csrwritebackexceptionaddro
    ,output          execholdo
    ,output          mulholdo
    ,output          interruptinhibito
);



`include "riscvdefs.v"

wire enablemuldivw     = SUPPORTMULDIV;
wire enablemulbypassw = SUPPORTMULBYPASS;

wire stallw;
wire squashw;

reg [1:0] privxq;

always @ (posedge clki or posedge rsti)
if (rsti)
    privxq <= `PRIVMACHINE;
else if (branchcsrrequesti)
    privxq <= branchcsrprivi;

wire opcodevalidw = fetchvalidi & ~squashw & ~branchcsrrequesti;

assign branchrequesto     = branchcsrrequesti | branchdexecrequesti;
assign branchpco          = branchcsrrequesti ? branchcsrpci   : branchdexecpci;
assign branchprivo        = branchcsrrequesti ? branchcsrprivi : privxq;

wire [4:0] issueraidxw   = fetchinstri[19:15];
wire [4:0] issuerbidxw   = fetchinstri[24:20];
wire [4:0] issuerdidxw   = fetchinstri[11:7];
wire       issuesballocw = fetchinstrrdvalidi;
wire       issueexecw     = fetchinstrexeci;
wire       issuelsuw      = fetchinstrlsui;
wire       issuebranchw   = fetchinstrbranchi;
wire       issuemulw      = fetchinstrmuli;
wire       issuedivw      = fetchinstrdivi;
wire       issuecsrw      = fetchinstrcsri;
wire       issueinvalidw  = fetchinstrinvalidi;

wire        pipesquashe1e2w;

reg         opcodeissuer;
reg         opcodeacceptr;
wire        pipestallraww;

wire        pipeloade1w;
wire        pipestoree1w;
wire        pipemule1w;
wire        pipebranche1w;
wire [4:0]  piperde1w;

wire [31:0] pipepce1w;
wire [31:0] pipeopcodee1w;
wire [31:0] pipeoperandrae1w;
wire [31:0] pipeoperandrbe1w;

wire        pipeloade2w;
wire        pipemule2w;
wire [4:0]  piperde2w;
wire [31:0] piperesulte2w;

wire        pipevalidwbw;
wire        pipecsrwbw;
wire [4:0]  piperdwbw;
wire [31:0] piperesultwbw;
wire [31:0] pipepcwbw;
wire [31:0] pipeopcwbw;
wire [31:0] piperavalwbw;
wire [31:0] piperbvalwbw;
wire [`EXCEPTIONW-1:0] pipeexceptionwbw;

wire [`EXCEPTIONW-1:0] issuefaultw = fetchfaultfetchi ? `EXCEPTIONFAULTFETCH:
                                        fetchfaultpagei  ? `EXCEPTIONPAGEFAULTINST: `EXCEPTIONW'b0;

riscvpipectrl
#( 
     .SUPPORTLOADBYPASS(SUPPORTLOADBYPASS)
    ,.SUPPORTMULBYPASS(SUPPORTMULBYPASS)
)
upipectrl
(
     .clki(clki)
    ,.rsti(rsti)    

    
    ,.issuevalidi(opcodeissuer)
    ,.issueaccepti(opcodeacceptr)
    ,.issuestalli(stallw)
    ,.issuelsui(issuelsuw)
    ,.issuecsri(issuecsrw)
    ,.issuedivi(issuedivw)
    ,.issuemuli(issuemulw)
    ,.issuebranchi(issuebranchw)
    ,.issuerdvalidi(issuesballocw)
    ,.issuerdi(issuerdidxw)
    ,.issueexceptioni(issuefaultw)
    ,.issuepci(opcodepco)
    ,.issueopcodei(opcodeopcodeo)
    ,.issueoperandrai(opcoderaoperando)
    ,.issueoperandrbi(opcoderboperando)
    ,.issuebranchtakeni(branchdexecrequesti)
    ,.issuebranchtargeti(branchdexecpci)
    ,.takeinterrupti(takeinterrupti)

    
    ,.aluresulte1i(writebackexecvaluei)
    ,.csrresultvaluee1i(csrresulte1valuei)
    ,.csrresultwritee1i(csrresulte1writei)
    ,.csrresultwdatae1i(csrresulte1wdatai)
    ,.csrresultexceptione1i(csrresulte1exceptioni)

    
    ,.loade1o(pipeloade1w)
    ,.storee1o(pipestoree1w)
    ,.mule1o(pipemule1w)
    ,.branche1o(pipebranche1w)
    ,.rde1o(piperde1w)
    ,.pce1o(pipepce1w)
    ,.opcodee1o(pipeopcodee1w)
    ,.operandrae1o(pipeoperandrae1w)
    ,.operandrbe1o(pipeoperandrbe1w)

    
    ,.memcompletei(writebackmemvalidi)
    ,.memresulte2i(writebackmemvaluei)
    ,.memexceptione2i(writebackmemexceptioni)
    ,.mulresulte2i(writebackmulvaluei)

    
    ,.loade2o(pipeloade2w)
    ,.mule2o(pipemule2w)
    ,.rde2o(piperde2w)
    ,.resulte2o(piperesulte2w)

    ,.stallo(pipestallraww)
    ,.squashe1e2o(pipesquashe1e2w)
    ,.squashe1e2i(1'b0)
    ,.squashwbi(1'b0)

    
    ,.divcompletei(writebackdivvalidi)
    ,.divresulti(writebackdivvaluei)

    
    ,.validwbo(pipevalidwbw)
    ,.csrwbo(pipecsrwbw)
    ,.rdwbo(piperdwbw)
    ,.resultwbo(piperesultwbw)
    ,.pcwbo(pipepcwbw)
    ,.opcodewbo(pipeopcwbw)
    ,.operandrawbo(piperavalwbw)
    ,.operandrbwbo(piperbvalwbw)
    ,.exceptionwbo(pipeexceptionwbw)
    ,.csrwritewbo(csrwritebackwriteo)
    ,.csrwaddrwbo(csrwritebackwaddro)
    ,.csrwdatawbo(csrwritebackwdatao)   
);

assign execholdo = stallw;
assign mulholdo  = stallw;

assign csrwritebackexceptiono      = pipeexceptionwbw;
assign csrwritebackexceptionpco   = pipepcwbw;
assign csrwritebackexceptionaddro = piperesultwbw;

reg divpendingq;
reg csrpendingq;

always @ (posedge clki or posedge rsti)
if (rsti)
    divpendingq <= 1'b0;
else if (pipesquashe1e2w)
    divpendingq <= 1'b0;
else if (divopcodevalido && issuedivw)
    divpendingq <= 1'b1;
else if (writebackdivvalidi)
    divpendingq <= 1'b0;

always @ (posedge clki or posedge rsti)
if (rsti)
    csrpendingq <= 1'b0;
else if (pipesquashe1e2w)
    csrpendingq <= 1'b0;
else if (csropcodevalido && issuecsrw)
    csrpendingq <= 1'b1;
else if (pipecsrwbw)
    csrpendingq <= 1'b0;

assign squashw = pipesquashe1e2w;

reg [31:0] scoreboardr;

always @ *
begin
    opcodeissuer     = 1'b0;
    opcodeacceptr    = 1'b0;
    scoreboardr       = 32'b0;

    
    if (SUPPORTLOADBYPASS == 0)
    begin
        if (pipeloade2w)
            scoreboardr[piperde2w] = 1'b1;
    end
    if (SUPPORTMULBYPASS == 0)
    begin
        if (pipemule2w)
            scoreboardr[piperde2w] = 1'b1;
    end

    
    if (pipeloade1w || pipemule1w)
        scoreboardr[piperde1w] = 1'b1;

    
    if ((pipeloade1w || pipestoree1w) && (issuemulw || issuedivw || issuecsrw))
        scoreboardr = 32'hFFFFFFFF;

    
    if (lsustalli || stallw || divpendingq || csrpendingq)
        ;
    
    else if (opcodevalidw &&
        !(scoreboardr[issueraidxw] || 
          scoreboardr[issuerbidxw] ||
          scoreboardr[issuerdidxw]))
    begin
        opcodeissuer  = 1'b1;
        opcodeacceptr = 1'b1;

        if (opcodeacceptr && issuesballocw && (|issuerdidxw))
            scoreboardr[issuerdidxw] = 1'b1;
    end 
end

assign lsuopcodevalido   = opcodeissuer & ~takeinterrupti;
assign execopcodevalido  = opcodeissuer;
assign mulopcodevalido   = enablemuldivw & opcodeissuer;
assign divopcodevalido   = enablemuldivw & opcodeissuer;
assign interruptinhibito  = csrpendingq || issuecsrw;

assign fetchaccepto       = opcodevalidw ? (opcodeacceptr & ~takeinterrupti) : 1'b1;

assign stallw              = pipestallraww;

wire [31:0] issueravaluew;
wire [31:0] issuerbvaluew;
wire [31:0] issuebravaluew;
wire [31:0] issuebrbvaluew;

riscvregfile
#(
     .SUPPORTREGFILEXILINX(SUPPORTREGFILEXILINX)
)
uregfile
(
    .clki(clki),
    .rsti(rsti),

    
    .rd0i(piperdwbw),
    .rd0valuei(piperesultwbw),

    
    .ra0i(issueraidxw),
    .rb0i(issuerbidxw),
    .ra0valueo(issueravaluew),
    .rb0valueo(issuerbvaluew)
);

assign opcodeopcodeo = fetchinstri;
assign opcodepco     = fetchpci;
assign opcoderdidxo = issuerdidxw;
assign opcoderaidxo = issueraidxw;
assign opcoderbidxo = issuerbidxw;
assign opcodeinvalido= 1'b0; 

reg [31:0] issueravaluer;
reg [31:0] issuerbvaluer;

always @ *
begin
    
    issueravaluer = issueravaluew;
    issuerbvaluer = issuerbvaluew;

    
    if (piperdwbw == issueraidxw)
        issueravaluer = piperesultwbw;
    if (piperdwbw == issuerbidxw)
        issuerbvaluer = piperesultwbw;

    
    if (piperde2w == issueraidxw)
        issueravaluer = piperesulte2w;
    if (piperde2w == issuerbidxw)
        issuerbvaluer = piperesulte2w;

    
    if (piperde1w == issueraidxw)
        issueravaluer = writebackexecvaluei;
    if (piperde1w == issuerbidxw)
        issuerbvaluer = writebackexecvaluei;

    
    if (issueraidxw == 5'b0)
        issueravaluer = 32'b0;
    if (issuerbidxw == 5'b0)
        issuerbvaluer = 32'b0;
end

assign opcoderaoperando = issueravaluer;
assign opcoderboperando = issuerbvaluer;

assign lsuopcodeopcodeo      = opcodeopcodeo;
assign lsuopcodepco          = opcodepco;
assign lsuopcoderdidxo      = opcoderdidxo;
assign lsuopcoderaidxo      = opcoderaidxo;
assign lsuopcoderbidxo      = opcoderbidxo;
assign lsuopcoderaoperando  = opcoderaoperando;
assign lsuopcoderboperando  = opcoderboperando;
assign lsuopcodeinvalido     = 1'b0;

assign mulopcodeopcodeo      = opcodeopcodeo;
assign mulopcodepco          = opcodepco;
assign mulopcoderdidxo      = opcoderdidxo;
assign mulopcoderaidxo      = opcoderaidxo;
assign mulopcoderbidxo      = opcoderbidxo;
assign mulopcoderaoperando  = opcoderaoperando;
assign mulopcoderboperando  = opcoderboperando;
assign mulopcodeinvalido     = 1'b0;

assign csropcodevalido       = opcodeissuer & ~takeinterrupti;
assign csropcodeopcodeo      = opcodeopcodeo;
assign csropcodepco          = opcodepco;
assign csropcoderdidxo      = opcoderdidxo;
assign csropcoderaidxo      = opcoderaidxo;
assign csropcoderbidxo      = opcoderbidxo;
assign csropcoderaoperando  = opcoderaoperando;
assign csropcoderboperando  = opcoderboperando;
assign csropcodeinvalido     = opcodeissuer && issueinvalidw;


`ifdef verilator
riscvtracesim
upipedec0verif
(
     .validi(pipevalidwbw)
    ,.pci(pipepcwbw)
    ,.opcodei(pipeopcwbw)
);

wire [4:0] vpipers1w = pipeopcwbw[19:15];
wire [4:0] vpipers2w = pipeopcwbw[24:20];

function [0:0] completevalid0; /*verilator public*/
begin
    completevalid0 = pipevalidwbw;
end
endfunction
function [31:0] completepc0; /*verilator public*/
begin
    completepc0 = pipepcwbw;
end
endfunction
function [31:0] completeopcode0; /*verilator public*/
begin
    completeopcode0 = pipeopcwbw;
end
endfunction
function [4:0] completera0; /*verilator public*/
begin
    completera0 = vpipers1w;
end
endfunction
function [4:0] completerb0; /*verilator public*/
begin
    completerb0 = vpipers2w;
end
endfunction
function [4:0] completerd0; /*verilator public*/
begin
    completerd0 = piperdwbw;
end
endfunction
function [31:0] completeraval0; /*verilator public*/
begin
    completeraval0 = piperavalwbw;
end
endfunction
function [31:0] completerbval0; /*verilator public*/
begin
    completerbval0 = piperbvalwbw;
end
endfunction
function [31:0] completerdval0; /*verilator public*/
begin
    if (|piperdwbw)
        completerdval0 = piperesultwbw;
    else
        completerdval0 = 32'b0;
end
endfunction
function [5:0] completeexception; /*verilator public*/
begin
    completeexception = pipeexceptionwbw;
end
endfunction
`endif


endmodule

module riscvlsu
#(
     parameter MEMCACHEADDRMIN = 32'h80000000
    ,parameter MEMCACHEADDRMAX = 32'h8fffffff
)
(
    
     input           clki
    ,input           rsti
    ,input           opcodevalidi
    ,input  [ 31:0]  opcodeopcodei
    ,input  [ 31:0]  opcodepci
    ,input           opcodeinvalidi
    ,input  [  4:0]  opcoderdidxi
    ,input  [  4:0]  opcoderaidxi
    ,input  [  4:0]  opcoderbidxi
    ,input  [ 31:0]  opcoderaoperandi
    ,input  [ 31:0]  opcoderboperandi
    ,input  [ 31:0]  memdatardi
    ,input           memaccepti
    ,input           memacki
    ,input           memerrori
    ,input  [ 10:0]  memresptagi
    ,input           memloadfaulti
    ,input           memstorefaulti

    
    ,output [ 31:0]  memaddro
    ,output [ 31:0]  memdatawro
    ,output          memrdo
    ,output [  3:0]  memwro
    ,output          memcacheableo
    ,output [ 10:0]  memreqtago
    ,output          meminvalidateo
    ,output          memwritebacko
    ,output          memflusho
    ,output          writebackvalido
    ,output [ 31:0]  writebackvalueo
    ,output [  5:0]  writebackexceptiono
    ,output          stallo
);



`include "riscvdefs.v"

reg [ 31:0]  memaddrq;
reg [ 31:0]  memdatawrq;
reg          memrdq;
reg [  3:0]  memwrq;
reg          memcacheableq;
reg          meminvalidateq;
reg          memwritebackq;
reg          memflushq;
reg          memunalignede1q;
reg          memunalignede2q;

reg          memloadq;
reg          memxbq;
reg          memxhq;
reg          memlsq;

reg pendinglsue2q;

wire issuelsue1w    = (memrdo || (|memwro) || memwritebacko || meminvalidateo || memflusho) && memaccepti;
wire completeoke2w  = memacki & ~memerrori;
wire completeerre2w = memacki & memerrori;

always @ (posedge clki or posedge rsti)
if (rsti)
    pendinglsue2q <= 1'b0;
else if (issuelsue1w)
    pendinglsue2q <= 1'b1;
else if (completeoke2w || completeerre2w)
    pendinglsue2q <= 1'b0;

wire delaylsue2w = pendinglsue2q && !completeoke2w;

always @ (posedge clki or posedge rsti)
if (rsti)
    memunalignede2q <= 1'b0;
else
    memunalignede2q <= memunalignede1q & ~delaylsue2w;


wire loadinstw = (((opcodeopcodei & `INSTLBMASK) == `INSTLB)  || 
                    ((opcodeopcodei & `INSTLHMASK) == `INSTLH)  || 
                    ((opcodeopcodei & `INSTLWMASK) == `INSTLW)  || 
                    ((opcodeopcodei & `INSTLBUMASK) == `INSTLBU) || 
                    ((opcodeopcodei & `INSTLHUMASK) == `INSTLHU) || 
                    ((opcodeopcodei & `INSTLWUMASK) == `INSTLWU));

wire loadsignedinstw = (((opcodeopcodei & `INSTLBMASK) == `INSTLB)  || 
                           ((opcodeopcodei & `INSTLHMASK) == `INSTLH)  || 
                           ((opcodeopcodei & `INSTLWMASK) == `INSTLW));

wire storeinstw = (((opcodeopcodei & `INSTSBMASK) == `INSTSB)  || 
                     ((opcodeopcodei & `INSTSHMASK) == `INSTSH)  || 
                     ((opcodeopcodei & `INSTSWMASK) == `INSTSW));

wire reqlbw = ((opcodeopcodei & `INSTLBMASK) == `INSTLB) || ((opcodeopcodei & `INSTLBUMASK) == `INSTLBU);
wire reqlhw = ((opcodeopcodei & `INSTLHMASK) == `INSTLH) || ((opcodeopcodei & `INSTLHUMASK) == `INSTLHU);
wire reqlww = ((opcodeopcodei & `INSTLWMASK) == `INSTLW) || ((opcodeopcodei & `INSTLWUMASK) == `INSTLWU);
wire reqsbw = ((opcodeopcodei & `INSTLBMASK) == `INSTSB);
wire reqshw = ((opcodeopcodei & `INSTLHMASK) == `INSTSH);
wire reqsww = ((opcodeopcodei & `INSTLWMASK) == `INSTSW);

wire reqswlww = ((opcodeopcodei & `INSTSWMASK) == `INSTSW) || ((opcodeopcodei & `INSTLWMASK) == `INSTLW) || ((opcodeopcodei & `INSTLWUMASK) == `INSTLWU);
wire reqshlhw = ((opcodeopcodei & `INSTSHMASK) == `INSTSH) || ((opcodeopcodei & `INSTLHMASK) == `INSTLH) || ((opcodeopcodei & `INSTLHUMASK) == `INSTLHU);

reg [31:0]  memaddrr;
reg         memunalignedr;
reg [31:0]  memdatar;
reg         memrdr;
reg [3:0]   memwrr;

always @ *
begin
    memaddrr      = 32'b0;
    memdatar      = 32'b0;
    memunalignedr = 1'b0;
    memwrr        = 4'b0;
    memrdr        = 1'b0;

    if (opcodevalidi && ((opcodeopcodei & `INSTCSRRWMASK) == `INSTCSRRW))
        memaddrr = opcoderaoperandi;
    else if (opcodevalidi && loadinstw)
        memaddrr = opcoderaoperandi + {{20{opcodeopcodei[31]}}, opcodeopcodei[31:20]};
    else
        memaddrr = opcoderaoperandi + {{20{opcodeopcodei[31]}}, opcodeopcodei[31:25], opcodeopcodei[11:7]};

    if (opcodevalidi && reqswlww)
        memunalignedr = (memaddrr[1:0] != 2'b0);
    else if (opcodevalidi && reqshlhw)
        memunalignedr = memaddrr[0];

    memrdr = (opcodevalidi && loadinstw && !memunalignedr);

    if (opcodevalidi && ((opcodeopcodei & `INSTSWMASK) == `INSTSW) && !memunalignedr)
    begin
        memdatar  = opcoderboperandi;
        memwrr    = 4'hF;
    end
    else if (opcodevalidi && ((opcodeopcodei & `INSTSHMASK) == `INSTSH) && !memunalignedr)
    begin
        case (memaddrr[1:0])
        2'h2 :
        begin
            memdatar  = {opcoderboperandi[15:0],16'h0000};
            memwrr    = 4'b1100;
        end
        default :
        begin
            memdatar  = {16'h0000,opcoderboperandi[15:0]};
            memwrr    = 4'b0011;
        end
        endcase
    end
    else if (opcodevalidi && ((opcodeopcodei & `INSTSBMASK) == `INSTSB))
    begin
        case (memaddrr[1:0])
        2'h3 :
        begin
            memdatar  = {opcoderboperandi[7:0],24'h000000};
            memwrr    = 4'b1000;
        end
        2'h2 :
        begin
            memdatar  = {{8'h00,opcoderboperandi[7:0]},16'h0000};
            memwrr    = 4'b0100;
        end
        2'h1 :
        begin
            memdatar  = {{16'h0000,opcoderboperandi[7:0]},8'h00};
            memwrr    = 4'b0010;
        end
        2'h0 :
        begin
            memdatar  = {24'h000000,opcoderboperandi[7:0]};
            memwrr    = 4'b0001;
        end
        default :
        ;
        endcase
    end
    else
        memwrr    = 4'b0;
end

wire dcacheflushw      = ((opcodeopcodei & `INSTCSRRWMASK) == `INSTCSRRW) && (opcodeopcodei[31:20] == `CSRDFLUSH);
wire dcachewritebackw  = ((opcodeopcodei & `INSTCSRRWMASK) == `INSTCSRRW) && (opcodeopcodei[31:20] == `CSRDWRITEBACK);
wire dcacheinvalidatew = ((opcodeopcodei & `INSTCSRRWMASK) == `INSTCSRRW) && (opcodeopcodei[31:20] == `CSRDINVALIDATE);


always @ (posedge clki or posedge rsti)
if (rsti)
begin
    memaddrq         <= 32'b0;
    memdatawrq      <= 32'b0;
    memrdq           <= 1'b0;
    memwrq           <= 4'b0;
    memcacheableq    <= 1'b0;
    meminvalidateq   <= 1'b0;
    memwritebackq    <= 1'b0;
    memflushq        <= 1'b0;
    memunalignede1q <= 1'b0;
    memloadq         <= 1'b0;
    memxbq           <= 1'b0;
    memxhq           <= 1'b0;
    memlsq           <= 1'b0;
end
else if (completeerre2w || memunalignede2q)
begin
    memaddrq         <= 32'b0;
    memdatawrq      <= 32'b0;
    memrdq           <= 1'b0;
    memwrq           <= 4'b0;
    memcacheableq    <= 1'b0;
    meminvalidateq   <= 1'b0;
    memwritebackq    <= 1'b0;
    memflushq        <= 1'b0;
    memunalignede1q <= 1'b0;
    memloadq         <= 1'b0;
    memxbq           <= 1'b0;
    memxhq           <= 1'b0;
    memlsq           <= 1'b0;
end
else if ((memrdq || (|memwrq) || memunalignede1q) && delaylsue2w)
    ;
else if (!((memwritebacko || meminvalidateo || memflusho || memrdo || memwro != 4'b0) && !memaccepti))
begin
    memaddrq         <= 32'b0;
    memdatawrq      <= memdatar;
    memrdq           <= memrdr;
    memwrq           <= memwrr;
    memcacheableq    <= 1'b0;
    meminvalidateq   <= 1'b0;
    memwritebackq    <= 1'b0;
    memflushq        <= 1'b0;
    memunalignede1q <= memunalignedr;
    memloadq         <= opcodevalidi && loadinstw;
    memxbq           <= reqlbw | reqsbw;
    memxhq           <= reqlhw | reqshw;
    memlsq           <= loadsignedinstw;

/* verilator lintoff UNSIGNED */
/* verilator lintoff CMPCONST */
    memcacheableq  <= (memaddrr >= MEMCACHEADDRMIN && memaddrr <= MEMCACHEADDRMAX) ||
                        (opcodevalidi && (dcacheinvalidatew || dcachewritebackw || dcacheflushw));
/* verilator linton CMPCONST */
/* verilator linton UNSIGNED */

    meminvalidateq <= opcodevalidi & dcacheinvalidatew;
    memwritebackq  <= opcodevalidi & dcachewritebackw;
    memflushq      <= opcodevalidi & dcacheflushw;
    memaddrq       <= memaddrr;
end

assign memaddro       = {memaddrq[31:2], 2'b0};
assign memdatawro    = memdatawrq;
assign memrdo         = memrdq & ~delaylsue2w;
assign memwro         = memwrq & ~{4{delaylsue2w}};
assign memcacheableo  = memcacheableq;
assign memreqtago    = 11'b0;
assign meminvalidateo = meminvalidateq;
assign memwritebacko  = memwritebackq;
assign memflusho      = memflushq;

assign stallo          = ((memwritebacko || meminvalidateo || memflusho || memrdo || memwro != 4'b0) && !memaccepti) || delaylsue2w || memunalignede1q;

wire        resploadw;
wire [31:0] respaddrw;
wire        respbytew;
wire        resphalfw;
wire        respsignedw;

riscvlsufifo
#(
     .WIDTH(36)
    ,.DEPTH(2)
    ,.ADDRW(1)
)
ulsurequest
(
     .clki(clki)
    ,.rsti(rsti)

    ,.pushi(((memrdo || (|memwro) || memwritebacko || meminvalidateo || memflusho) && memaccepti) || (memunalignede1q && ~delaylsue2w))
    ,.dataini({memaddrq, memlsq, memxhq, memxbq, memloadq})
    ,.accepto()

    ,.valido()
    ,.dataouto({respaddrw, respsignedw, resphalfw, respbytew, resploadw})
    ,.popi(memacki || memunalignede2q)
);

reg [1:0]  addrlsbr;
reg        loadbyter;
reg        loadhalfr;
reg        loadsignedr;
reg [31:0] wbresultr;

always @ *
begin
    wbresultr   = 32'b0;

    
    addrlsbr    = respaddrw[1:0];
    loadbyter   = respbytew;
    loadhalfr   = resphalfw;
    loadsignedr = respsignedw;

    
    if ((memacki && memerrori) || memunalignede2q)
        wbresultr = respaddrw;
    
    else if (memacki && resploadw)
    begin
        if (loadbyter)
        begin
            case (addrlsbr[1:0])
            2'h3: wbresultr = {24'b0, memdatardi[31:24]};
            2'h2: wbresultr = {24'b0, memdatardi[23:16]};
            2'h1: wbresultr = {24'b0, memdatardi[15:8]};
            2'h0: wbresultr = {24'b0, memdatardi[7:0]};
            endcase

            if (loadsignedr && wbresultr[7])
                wbresultr = {24'hFFFFFF, wbresultr[7:0]};
        end
        else if (loadhalfr)
        begin
            if (addrlsbr[1])
                wbresultr = {16'b0, memdatardi[31:16]};
            else
                wbresultr = {16'b0, memdatardi[15:0]};

            if (loadsignedr && wbresultr[15])
                wbresultr = {16'hFFFF, wbresultr[15:0]};
        end
        else
            wbresultr = memdatardi;
    end
end

assign writebackvalido    = memacki | memunalignede2q;
assign writebackvalueo    = wbresultr;

wire faultloadalignw     = memunalignede2q & resploadw;
wire faultstorealignw    = memunalignede2q & ~resploadw;
wire faultloadbusw       = memerrori &&  resploadw;
wire faultstorebusw      = memerrori && ~resploadw;
wire faultloadpagew      = memerrori && memloadfaulti;
wire faultstorepagew     = memerrori && memstorefaulti;


assign writebackexceptiono         = faultloadalignw  ? `EXCEPTIONMISALIGNEDLOAD:
                                       faultstorealignw ? `EXCEPTIONMISALIGNEDSTORE:
                                       faultloadpagew   ? `EXCEPTIONPAGEFAULTLOAD:
                                       faultstorepagew  ? `EXCEPTIONPAGEFAULTSTORE:
                                       faultloadbusw    ? `EXCEPTIONFAULTLOAD:
                                       faultstorebusw   ? `EXCEPTIONFAULTSTORE:
                                       `EXCEPTIONW'b0;

endmodule 

module riscvlsufifo
#(
    parameter WIDTH   = 8,
    parameter DEPTH   = 4,
    parameter ADDRW  = 2
)
(
    
     input               clki
    ,input               rsti
    ,input  [WIDTH-1:0]  dataini
    ,input               pushi
    ,input               popi

    
    ,output [WIDTH-1:0]  dataouto
    ,output              accepto
    ,output              valido
);

localparam COUNTW = ADDRW + 1;

reg [WIDTH-1:0]   ramq[DEPTH-1:0];
reg [ADDRW-1:0]  rdptrq;
reg [ADDRW-1:0]  wrptrq;
reg [COUNTW-1:0] countq;

integer i;

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    countq   <= {(COUNTW) {1'b0}};
    rdptrq  <= {(ADDRW) {1'b0}};
    wrptrq  <= {(ADDRW) {1'b0}};

    for (i=0;i<DEPTH;i=i+1)
    begin
        ramq[i] <= {(WIDTH) {1'b0}};
    end
end
else
begin
    
    if (pushi & accepto)
    begin
        ramq[wrptrq] <= dataini;
        wrptrq        <= wrptrq + 1;
    end

    
    if (popi & valido)
        rdptrq      <= rdptrq + 1;

    
    if ((pushi & accepto) & ~(popi & valido))
        countq <= countq + 1;
    
    else if (~(pushi & accepto) & (popi & valido))
        countq <= countq - 1;
end

/* verilator lintoff WIDTH */
assign valido       = (countq != 0);
assign accepto      = (countq != DEPTH);
/* verilator linton WIDTH */

assign dataouto    = ramq[rdptrq];



endmodule

module riscvmmu
#(
     parameter MEMCACHEADDRMIN = 32'h80000000
    ,parameter MEMCACHEADDRMAX = 32'h8fffffff
    ,parameter SUPPORTMMU      = 1
)
(
    
     input           clki
    ,input           rsti
    ,input  [  1:0]  privdi
    ,input           sumi
    ,input           mxri
    ,input           flushi
    ,input  [ 31:0]  satpi
    ,input           fetchinrdi
    ,input           fetchinflushi
    ,input           fetchininvalidatei
    ,input  [ 31:0]  fetchinpci
    ,input  [  1:0]  fetchinprivi
    ,input           fetchoutaccepti
    ,input           fetchoutvalidi
    ,input           fetchouterrori
    ,input  [ 31:0]  fetchoutinsti
    ,input  [ 31:0]  lsuinaddri
    ,input  [ 31:0]  lsuindatawri
    ,input           lsuinrdi
    ,input  [  3:0]  lsuinwri
    ,input           lsuincacheablei
    ,input  [ 10:0]  lsuinreqtagi
    ,input           lsuininvalidatei
    ,input           lsuinwritebacki
    ,input           lsuinflushi
    ,input  [ 31:0]  lsuoutdatardi
    ,input           lsuoutaccepti
    ,input           lsuoutacki
    ,input           lsuouterrori
    ,input  [ 10:0]  lsuoutresptagi

    
    ,output          fetchinaccepto
    ,output          fetchinvalido
    ,output          fetchinerroro
    ,output [ 31:0]  fetchininsto
    ,output          fetchoutrdo
    ,output          fetchoutflusho
    ,output          fetchoutinvalidateo
    ,output [ 31:0]  fetchoutpco
    ,output          fetchinfaulto
    ,output [ 31:0]  lsuindatardo
    ,output          lsuinaccepto
    ,output          lsuinacko
    ,output          lsuinerroro
    ,output [ 10:0]  lsuinresptago
    ,output [ 31:0]  lsuoutaddro
    ,output [ 31:0]  lsuoutdatawro
    ,output          lsuoutrdo
    ,output [  3:0]  lsuoutwro
    ,output          lsuoutcacheableo
    ,output [ 10:0]  lsuoutreqtago
    ,output          lsuoutinvalidateo
    ,output          lsuoutwritebacko
    ,output          lsuoutflusho
    ,output          lsuinloadfaulto
    ,output          lsuinstorefaulto
);



`include "riscvdefs.v"

localparam  STATEW            = 2;
localparam  STATEIDLE         = 0;
localparam  STATELEVELFIRST  = 1;
localparam  STATELEVELSECOND = 2;
localparam  STATEUPDATE       = 3;

generate
if (SUPPORTMMU)
begin

    
    
    
    reg [STATEW-1:0] stateq;
    wire              idlew = (stateq == STATEIDLE);

    
    wire        respmmuw   = (lsuoutresptagi[9:7] == 3'b111);
    wire        respvalidw = respmmuw & lsuoutacki;
    wire        resperrorw = respmmuw & lsuouterrori;
    wire [31:0] respdataw  = lsuoutdatardi;

    wire        cpuacceptw;

    
    
    
    reg       loadq;
    reg [3:0] storeq;

    always @ (posedge clki or posedge rsti)
    if (rsti)
        loadq <= 1'b0;
    else if (lsuinrdi)
        loadq <= ~lsuinaccepto;

    always @ (posedge clki or posedge rsti)
    if (rsti)
        storeq <= 4'b0;
    else if (|lsuinwri)
        storeq <= lsuinaccepto ? 4'b0 : lsuinwri;

    wire       loadw  = lsuinrdi | loadq;
    wire [3:0] storew = lsuinwri | storeq;

    reg [31:0] lsuinaddrq;

    always @ (posedge clki or posedge rsti)
    if (rsti)
        lsuinaddrq <= 32'b0;
    else if (loadw || (|storew))
        lsuinaddrq <= lsuinaddri;

    wire [31:0] lsuaddrw = (loadw || (|storew)) ? lsuinaddri : lsuinaddrq;

    
    
    
    wire        itlbhitw;
    wire        dtlbhitw;

    reg         dtlbreqq;

    
    wire        vmenablew = satpi[`SATPMODER];
    wire [31:0] ptbrw      = {satpi[`SATPPPNR], 12'b0};

    wire        ifetchvmw = (fetchinprivi != `PRIVMACHINE);
    wire        dfetchvmw = (privdi != `PRIVMACHINE);

    wire        supervisoriw = (fetchinprivi == `PRIVSUPER);
    wire        supervisordw = (privdi == `PRIVSUPER);

    wire        vmienablew = (ifetchvmw);
    wire        vmdenablew = (vmenablew & dfetchvmw);

    
    wire        itlbmissw = fetchinrdi & vmienablew & ~itlbhitw;
    wire        dtlbmissw = (loadw || (|storew)) & vmdenablew & ~dtlbhitw;

    
    wire [31:0] requestaddrw = idlew ? 
                                (dtlbmissw ? lsuaddrw : fetchinpci) :
                                 dtlbreqq ? lsuaddrw : fetchinpci;

    reg [31:0]  pteaddrq;
    reg [31:0]  pteentryq;
    reg [31:0]  virtaddrq;

    wire [31:0] pteppnw   = {`PAGEPFNSHIFT'b0, respdataw[31:`PAGEPFNSHIFT]};
    wire [9:0]  pteflagsw = respdataw[9:0];

    always @ (posedge clki or posedge rsti)
    if (rsti)
    begin
        pteaddrq  <= 32'b0;
        pteentryq <= 32'b0;
        virtaddrq <= 32'b0;
        dtlbreqq  <= 1'b0;
        stateq     <= STATEIDLE;
    end
    else
    begin
        
        if (stateq == STATEIDLE && (itlbmissw || dtlbmissw))
        begin
            pteaddrq  <= ptbrw + {20'b0, requestaddrw[31:22], 2'b0};
            virtaddrq <= requestaddrw;
            dtlbreqq  <= dtlbmissw;

            stateq     <= STATELEVELFIRST;
        end
        
        else if (stateq == STATELEVELFIRST && respvalidw)
        begin
            
            if (resperrorw || !respdataw[`PAGEPRESENT])
            begin
                pteentryq <= 32'b0;
                stateq     <= STATEUPDATE;
            end
            
            else if (!(respdataw[`PAGEREAD] || respdataw[`PAGEWRITE] || respdataw[`PAGEEXEC]))
            begin
                pteaddrq  <= {respdataw[29:10], 12'b0} + {20'b0, requestaddrw[21:12], 2'b0};
                stateq     <= STATELEVELSECOND;
            end
            
            else
            begin
                pteentryq <= ((pteppnw | {22'b0, requestaddrw[21:12]}) << `MMUPGSHIFT) | {22'b0, pteflagsw};
                stateq     <= STATEUPDATE;
            end
        end
        
        else if (stateq == STATELEVELSECOND && respvalidw)
        begin
            
            if (respdataw[`PAGEPRESENT])
            begin
                pteentryq <= (pteppnw << `MMUPGSHIFT) | {22'b0, pteflagsw};
                stateq     <= STATEUPDATE;
            end
            
            else
            begin
                pteentryq <= 32'b0;
                stateq     <= STATEUPDATE;
            end
        end
        else if (stateq == STATEUPDATE)
        begin
            stateq    <= STATEIDLE;
        end
    end

    
    
    
    reg         itlbvalidq;
    reg [31:12] itlbvaaddrq;
    reg [31:0]  itlbentryq;

    always @ (posedge clki or posedge rsti)
    if (rsti)
        itlbvalidq <= 1'b0;
    else if (flushi)
        itlbvalidq <= 1'b0;
    else if (stateq == STATEUPDATE && !dtlbreqq)
        itlbvalidq <= (itlbvaaddrq == fetchinpci[31:12]); 
    else if (stateq != STATEIDLE && !dtlbreqq)
        itlbvalidq <= 1'b0;

    always @ (posedge clki or posedge rsti)
    if (rsti)
    begin
        itlbvaaddrq <= 20'b0;
        itlbentryq   <= 32'b0;
    end
    else if (stateq == STATEUPDATE && !dtlbreqq)
    begin
        itlbvaaddrq <= virtaddrq[31:12];
        itlbentryq   <= pteentryq;
    end

    
    assign itlbhitw   = fetchinrdi & itlbvalidq & (itlbvaaddrq == fetchinpci[31:12]);

    reg pcfaultr;
    always @ *
    begin
        pcfaultr = 1'b0;

        if (vmienablew && itlbhitw)
        begin
            
            if (supervisoriw)
            begin
                
                if (itlbentryq[`PAGEUSER])
                    pcfaultr = 1'b1;
                
                else
                    pcfaultr = ~itlbentryq[`PAGEEXEC];
            end
            
            else
                pcfaultr = (~itlbentryq[`PAGEEXEC]) | (~itlbentryq[`PAGEUSER]);
        end
    end

    reg pcfaultq;

    always @ (posedge clki or posedge rsti)
    if (rsti)
        pcfaultq <= 1'b0;
    else
        pcfaultq <= pcfaultr;

    assign fetchoutrdo         = (~vmienablew & fetchinrdi) || (itlbhitw & ~pcfaultr);
    assign fetchoutpco         = vmienablew ? {itlbentryq[31:12], fetchinpci[11:0]} : fetchinpci;
    assign fetchoutflusho      = fetchinflushi;
    assign fetchoutinvalidateo = fetchininvalidatei; 

    assign fetchinaccepto      = (~vmienablew & fetchoutaccepti) | (vmienablew & itlbhitw & fetchoutaccepti) | pcfaultr;
    assign fetchinvalido       = fetchoutvalidi | pcfaultq;
    assign fetchinerroro       = fetchoutvalidi & fetchouterrori;
    assign fetchinfaulto       = pcfaultq;
    assign fetchininsto        = fetchoutinsti;

    
    
    
    reg         dtlbvalidq;
    reg [31:12] dtlbvaaddrq;
    reg [31:0]  dtlbentryq;

    always @ (posedge clki or posedge rsti)
    if (rsti)
        dtlbvalidq <= 1'b0;
    else if (flushi)
        dtlbvalidq <= 1'b0;
    else if (stateq == STATEUPDATE && dtlbreqq)
        dtlbvalidq <= 1'b1;

    always @ (posedge clki or posedge rsti)
    if (rsti)
    begin
        dtlbvaaddrq <= 20'b0;
        dtlbentryq   <= 32'b0;
    end
    else if (stateq == STATEUPDATE && dtlbreqq)
    begin
        dtlbvaaddrq <= virtaddrq[31:12];
        dtlbentryq   <= pteentryq;
    end

    
    assign dtlbhitw   = dtlbvalidq & (dtlbvaaddrq == lsuaddrw[31:12]);

    reg loadfaultr;
    always @ *
    begin
        loadfaultr = 1'b0;

        if (vmdenablew && loadw && dtlbhitw)
        begin
            
            if (supervisordw)
            begin
                
                if (dtlbentryq[`PAGEUSER] && !sumi)
                    loadfaultr = 1'b1;
                
                else
                    loadfaultr = ~(dtlbentryq[`PAGEREAD] | (mxri & dtlbentryq[`PAGEEXEC]));
            end
            
            else
                loadfaultr = (~dtlbentryq[`PAGEREAD]) | (~dtlbentryq[`PAGEUSER]);
        end
    end

    reg storefaultr;
    always @ *
    begin
        storefaultr = 1'b0;

        if (vmdenablew && (|storew) && dtlbhitw)
        begin
            
            if (supervisordw)
            begin
                
                if (dtlbentryq[`PAGEUSER] && !sumi)
                    storefaultr = 1'b1;
                
                else
                    storefaultr = (~dtlbentryq[`PAGEREAD]) | (~dtlbentryq[`PAGEWRITE]);
            end
            
            else
                storefaultr = (~dtlbentryq[`PAGEREAD]) | (~dtlbentryq[`PAGEWRITE]) | (~dtlbentryq[`PAGEUSER]);
        end
    end

    reg storefaultq;
    reg loadfaultq;

    always @ (posedge clki or posedge rsti)
    if (rsti)
        storefaultq <= 1'b0;
    else
        storefaultq <= storefaultr;

    always @ (posedge clki or posedge rsti)
    if (rsti)
        loadfaultq <= 1'b0;
    else
        loadfaultq <= loadfaultr;   

    wire        lsuoutrdw         = vmdenablew ? (loadw  & dtlbhitw & ~loadfaultr)       : lsuinrdi;
    wire [3:0]  lsuoutwrw         = vmdenablew ? (storew & {4{dtlbhitw & ~storefaultr}}) : lsuinwri;
    wire [31:0] lsuoutaddrw       = vmdenablew ? {dtlbentryq[31:12], lsuaddrw[11:0]}      : lsuaddrw;
    wire [31:0] lsuoutdatawrw    = lsuindatawri;

    wire        lsuoutinvalidatew = lsuininvalidatei;
    wire        lsuoutwritebackw  = lsuinwritebacki;

    reg         lsuoutcacheabler;
    always @ *
    begin
/* verilator lintoff UNSIGNED */
/* verilator lintoff CMPCONST */
        if (lsuininvalidatei || lsuinwritebacki || lsuinflushi)
            lsuoutcacheabler = 1'b1;
        else
            lsuoutcacheabler = (lsuoutaddrw >= MEMCACHEADDRMIN && lsuoutaddrw <= MEMCACHEADDRMAX);
/* verilator linton CMPCONST */
/* verilator linton UNSIGNED */
    end

    wire [10:0] lsuoutreqtagw    = lsuinreqtagi;
    wire        lsuoutflushw      = lsuinflushi;

    assign lsuinacko         = (lsuoutacki & ~respmmuw) | storefaultq | loadfaultq;
    assign lsuinresptago    = lsuoutresptagi;
    assign lsuinerroro       = (lsuouterrori & ~respmmuw) | storefaultq | loadfaultq;
    assign lsuindatardo     = lsuoutdatardi;
    assign lsuinstorefaulto = storefaultq;
    assign lsuinloadfaulto  = loadfaultq;

    assign lsuinaccepto      = (~vmdenablew & cpuacceptw) | (vmdenablew & dtlbhitw & cpuacceptw) | storefaultr | loadfaultr;

    
    
    
    reg memreqq;
    wire mmuacceptw;

    always @ (posedge clki or posedge rsti)
    if (rsti)
        memreqq <= 1'b0;
    else if (stateq == STATEIDLE && (itlbmissw || dtlbmissw))
        memreqq <= 1'b1;
    else if (stateq == STATELEVELFIRST && respvalidw && !resperrorw && respdataw[`PAGEPRESENT] && (!(respdataw[`PAGEREAD] || respdataw[`PAGEWRITE] || respdataw[`PAGEEXEC])))
        memreqq <= 1'b1;    
    else if (mmuacceptw)
        memreqq <= 1'b0;

    
    
    
    reg  readholdq;
    reg  srcmmuq;
    wire srcmmuw = readholdq ? srcmmuq : memreqq;

    always @ (posedge clki or posedge rsti)
    if (rsti)
    begin
        readholdq  <= 1'b0;
        srcmmuq    <= 1'b0;
    end
    else if ((lsuoutrdo || (|lsuoutwro)) && !lsuoutaccepti)
    begin
        readholdq  <= 1'b1;
        srcmmuq    <= srcmmuw;
    end
    else if (lsuoutaccepti)
        readholdq  <= 1'b0;

    assign mmuacceptw         = srcmmuw  & lsuoutaccepti;
    assign cpuacceptw         = ~srcmmuw & lsuoutaccepti;

    assign lsuoutrdo         = srcmmuw ? memreqq  : lsuoutrdw;
    assign lsuoutwro         = srcmmuw ? 4'b0       : lsuoutwrw;
    assign lsuoutaddro       = srcmmuw ? pteaddrq : lsuoutaddrw;
    assign lsuoutdatawro    = lsuoutdatawrw;

    assign lsuoutinvalidateo = srcmmuw ? 1'b0 : lsuoutinvalidatew;
    assign lsuoutwritebacko  = srcmmuw ? 1'b0 : lsuoutwritebackw;
    assign lsuoutcacheableo  = srcmmuw ? 1'b1 : lsuoutcacheabler;
    assign lsuoutreqtago    = srcmmuw ? {1'b0, 3'b111, 7'b0} : lsuoutreqtagw;
    assign lsuoutflusho      = srcmmuw ? 1'b0 : lsuoutflushw;

end
else
begin
    assign fetchoutrdo         = fetchinrdi;
    assign fetchoutpco         = fetchinpci;
    assign fetchoutflusho      = fetchinflushi;
    assign fetchoutinvalidateo = fetchininvalidatei;
    assign fetchinaccepto      = fetchoutaccepti;
    assign fetchinvalido       = fetchoutvalidi;
    assign fetchinerroro       = fetchouterrori;
    assign fetchinfaulto       = 1'b0;
    assign fetchininsto        = fetchoutinsti;

    assign lsuoutrdo           = lsuinrdi;
    assign lsuoutwro           = lsuinwri;
    assign lsuoutaddro         = lsuinaddri;
    assign lsuoutdatawro      = lsuindatawri;
    assign lsuoutinvalidateo   = lsuininvalidatei;
    assign lsuoutwritebacko    = lsuinwritebacki;
    assign lsuoutcacheableo    = lsuincacheablei;
    assign lsuoutreqtago      = lsuinreqtagi;
    assign lsuoutflusho        = lsuinflushi;
    
    assign lsuinacko           = lsuoutacki;
    assign lsuinresptago      = lsuoutresptagi;
    assign lsuinerroro         = lsuouterrori;
    assign lsuindatardo       = lsuoutdatardi;
    assign lsuinstorefaulto   = 1'b0;
    assign lsuinloadfaulto    = 1'b0;

    assign lsuinaccepto        = lsuoutaccepti;
end
endgenerate

endmodule

module riscvmultiplier
(
    
     input           clki
    ,input           rsti
    ,input           opcodevalidi
    ,input  [ 31:0]  opcodeopcodei
    ,input  [ 31:0]  opcodepci
    ,input           opcodeinvalidi
    ,input  [  4:0]  opcoderdidxi
    ,input  [  4:0]  opcoderaidxi
    ,input  [  4:0]  opcoderbidxi
    ,input  [ 31:0]  opcoderaoperandi
    ,input  [ 31:0]  opcoderboperandi
    ,input           holdi

    
    ,output [ 31:0]  writebackvalueo
);



`include "riscvdefs.v"

localparam MULTSTAGES = 2; 

reg  [31:0]  resulte2q;
reg  [31:0]  resulte3q;

reg [32:0]   operandae1q;
reg [32:0]   operandbe1q;
reg          mulhisele1q;

wire [64:0]  multresultw;
reg  [32:0]  operandbr;
reg  [32:0]  operandar;
reg  [31:0]  resultr;

wire multinstw    = ((opcodeopcodei & `INSTMULMASK) == `INSTMUL)        || 
                      ((opcodeopcodei & `INSTMULHMASK) == `INSTMULH)      ||
                      ((opcodeopcodei & `INSTMULHSUMASK) == `INSTMULHSU)  ||
                      ((opcodeopcodei & `INSTMULHUMASK) == `INSTMULHU);


always @ *
begin
    if ((opcodeopcodei & `INSTMULHSUMASK) == `INSTMULHSU)
        operandar = {opcoderaoperandi[31], opcoderaoperandi[31:0]};
    else if ((opcodeopcodei & `INSTMULHMASK) == `INSTMULH)
        operandar = {opcoderaoperandi[31], opcoderaoperandi[31:0]};
    else 
        operandar = {1'b0, opcoderaoperandi[31:0]};
end

always @ *
begin
    if ((opcodeopcodei & `INSTMULHSUMASK) == `INSTMULHSU)
        operandbr = {1'b0, opcoderboperandi[31:0]};
    else if ((opcodeopcodei & `INSTMULHMASK) == `INSTMULH)
        operandbr = {opcoderboperandi[31], opcoderboperandi[31:0]};
    else 
        operandbr = {1'b0, opcoderboperandi[31:0]};
end


always @(posedge clki or posedge rsti)
if (rsti)
begin
    operandae1q <= 33'b0;
    operandbe1q <= 33'b0;
    mulhisele1q <= 1'b0;
end
else if (holdi)
    ;
else if (opcodevalidi && multinstw)
begin
    operandae1q <= operandar;
    operandbe1q <= operandbr;
    mulhisele1q <= ~((opcodeopcodei & `INSTMULMASK) == `INSTMUL);
end
else
begin
    operandae1q <= 33'b0;
    operandbe1q <= 33'b0;
    mulhisele1q <= 1'b0;
end

assign multresultw = {{ 32 {operandae1q[32]}}, operandae1q}*{{ 32 {operandbe1q[32]}}, operandbe1q};

always @ *
begin
    resultr = mulhisele1q ? multresultw[63:32] : multresultw[31:0];
end

always @(posedge clki or posedge rsti)
if (rsti)
    resulte2q <= 32'b0;
else if (~holdi)
    resulte2q <= resultr;

always @(posedge clki or posedge rsti)
if (rsti)
    resulte3q <= 32'b0;
else if (~holdi)
    resulte3q <= resulte2q;

assign writebackvalueo  = (MULTSTAGES == 3) ? resulte3q : resulte2q;


endmodule
module riscvpipectrl
#(
     parameter SUPPORTLOADBYPASS = 1
    ,parameter SUPPORTMULBYPASS  = 1
)
(
     input           clki
    ,input           rsti

    
    ,input           issuevalidi
    ,input           issueaccepti
    ,input           issuestalli
    ,input           issuelsui
    ,input           issuecsri
    ,input           issuedivi
    ,input           issuemuli
    ,input           issuebranchi
    ,input           issuerdvalidi
    ,input  [4:0]    issuerdi
    ,input  [5:0]    issueexceptioni
    ,input           takeinterrupti
    ,input           issuebranchtakeni
    ,input [31:0]    issuebranchtargeti
    ,input [31:0]    issuepci
    ,input [31:0]    issueopcodei
    ,input [31:0]    issueoperandrai
    ,input [31:0]    issueoperandrbi

    
    ,input [31:0]    aluresulte1i

    
    ,input [ 31:0]   csrresultvaluee1i
    ,input           csrresultwritee1i
    ,input [ 31:0]   csrresultwdatae1i
    ,input [  5:0]   csrresultexceptione1i

    
    ,output          loade1o
    ,output          storee1o
    ,output          mule1o
    ,output          branche1o
    ,output [  4:0]  rde1o
    ,output [31:0]   pce1o
    ,output [31:0]   opcodee1o
    ,output [31:0]   operandrae1o
    ,output [31:0]   operandrbe1o

    
    ,input           memcompletei
    ,input [31:0]    memresulte2i
    ,input  [5:0]    memexceptione2i
    ,input [31:0]    mulresulte2i

    
    ,output          loade2o
    ,output          mule2o
    ,output [  4:0]  rde2o
    ,output [31:0]   resulte2o

    
    ,input           divcompletei
    ,input  [31:0]   divresulti

    
    ,output          validwbo
    ,output          csrwbo
    ,output [  4:0]  rdwbo
    ,output [31:0]   resultwbo
    ,output [31:0]   pcwbo
    ,output [31:0]   opcodewbo
    ,output [31:0]   operandrawbo
    ,output [31:0]   operandrbwbo
    ,output [5:0]    exceptionwbo
    ,output          csrwritewbo
    ,output [11:0]   csrwaddrwbo
    ,output [31:0]   csrwdatawbo

    ,output          stallo
    ,output          squashe1e2o
    ,input           squashe1e2i
    ,input           squashwbi
);

`include "riscvdefs.v"

wire squashe1e2w;
wire branchmisalignedw = (issuebranchtakeni && issuebranchtargeti[1:0] != 2'b0);

`define PCINFOW     10
`define PCINFOALU       0
`define PCINFOLOAD      1
`define PCINFOSTORE     2
`define PCINFOCSR       3
`define PCINFODIV       4
`define PCINFOMUL       5
`define PCINFOBRANCH    6
`define PCINFORDVALID  7
`define PCINFOINTR      8
`define PCINFOCOMPLETE  9

`define RDIDXR    11:7

reg                     valide1q;
reg [`PCINFOW-1:0]     ctrle1q;
reg [31:0]              pce1q;
reg [31:0]              npce1q;
reg [31:0]              opcodee1q;
reg [31:0]              operandrae1q;
reg [31:0]              operandrbe1q;
reg [`EXCEPTIONW-1:0]  exceptione1q;

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    valide1q      <= 1'b0;
    ctrle1q       <= `PCINFOW'b0;
    pce1q         <= 32'b0;
    npce1q        <= 32'b0;
    opcodee1q     <= 32'b0;
    operandrae1q <= 32'b0;
    operandrbe1q <= 32'b0;
    exceptione1q  <= `EXCEPTIONW'b0;
end
else if (issuestalli)
    ;
else if ((issuevalidi && issueaccepti) && ~(squashe1e2o || squashe1e2i))
begin
    valide1q                  <= 1'b1;
    ctrle1q[`PCINFOALU]      <= ~(issuelsui | issuecsri | issuedivi | issuemuli);
    ctrle1q[`PCINFOLOAD]     <= issuelsui &  issuerdvalidi & ~takeinterrupti; 
    ctrle1q[`PCINFOSTORE]    <= issuelsui & ~issuerdvalidi & ~takeinterrupti;
    ctrle1q[`PCINFOCSR]      <= issuecsri & ~takeinterrupti;
    ctrle1q[`PCINFODIV]      <= issuedivi & ~takeinterrupti;
    ctrle1q[`PCINFOMUL]      <= issuemuli & ~takeinterrupti;
    ctrle1q[`PCINFOBRANCH]   <= issuebranchi & ~takeinterrupti;
    ctrle1q[`PCINFORDVALID] <= issuerdvalidi & ~takeinterrupti;
    ctrle1q[`PCINFOINTR]     <= takeinterrupti;
    ctrle1q[`PCINFOCOMPLETE] <= 1'b1;

    pce1q         <= issuepci;
    npce1q        <= issuebranchtakeni ? issuebranchtargeti : issuepci + 32'd4;
    opcodee1q     <= issueopcodei;
    operandrae1q <= issueoperandrai;
    operandrbe1q <= issueoperandrbi;
    exceptione1q  <= (|issueexceptioni) ? issueexceptioni : 
                       branchmisalignedw  ? `EXCEPTIONMISALIGNEDFETCH : `EXCEPTIONW'b0;
end
else
begin
    valide1q      <= 1'b0;
    ctrle1q       <= `PCINFOW'b0;
    pce1q         <= 32'b0;
    npce1q        <= 32'b0;
    opcodee1q     <= 32'b0;
    operandrae1q <= 32'b0;
    operandrbe1q <= 32'b0;
    exceptione1q  <= `EXCEPTIONW'b0;
end

wire   alue1w        = ctrle1q[`PCINFOALU];
assign loade1o       = ctrle1q[`PCINFOLOAD];
assign storee1o      = ctrle1q[`PCINFOSTORE];
wire   csre1w        = ctrle1q[`PCINFOCSR];
wire   dive1w        = ctrle1q[`PCINFODIV];
assign mule1o        = ctrle1q[`PCINFOMUL];
assign branche1o     = ctrle1q[`PCINFOBRANCH];
assign rde1o         = {5{ctrle1q[`PCINFORDVALID]}} & opcodee1q[`RDIDXR];
assign pce1o         = pce1q;
assign opcodee1o     = opcodee1q;
assign operandrae1o = operandrae1q;
assign operandrbe1o = operandrbe1q;

reg                     valide2q;
reg [`PCINFOW-1:0]     ctrle2q;
reg                     csrwre2q;
reg [31:0]              csrwdatae2q;
reg [31:0]              resulte2q;
reg [31:0]              pce2q;
reg [31:0]              npce2q;
reg [31:0]              opcodee2q;
reg [31:0]              operandrae2q;
reg [31:0]              operandrbe2q;
reg [`EXCEPTIONW-1:0]  exceptione2q;

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    valide2q      <= 1'b0;
    ctrle2q       <= `PCINFOW'b0;
    csrwre2q     <= 1'b0;
    csrwdatae2q  <= 32'b0;
    pce2q         <= 32'b0;
    npce2q        <= 32'b0;
    opcodee2q     <= 32'b0;
    operandrae2q <= 32'b0;
    operandrbe2q <= 32'b0;
    resulte2q     <= 32'b0;
    exceptione2q  <= `EXCEPTIONW'b0;
end
else if (issuestalli)
    ;
else if (squashe1e2o || squashe1e2i)
begin
    valide2q      <= 1'b0;
    ctrle2q       <= `PCINFOW'b0;
    csrwre2q     <= 1'b0;
    csrwdatae2q  <= 32'b0;
    pce2q         <= 32'b0;
    npce2q        <= 32'b0;
    opcodee2q     <= 32'b0;
    operandrae2q <= 32'b0;
    operandrbe2q <= 32'b0;
    resulte2q     <= 32'b0;
    exceptione2q  <= `EXCEPTIONW'b0;
end
else
begin
    valide2q      <= valide1q;
    ctrle2q       <= ctrle1q;
    csrwre2q     <= csrresultwritee1i;
    csrwdatae2q  <= csrresultwdatae1i;
    pce2q         <= pce1q;
    npce2q        <= npce1q;
    opcodee2q     <= opcodee1q;
    operandrae2q <= operandrae1q;
    operandrbe2q <= operandrbe1q;

    
    if (ctrle1q[`PCINFOINTR])
        exceptione2q  <= `EXCEPTIONINTERRUPT;
    
    else if (|exceptione1q)
    begin
        valide2q      <= 1'b0;
        exceptione2q  <= exceptione1q;
    end
    else
        exceptione2q  <= csrresultexceptione1i;

    if (ctrle1q[`PCINFODIV])
        resulte2q <= divresulti; 
    else if (ctrle1q[`PCINFOCSR])
        resulte2q <= csrresultvaluee1i;
    else
        resulte2q <= aluresulte1i;
end

reg [31:0] resulte2r;

wire valide2w      = valide2q & ~issuestalli;

always @ *
begin
    
    resulte2r = resulte2q;

    if (SUPPORTLOADBYPASS && valide2w && (ctrle2q[`PCINFOLOAD] || ctrle2q[`PCINFOSTORE]))
        resulte2r = memresulte2i;
    else if (SUPPORTMULBYPASS && valide2w && ctrle2q[`PCINFOMUL])
        resulte2r = mulresulte2i;
end

wire   loadstoree2w = ctrle2q[`PCINFOLOAD] | ctrle2q[`PCINFOSTORE];
assign loade2o       = ctrle2q[`PCINFOLOAD];
assign mule2o        = ctrle2q[`PCINFOMUL];
assign rde2o         = {5{(valide2w && ctrle2q[`PCINFORDVALID] && ~stallo)}} & opcodee2q[`RDIDXR];
assign resulte2o     = resulte2r;

assign stallo         = (ctrle1q[`PCINFODIV] && ~divcompletei) || ((ctrle2q[`PCINFOLOAD] | ctrle2q[`PCINFOSTORE]) & ~memcompletei);

reg [`EXCEPTIONW-1:0] exceptione2r;
always @ *
begin
    if (valide2q && (ctrle2q[`PCINFOLOAD] || ctrle2q[`PCINFOSTORE]) && memcompletei)
        exceptione2r = memexceptione2i;
    else
        exceptione2r = exceptione2q;
end

assign squashe1e2w = |exceptione2r;

reg squashe1e2q;

always @ (posedge clki or posedge rsti)
if (rsti)
    squashe1e2q <= 1'b0;
else if (~issuestalli)
    squashe1e2q <= squashe1e2w;

assign squashe1e2o = squashe1e2w | squashe1e2q;

reg                     validwbq;
reg [`PCINFOW-1:0]     ctrlwbq;
reg                     csrwrwbq;
reg [31:0]              csrwdatawbq;
reg [31:0]              resultwbq;
reg [31:0]              pcwbq;
reg [31:0]              npcwbq;
reg [31:0]              opcodewbq;
reg [31:0]              operandrawbq;
reg [31:0]              operandrbwbq;
reg [`EXCEPTIONW-1:0]  exceptionwbq;

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    validwbq      <= 1'b0;
    ctrlwbq       <= `PCINFOW'b0;
    csrwrwbq     <= 1'b0;
    csrwdatawbq  <= 32'b0;
    pcwbq         <= 32'b0;
    npcwbq        <= 32'b0;
    opcodewbq     <= 32'b0;
    operandrawbq <= 32'b0;
    operandrbwbq <= 32'b0;
    resultwbq     <= 32'b0;
    exceptionwbq  <= `EXCEPTIONW'b0;
end
else if (issuestalli)
    ;
else if (squashwbi)
begin
    validwbq      <= 1'b0;
    ctrlwbq       <= `PCINFOW'b0;
    csrwrwbq     <= 1'b0;
    csrwdatawbq  <= 32'b0;
    pcwbq         <= 32'b0;
    npcwbq        <= 32'b0;
    opcodewbq     <= 32'b0;
    operandrawbq <= 32'b0;
    operandrbwbq <= 32'b0;
    resultwbq     <= 32'b0;
    exceptionwbq  <= `EXCEPTIONW'b0;
end
else
begin
    
    case (exceptione2r)
    `EXCEPTIONMISALIGNEDLOAD,
    `EXCEPTIONFAULTLOAD,
    `EXCEPTIONMISALIGNEDSTORE,
    `EXCEPTIONFAULTSTORE,
    `EXCEPTIONPAGEFAULTLOAD,
    `EXCEPTIONPAGEFAULTSTORE:
        validwbq      <= 1'b0;
    default:
        validwbq      <= valide2q;
    endcase

    csrwrwbq     <= csrwre2q;  
    csrwdatawbq  <= csrwdatae2q;

    
    if (|exceptione2r)
        ctrlwbq       <= ctrle2q & ~(1 << `PCINFORDVALID);
    else
        ctrlwbq       <= ctrle2q;

    pcwbq         <= pce2q;
    npcwbq        <= npce2q;
    opcodewbq     <= opcodee2q;
    operandrawbq <= operandrae2q;
    operandrbwbq <= operandrbe2q;
    exceptionwbq  <= exceptione2r;

    if (valide2w && (ctrle2q[`PCINFOLOAD] || ctrle2q[`PCINFOSTORE]))
        resultwbq <= memresulte2i;
    else if (valide2w && ctrle2q[`PCINFOMUL])
        resultwbq <= mulresulte2i;
    else
        resultwbq <= resulte2q;
end

wire completewbw     = ctrlwbq[`PCINFOCOMPLETE] & ~issuestalli;

assign validwbo      = validwbq & ~issuestalli;
assign csrwbo        = ctrlwbq[`PCINFOCSR] & ~issuestalli; 
assign rdwbo         = {5{(validwbo && ctrlwbq[`PCINFORDVALID] && ~stallo)}} & opcodewbq[`RDIDXR];
assign resultwbo     = resultwbq;
assign pcwbo         = pcwbq;
assign opcodewbo     = opcodewbq;
assign operandrawbo = operandrawbq;
assign operandrbwbo = operandrbwbq;

assign exceptionwbo  = exceptionwbq;

assign csrwritewbo  = csrwrwbq;
assign csrwaddrwbo  = opcodewbq[31:20];
assign csrwdatawbo  = csrwdatawbq;

`ifdef verilator
riscvtracesim
utraced
(
     .validi(issuevalidi)
    ,.pci(issuepci)
    ,.opcodei(issueopcodei)
);

riscvtracesim
utracewb
(
     .validi(validwbo)
    ,.pci(pcwbo)
    ,.opcodei(opcodewbo)
);
`endif

endmodule
module riscvregfile
#(
     parameter SUPPORTREGFILEXILINX = 0
)
(
    
     input           clki
    ,input           rsti
    ,input  [  4:0]  rd0i
    ,input  [ 31:0]  rd0valuei
    ,input  [  4:0]  ra0i
    ,input  [  4:0]  rb0i

    
    ,output [ 31:0]  ra0valueo
    ,output [ 31:0]  rb0valueo
);

generate
if (SUPPORTREGFILEXILINX)
begin: REGFILEXILINXSINGLE

    riscvxilinx2r1w
    ureg
    (
        
         .clki(clki)
        ,.rsti(rsti)
        ,.rd0i(rd0i)
        ,.rd0valuei(rd0valuei)
        ,.rai(ra0i)
        ,.rbi(rb0i)

        
        ,.ravalueo(ra0valueo)
        ,.rbvalueo(rb0valueo)
    );
end
else
begin: REGFILE
    reg [31:0] regr1q;
    reg [31:0] regr2q;
    reg [31:0] regr3q;
    reg [31:0] regr4q;
    reg [31:0] regr5q;
    reg [31:0] regr6q;
    reg [31:0] regr7q;
    reg [31:0] regr8q;
    reg [31:0] regr9q;
    reg [31:0] regr10q;
    reg [31:0] regr11q;
    reg [31:0] regr12q;
    reg [31:0] regr13q;
    reg [31:0] regr14q;
    reg [31:0] regr15q;
    reg [31:0] regr16q;
    reg [31:0] regr17q;
    reg [31:0] regr18q;
    reg [31:0] regr19q;
    reg [31:0] regr20q;
    reg [31:0] regr21q;
    reg [31:0] regr22q;
    reg [31:0] regr23q;
    reg [31:0] regr24q;
    reg [31:0] regr25q;
    reg [31:0] regr26q;
    reg [31:0] regr27q;
    reg [31:0] regr28q;
    reg [31:0] regr29q;
    reg [31:0] regr30q;
    reg [31:0] regr31q;

    
    wire [31:0] x0zerow = 32'b0;
    wire [31:0] x1raw   = regr1q;
    wire [31:0] x2spw   = regr2q;
    wire [31:0] x3gpw   = regr3q;
    wire [31:0] x4tpw   = regr4q;
    wire [31:0] x5t0w   = regr5q;
    wire [31:0] x6t1w   = regr6q;
    wire [31:0] x7t2w   = regr7q;
    wire [31:0] x8s0w   = regr8q;
    wire [31:0] x9s1w   = regr9q;
    wire [31:0] x10a0w  = regr10q;
    wire [31:0] x11a1w  = regr11q;
    wire [31:0] x12a2w  = regr12q;
    wire [31:0] x13a3w  = regr13q;
    wire [31:0] x14a4w  = regr14q;
    wire [31:0] x15a5w  = regr15q;
    wire [31:0] x16a6w  = regr16q;
    wire [31:0] x17a7w  = regr17q;
    wire [31:0] x18s2w  = regr18q;
    wire [31:0] x19s3w  = regr19q;
    wire [31:0] x20s4w  = regr20q;
    wire [31:0] x21s5w  = regr21q;
    wire [31:0] x22s6w  = regr22q;
    wire [31:0] x23s7w  = regr23q;
    wire [31:0] x24s8w  = regr24q;
    wire [31:0] x25s9w  = regr25q;
    wire [31:0] x26s10w = regr26q;
    wire [31:0] x27s11w = regr27q;
    wire [31:0] x28t3w  = regr28q;
    wire [31:0] x29t4w  = regr29q;
    wire [31:0] x30t5w  = regr30q;
    wire [31:0] x31t6w  = regr31q;

    
    
    

    
    always @ (posedge clki )
    if (rsti)
    begin
        regr1q       <= 32'h00000000;
        regr2q       <= 32'h00000000;
        regr3q       <= 32'h00000000;
        regr4q       <= 32'h00000000;
        regr5q       <= 32'h00000000;
        regr6q       <= 32'h00000000;
        regr7q       <= 32'h00000000;
        regr8q       <= 32'h00000000;
        regr9q       <= 32'h00000000;
        regr10q      <= 32'h00000000;
        regr11q      <= 32'h00000000;
        regr12q      <= 32'h00000000;
        regr13q      <= 32'h00000000;
        regr14q      <= 32'h00000000;
        regr15q      <= 32'h00000000;
        regr16q      <= 32'h00000000;
        regr17q      <= 32'h00000000;
        regr18q      <= 32'h00000000;
        regr19q      <= 32'h00000000;
        regr20q      <= 32'h00000000;
        regr21q      <= 32'h00000000;
        regr22q      <= 32'h00000000;
        regr23q      <= 32'h00000000;
        regr24q      <= 32'h00000000;
        regr25q      <= 32'h00000000;
        regr26q      <= 32'h00000000;
        regr27q      <= 32'h00000000;
        regr28q      <= 32'h00000000;
        regr29q      <= 32'h00000000;
        regr30q      <= 32'h00000000;
        regr31q      <= 32'h00000000;
    end
    else
    begin
        if      (rd0i == 5'd1) regr1q <= rd0valuei;
        if      (rd0i == 5'd2) regr2q <= rd0valuei;
        if      (rd0i == 5'd3) regr3q <= rd0valuei;
        if      (rd0i == 5'd4) regr4q <= rd0valuei;
        if      (rd0i == 5'd5) regr5q <= rd0valuei;
        if      (rd0i == 5'd6) regr6q <= rd0valuei;
        if      (rd0i == 5'd7) regr7q <= rd0valuei;
        if      (rd0i == 5'd8) regr8q <= rd0valuei;
        if      (rd0i == 5'd9) regr9q <= rd0valuei;
        if      (rd0i == 5'd10) regr10q <= rd0valuei;
        if      (rd0i == 5'd11) regr11q <= rd0valuei;
        if      (rd0i == 5'd12) regr12q <= rd0valuei;
        if      (rd0i == 5'd13) regr13q <= rd0valuei;
        if      (rd0i == 5'd14) regr14q <= rd0valuei;
        if      (rd0i == 5'd15) regr15q <= rd0valuei;
        if      (rd0i == 5'd16) regr16q <= rd0valuei;
        if      (rd0i == 5'd17) regr17q <= rd0valuei;
        if      (rd0i == 5'd18) regr18q <= rd0valuei;
        if      (rd0i == 5'd19) regr19q <= rd0valuei;
        if      (rd0i == 5'd20) regr20q <= rd0valuei;
        if      (rd0i == 5'd21) regr21q <= rd0valuei;
        if      (rd0i == 5'd22) regr22q <= rd0valuei;
        if      (rd0i == 5'd23) regr23q <= rd0valuei;
        if      (rd0i == 5'd24) regr24q <= rd0valuei;
        if      (rd0i == 5'd25) regr25q <= rd0valuei;
        if      (rd0i == 5'd26) regr26q <= rd0valuei;
        if      (rd0i == 5'd27) regr27q <= rd0valuei;
        if      (rd0i == 5'd28) regr28q <= rd0valuei;
        if      (rd0i == 5'd29) regr29q <= rd0valuei;
        if      (rd0i == 5'd30) regr30q <= rd0valuei;
        if      (rd0i == 5'd31) regr31q <= rd0valuei;
    end

    
    
    
    reg [31:0] ra0valuer;
    reg [31:0] rb0valuer;
    always @ *
    begin
        case (ra0i)
        5'd1: ra0valuer = regr1q;
        5'd2: ra0valuer = regr2q;
        5'd3: ra0valuer = regr3q;
        5'd4: ra0valuer = regr4q;
        5'd5: ra0valuer = regr5q;
        5'd6: ra0valuer = regr6q;
        5'd7: ra0valuer = regr7q;
        5'd8: ra0valuer = regr8q;
        5'd9: ra0valuer = regr9q;
        5'd10: ra0valuer = regr10q;
        5'd11: ra0valuer = regr11q;
        5'd12: ra0valuer = regr12q;
        5'd13: ra0valuer = regr13q;
        5'd14: ra0valuer = regr14q;
        5'd15: ra0valuer = regr15q;
        5'd16: ra0valuer = regr16q;
        5'd17: ra0valuer = regr17q;
        5'd18: ra0valuer = regr18q;
        5'd19: ra0valuer = regr19q;
        5'd20: ra0valuer = regr20q;
        5'd21: ra0valuer = regr21q;
        5'd22: ra0valuer = regr22q;
        5'd23: ra0valuer = regr23q;
        5'd24: ra0valuer = regr24q;
        5'd25: ra0valuer = regr25q;
        5'd26: ra0valuer = regr26q;
        5'd27: ra0valuer = regr27q;
        5'd28: ra0valuer = regr28q;
        5'd29: ra0valuer = regr29q;
        5'd30: ra0valuer = regr30q;
        5'd31: ra0valuer = regr31q;
        default : ra0valuer = 32'h00000000;
        endcase

        case (rb0i)
        5'd1: rb0valuer = regr1q;
        5'd2: rb0valuer = regr2q;
        5'd3: rb0valuer = regr3q;
        5'd4: rb0valuer = regr4q;
        5'd5: rb0valuer = regr5q;
        5'd6: rb0valuer = regr6q;
        5'd7: rb0valuer = regr7q;
        5'd8: rb0valuer = regr8q;
        5'd9: rb0valuer = regr9q;
        5'd10: rb0valuer = regr10q;
        5'd11: rb0valuer = regr11q;
        5'd12: rb0valuer = regr12q;
        5'd13: rb0valuer = regr13q;
        5'd14: rb0valuer = regr14q;
        5'd15: rb0valuer = regr15q;
        5'd16: rb0valuer = regr16q;
        5'd17: rb0valuer = regr17q;
        5'd18: rb0valuer = regr18q;
        5'd19: rb0valuer = regr19q;
        5'd20: rb0valuer = regr20q;
        5'd21: rb0valuer = regr21q;
        5'd22: rb0valuer = regr22q;
        5'd23: rb0valuer = regr23q;
        5'd24: rb0valuer = regr24q;
        5'd25: rb0valuer = regr25q;
        5'd26: rb0valuer = regr26q;
        5'd27: rb0valuer = regr27q;
        5'd28: rb0valuer = regr28q;
        5'd29: rb0valuer = regr29q;
        5'd30: rb0valuer = regr30q;
        5'd31: rb0valuer = regr31q;
        default : rb0valuer = 32'h00000000;
        endcase
    end

    assign ra0valueo = ra0valuer;
    assign rb0valueo = rb0valuer;

    
    
    
    `ifdef verilator
    function [31:0] getregister; /*verilator public*/
        input [4:0] r;
    begin
        case (r)
        5'd1: getregister = regr1q;
        5'd2: getregister = regr2q;
        5'd3: getregister = regr3q;
        5'd4: getregister = regr4q;
        5'd5: getregister = regr5q;
        5'd6: getregister = regr6q;
        5'd7: getregister = regr7q;
        5'd8: getregister = regr8q;
        5'd9: getregister = regr9q;
        5'd10: getregister = regr10q;
        5'd11: getregister = regr11q;
        5'd12: getregister = regr12q;
        5'd13: getregister = regr13q;
        5'd14: getregister = regr14q;
        5'd15: getregister = regr15q;
        5'd16: getregister = regr16q;
        5'd17: getregister = regr17q;
        5'd18: getregister = regr18q;
        5'd19: getregister = regr19q;
        5'd20: getregister = regr20q;
        5'd21: getregister = regr21q;
        5'd22: getregister = regr22q;
        5'd23: getregister = regr23q;
        5'd24: getregister = regr24q;
        5'd25: getregister = regr25q;
        5'd26: getregister = regr26q;
        5'd27: getregister = regr27q;
        5'd28: getregister = regr28q;
        5'd29: getregister = regr29q;
        5'd30: getregister = regr30q;
        5'd31: getregister = regr31q;
        default : getregister = 32'h00000000;
        endcase
    end
    endfunction
    
    
    
    function setregister; /*verilator public*/
        input [4:0] r;
        input [31:0] value;
    begin
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    end
    endfunction
    `endif

end
endgenerate

endmodule

module top
#(
     parameter BOOTVECTOR      = 32'h00002000
    ,parameter COREID          = 0
    ,parameter TCMMEMBASE     = 0
    ,parameter MEMCACHEADDRMIN = 0
    ,parameter MEMCACHEADDRMAX = 32'hffffffff
)
(
    
     input           clki
    ,input           rsti
    ,input           rstcpui
    ,input           axiiawreadyi
    ,input           axiiwreadyi
    ,input           axiibvalidi
    ,input  [  1:0]  axiibrespi
    ,input           axiiarreadyi
    ,input           axiirvalidi
    ,input  [ 31:0]  axiirdatai
    ,input  [  1:0]  axiirrespi
    ,input           axitawvalidi
    ,input  [ 31:0]  axitawaddri
    ,input  [  3:0]  axitawidi
    ,input  [  7:0]  axitawleni
    ,input  [  1:0]  axitawbursti
    ,input           axitwvalidi
    ,input  [ 31:0]  axitwdatai
    ,input  [  3:0]  axitwstrbi
    ,input           axitwlasti
    ,input           axitbreadyi
    ,input           axitarvalidi
    ,input  [ 31:0]  axitaraddri
    ,input  [  3:0]  axitaridi
    ,input  [  7:0]  axitarleni
    ,input  [  1:0]  axitarbursti
    ,input           axitrreadyi
    ,input  [ 31:0]  intri

    
    ,output          axiiawvalido
    ,output [ 31:0]  axiiawaddro
    ,output          axiiwvalido
    ,output [ 31:0]  axiiwdatao
    ,output [  3:0]  axiiwstrbo
    ,output          axiibreadyo
    ,output          axiiarvalido
    ,output [ 31:0]  axiiaraddro
    ,output          axiirreadyo
    ,output          axitawreadyo
    ,output          axitwreadyo
    ,output          axitbvalido
    ,output [  1:0]  axitbrespo
    ,output [  3:0]  axitbido
    ,output          axitarreadyo
    ,output          axitrvalido
    ,output [ 31:0]  axitrdatao
    ,output [  1:0]  axitrrespo
    ,output [  3:0]  axitrido
    ,output          axitrlasto
);

wire  [ 31:0]  ifetchpcw;
wire  [ 31:0]  dporttcmdatardw;
wire           dporttcmcacheablew;
wire           dportflushw;
wire  [  3:0]  dporttcmwrw;
wire           ifetchrdw;
wire           dportaxiacceptw;
wire           dportcacheablew;
wire           dporttcmflushw;
wire  [ 10:0]  dportresptagw;
wire  [ 10:0]  dportaxiresptagw;
wire           ifetchacceptw;
wire  [ 31:0]  dportdatardw;
wire           dporttcminvalidatew;
wire           dportackw;
wire  [ 10:0]  dportaxireqtagw;
wire  [ 31:0]  dportdatawrw;
wire           dportinvalidatew;
wire  [ 10:0]  dporttcmreqtagw;
wire  [ 31:0]  dporttcmaddrw;
wire           dportaxierrorw;
wire           dporttcmackw;
wire           dporttcmrdw;
wire  [ 10:0]  dporttcmresptagw;
wire           dportwritebackw;
wire  [ 31:0]  cpuidw = COREID;
wire           dportrdw;
wire           dportaxiackw;
wire           dportaxirdw;
wire  [ 31:0]  dportaxidatardw;
wire           dportaxiinvalidatew;
wire  [ 31:0]  bootvectorw = BOOTVECTOR;
wire  [ 31:0]  dportaddrw;
wire           ifetcherrorw;
wire  [ 31:0]  dporttcmdatawrw;
wire           ifetchflushw;
wire  [ 31:0]  dportaxiaddrw;
wire           dporterrorw;
wire           dporttcmacceptw;
wire           ifetchinvalidatew;
wire           dportaxiwritebackw;
wire  [  3:0]  dportwrw;
wire           ifetchvalidw;
wire  [ 31:0]  dportaxidatawrw;
wire  [ 10:0]  dportreqtagw;
wire  [ 31:0]  ifetchinstw;
wire           dportaxicacheablew;
wire           dporttcmwritebackw;
wire  [  3:0]  dportaxiwrw;
wire           dportaxiflushw;
wire           dporttcmerrorw;
wire           dportacceptw;


riscvcore
#(
     .MEMCACHEADDRMIN(MEMCACHEADDRMIN)
    ,.MEMCACHEADDRMAX(MEMCACHEADDRMAX)
)
ucore
(
    
     .clki(clki)
    ,.rsti(rstcpui)
    ,.memddatardi(dportdatardw)
    ,.memdaccepti(dportacceptw)
    ,.memdacki(dportackw)
    ,.memderrori(dporterrorw)
    ,.memdresptagi(dportresptagw)
    ,.memiaccepti(ifetchacceptw)
    ,.memivalidi(ifetchvalidw)
    ,.memierrori(ifetcherrorw)
    ,.memiinsti(ifetchinstw)
    ,.intri(intri[0:0])
    ,.resetvectori(bootvectorw)
    ,.cpuidi(cpuidw)

    
    ,.memdaddro(dportaddrw)
    ,.memddatawro(dportdatawrw)
    ,.memdrdo(dportrdw)
    ,.memdwro(dportwrw)
    ,.memdcacheableo(dportcacheablew)
    ,.memdreqtago(dportreqtagw)
    ,.memdinvalidateo(dportinvalidatew)
    ,.memdwritebacko(dportwritebackw)
    ,.memdflusho(dportflushw)
    ,.memirdo(ifetchrdw)
    ,.memiflusho(ifetchflushw)
    ,.memiinvalidateo(ifetchinvalidatew)
    ,.memipco(ifetchpcw)
);


dportmux
#(
     .TCMMEMBASE(TCMMEMBASE)
)
udmux
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.memaddri(dportaddrw)
    ,.memdatawri(dportdatawrw)
    ,.memrdi(dportrdw)
    ,.memwri(dportwrw)
    ,.memcacheablei(dportcacheablew)
    ,.memreqtagi(dportreqtagw)
    ,.meminvalidatei(dportinvalidatew)
    ,.memwritebacki(dportwritebackw)
    ,.memflushi(dportflushw)
    ,.memtcmdatardi(dporttcmdatardw)
    ,.memtcmaccepti(dporttcmacceptw)
    ,.memtcmacki(dporttcmackw)
    ,.memtcmerrori(dporttcmerrorw)
    ,.memtcmresptagi(dporttcmresptagw)
    ,.memextdatardi(dportaxidatardw)
    ,.memextaccepti(dportaxiacceptw)
    ,.memextacki(dportaxiackw)
    ,.memexterrori(dportaxierrorw)
    ,.memextresptagi(dportaxiresptagw)

    
    ,.memdatardo(dportdatardw)
    ,.memaccepto(dportacceptw)
    ,.memacko(dportackw)
    ,.memerroro(dporterrorw)
    ,.memresptago(dportresptagw)
    ,.memtcmaddro(dporttcmaddrw)
    ,.memtcmdatawro(dporttcmdatawrw)
    ,.memtcmrdo(dporttcmrdw)
    ,.memtcmwro(dporttcmwrw)
    ,.memtcmcacheableo(dporttcmcacheablew)
    ,.memtcmreqtago(dporttcmreqtagw)
    ,.memtcminvalidateo(dporttcminvalidatew)
    ,.memtcmwritebacko(dporttcmwritebackw)
    ,.memtcmflusho(dporttcmflushw)
    ,.memextaddro(dportaxiaddrw)
    ,.memextdatawro(dportaxidatawrw)
    ,.memextrdo(dportaxirdw)
    ,.memextwro(dportaxiwrw)
    ,.memextcacheableo(dportaxicacheablew)
    ,.memextreqtago(dportaxireqtagw)
    ,.memextinvalidateo(dportaxiinvalidatew)
    ,.memextwritebacko(dportaxiwritebackw)
    ,.memextflusho(dportaxiflushw)
);


tcmmem
utcm
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.memirdi(ifetchrdw)
    ,.memiflushi(ifetchflushw)
    ,.memiinvalidatei(ifetchinvalidatew)
    ,.memipci(ifetchpcw)
    ,.memdaddri(dporttcmaddrw)
    ,.memddatawri(dporttcmdatawrw)
    ,.memdrdi(dporttcmrdw)
    ,.memdwri(dporttcmwrw)
    ,.memdcacheablei(dporttcmcacheablew)
    ,.memdreqtagi(dporttcmreqtagw)
    ,.memdinvalidatei(dporttcminvalidatew)
    ,.memdwritebacki(dporttcmwritebackw)
    ,.memdflushi(dporttcmflushw)
    ,.axiawvalidi(axitawvalidi)
    ,.axiawaddri(axitawaddri)
    ,.axiawidi(axitawidi)
    ,.axiawleni(axitawleni)
    ,.axiawbursti(axitawbursti)
    ,.axiwvalidi(axitwvalidi)
    ,.axiwdatai(axitwdatai)
    ,.axiwstrbi(axitwstrbi)
    ,.axiwlasti(axitwlasti)
    ,.axibreadyi(axitbreadyi)
    ,.axiarvalidi(axitarvalidi)
    ,.axiaraddri(axitaraddri)
    ,.axiaridi(axitaridi)
    ,.axiarleni(axitarleni)
    ,.axiarbursti(axitarbursti)
    ,.axirreadyi(axitrreadyi)

    
    ,.memiaccepto(ifetchacceptw)
    ,.memivalido(ifetchvalidw)
    ,.memierroro(ifetcherrorw)
    ,.memiinsto(ifetchinstw)
    ,.memddatardo(dporttcmdatardw)
    ,.memdaccepto(dporttcmacceptw)
    ,.memdacko(dporttcmackw)
    ,.memderroro(dporttcmerrorw)
    ,.memdresptago(dporttcmresptagw)
    ,.axiawreadyo(axitawreadyo)
    ,.axiwreadyo(axitwreadyo)
    ,.axibvalido(axitbvalido)
    ,.axibrespo(axitbrespo)
    ,.axibido(axitbido)
    ,.axiarreadyo(axitarreadyo)
    ,.axirvalido(axitrvalido)
    ,.axirdatao(axitrdatao)
    ,.axirrespo(axitrrespo)
    ,.axirido(axitrido)
    ,.axirlasto(axitrlasto)
);


dportaxi
uaxi
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.memaddri(dportaxiaddrw)
    ,.memdatawri(dportaxidatawrw)
    ,.memrdi(dportaxirdw)
    ,.memwri(dportaxiwrw)
    ,.memcacheablei(dportaxicacheablew)
    ,.memreqtagi(dportaxireqtagw)
    ,.meminvalidatei(dportaxiinvalidatew)
    ,.memwritebacki(dportaxiwritebackw)
    ,.memflushi(dportaxiflushw)
    ,.axiawreadyi(axiiawreadyi)
    ,.axiwreadyi(axiiwreadyi)
    ,.axibvalidi(axiibvalidi)
    ,.axibrespi(axiibrespi)
    ,.axiarreadyi(axiiarreadyi)
    ,.axirvalidi(axiirvalidi)
    ,.axirdatai(axiirdatai)
    ,.axirrespi(axiirrespi)

    
    ,.memdatardo(dportaxidatardw)
    ,.memaccepto(dportaxiacceptw)
    ,.memacko(dportaxiackw)
    ,.memerroro(dportaxierrorw)
    ,.memresptago(dportaxiresptagw)
    ,.axiawvalido(axiiawvalido)
    ,.axiawaddro(axiiawaddro)
    ,.axiwvalido(axiiwvalido)
    ,.axiwdatao(axiiwdatao)
    ,.axiwstrbo(axiiwstrbo)
    ,.axibreadyo(axiibreadyo)
    ,.axiarvalido(axiiarvalido)
    ,.axiaraddro(axiiaraddro)
    ,.axirreadyo(axiirreadyo)
);



endmodule

module riscvtcmwrapper
#(
     parameter BOOTVECTOR      = 0
    ,parameter COREID          = 0
    ,parameter TCMMEMBASE     = 0
    ,parameter MEMCACHEADDRMIN = 0
    ,parameter MEMCACHEADDRMAX = 32'hffffffff
)
(
    
     input           clki
    ,input           rsti
    ,input           rstcpui
    ,input           axiiawreadyi
    ,input           axiiwreadyi
    ,input           axiibvalidi
    ,input  [  1:0]  axiibrespi
    ,input  [  3:0]  axiibidi
    ,input           axiiarreadyi
    ,input           axiirvalidi
    ,input  [ 31:0]  axiirdatai
    ,input  [  1:0]  axiirrespi
    ,input  [  3:0]  axiiridi
    ,input           axiirlasti
    ,input           axitawvalidi
    ,input  [ 31:0]  axitawaddri
    ,input  [  3:0]  axitawidi
    ,input  [  7:0]  axitawleni
    ,input  [  1:0]  axitawbursti
    ,input           axitwvalidi
    ,input  [ 31:0]  axitwdatai
    ,input  [  3:0]  axitwstrbi
    ,input           axitwlasti
    ,input           axitbreadyi
    ,input           axitarvalidi
    ,input  [ 31:0]  axitaraddri
    ,input  [  3:0]  axitaridi
    ,input  [  7:0]  axitarleni
    ,input  [  1:0]  axitarbursti
    ,input           axitrreadyi
    ,input  [ 31:0]  intri

    
    ,output          axiiawvalido
    ,output [ 31:0]  axiiawaddro
    ,output [  3:0]  axiiawido
    ,output [  7:0]  axiiawleno
    ,output [  1:0]  axiiawbursto
    ,output          axiiwvalido
    ,output [ 31:0]  axiiwdatao
    ,output [  3:0]  axiiwstrbo
    ,output          axiiwlasto
    ,output          axiibreadyo
    ,output          axiiarvalido
    ,output [ 31:0]  axiiaraddro
    ,output [  3:0]  axiiarido
    ,output [  7:0]  axiiarleno
    ,output [  1:0]  axiiarbursto
    ,output          axiirreadyo
    ,output          axitawreadyo
    ,output          axitwreadyo
    ,output          axitbvalido
    ,output [  1:0]  axitbrespo
    ,output [  3:0]  axitbido
    ,output          axitarreadyo
    ,output          axitrvalido
    ,output [ 31:0]  axitrdatao
    ,output [  1:0]  axitrrespo
    ,output [  3:0]  axitrido
    ,output          axitrlasto
);

wire  [ 31:0]  ifetchpcw;
wire  [ 31:0]  dporttcmdatardw;
wire           dporttcmcacheablew;
wire           dportflushw;
wire  [  3:0]  dporttcmwrw;
wire           ifetchrdw;
wire           dportaxiacceptw;
wire           dportcacheablew;
wire           dporttcmflushw;
wire  [ 10:0]  dportresptagw;
wire  [ 10:0]  dportaxiresptagw;
wire           ifetchacceptw;
wire  [ 31:0]  dportdatardw;
wire           dporttcminvalidatew;
wire           dportackw;
wire  [ 10:0]  dportaxireqtagw;
wire  [ 31:0]  dportdatawrw;
wire           dportinvalidatew;
wire  [ 10:0]  dporttcmreqtagw;
wire  [ 31:0]  dporttcmaddrw;
wire           dportaxierrorw;
wire           dporttcmackw;
wire           dporttcmrdw;
wire  [ 10:0]  dporttcmresptagw;
wire           dportwritebackw;
wire  [ 31:0]  cpuidw = COREID;
wire           dportrdw;
wire           dportaxiackw;
wire           dportaxirdw;
wire  [ 31:0]  dportaxidatardw;
wire           dportaxiinvalidatew;
wire  [ 31:0]  bootvectorw = BOOTVECTOR;
wire  [ 31:0]  dportaddrw;
wire           ifetcherrorw;
wire  [ 31:0]  dporttcmdatawrw;
wire           ifetchflushw;
wire  [ 31:0]  dportaxiaddrw;
wire           dporterrorw;
wire           dporttcmacceptw;
wire           ifetchinvalidatew;
wire           dportaxiwritebackw;
wire  [  3:0]  dportwrw;
wire           ifetchvalidw;
wire  [ 31:0]  dportaxidatawrw;
wire  [ 10:0]  dportreqtagw;
wire  [ 31:0]  ifetchinstw;
wire           dportaxicacheablew;
wire           dporttcmwritebackw;
wire  [  3:0]  dportaxiwrw;
wire           dportaxiflushw;
wire           dporttcmerrorw;
wire           dportacceptw;


riscvcore
#(
     .MEMCACHEADDRMIN(MEMCACHEADDRMIN)
    ,.MEMCACHEADDRMAX(MEMCACHEADDRMAX)
)
ucore
(
    
     .clki(clki)
    ,.rsti(rstcpui)
    ,.memddatardi(dportdatardw)
    ,.memdaccepti(dportacceptw)
    ,.memdacki(dportackw)
    ,.memderrori(dporterrorw)
    ,.memdresptagi(dportresptagw)
    ,.memiaccepti(ifetchacceptw)
    ,.memivalidi(ifetchvalidw)
    ,.memierrori(ifetcherrorw)
    ,.memiinsti(ifetchinstw)
    ,.intri(intri[0:0])
    ,.resetvectori(bootvectorw)
    ,.cpuidi(cpuidw)

    
    ,.memdaddro(dportaddrw)
    ,.memddatawro(dportdatawrw)
    ,.memdrdo(dportrdw)
    ,.memdwro(dportwrw)
    ,.memdcacheableo(dportcacheablew)
    ,.memdreqtago(dportreqtagw)
    ,.memdinvalidateo(dportinvalidatew)
    ,.memdwritebacko(dportwritebackw)
    ,.memdflusho(dportflushw)
    ,.memirdo(ifetchrdw)
    ,.memiflusho(ifetchflushw)
    ,.memiinvalidateo(ifetchinvalidatew)
    ,.memipco(ifetchpcw)
);


dportmux
#(
     .TCMMEMBASE(TCMMEMBASE)
)
udmux
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.memaddri(dportaddrw)
    ,.memdatawri(dportdatawrw)
    ,.memrdi(dportrdw)
    ,.memwri(dportwrw)
    ,.memcacheablei(dportcacheablew)
    ,.memreqtagi(dportreqtagw)
    ,.meminvalidatei(dportinvalidatew)
    ,.memwritebacki(dportwritebackw)
    ,.memflushi(dportflushw)
    ,.memtcmdatardi(dporttcmdatardw)
    ,.memtcmaccepti(dporttcmacceptw)
    ,.memtcmacki(dporttcmackw)
    ,.memtcmerrori(dporttcmerrorw)
    ,.memtcmresptagi(dporttcmresptagw)
    ,.memextdatardi(dportaxidatardw)
    ,.memextaccepti(dportaxiacceptw)
    ,.memextacki(dportaxiackw)
    ,.memexterrori(dportaxierrorw)
    ,.memextresptagi(dportaxiresptagw)

    
    ,.memdatardo(dportdatardw)
    ,.memaccepto(dportacceptw)
    ,.memacko(dportackw)
    ,.memerroro(dporterrorw)
    ,.memresptago(dportresptagw)
    ,.memtcmaddro(dporttcmaddrw)
    ,.memtcmdatawro(dporttcmdatawrw)
    ,.memtcmrdo(dporttcmrdw)
    ,.memtcmwro(dporttcmwrw)
    ,.memtcmcacheableo(dporttcmcacheablew)
    ,.memtcmreqtago(dporttcmreqtagw)
    ,.memtcminvalidateo(dporttcminvalidatew)
    ,.memtcmwritebacko(dporttcmwritebackw)
    ,.memtcmflusho(dporttcmflushw)
    ,.memextaddro(dportaxiaddrw)
    ,.memextdatawro(dportaxidatawrw)
    ,.memextrdo(dportaxirdw)
    ,.memextwro(dportaxiwrw)
    ,.memextcacheableo(dportaxicacheablew)
    ,.memextreqtago(dportaxireqtagw)
    ,.memextinvalidateo(dportaxiinvalidatew)
    ,.memextwritebacko(dportaxiwritebackw)
    ,.memextflusho(dportaxiflushw)
);


tcmmem
utcm
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.memirdi(ifetchrdw)
    ,.memiflushi(ifetchflushw)
    ,.memiinvalidatei(ifetchinvalidatew)
    ,.memipci(ifetchpcw)
    ,.memdaddri(dporttcmaddrw)
    ,.memddatawri(dporttcmdatawrw)
    ,.memdrdi(dporttcmrdw)
    ,.memdwri(dporttcmwrw)
    ,.memdcacheablei(dporttcmcacheablew)
    ,.memdreqtagi(dporttcmreqtagw)
    ,.memdinvalidatei(dporttcminvalidatew)
    ,.memdwritebacki(dporttcmwritebackw)
    ,.memdflushi(dporttcmflushw)
    ,.axiawvalidi(axitawvalidi)
    ,.axiawaddri(axitawaddri)
    ,.axiawidi(axitawidi)
    ,.axiawleni(axitawleni)
    ,.axiawbursti(axitawbursti)
    ,.axiwvalidi(axitwvalidi)
    ,.axiwdatai(axitwdatai)
    ,.axiwstrbi(axitwstrbi)
    ,.axiwlasti(axitwlasti)
    ,.axibreadyi(axitbreadyi)
    ,.axiarvalidi(axitarvalidi)
    ,.axiaraddri(axitaraddri)
    ,.axiaridi(axitaridi)
    ,.axiarleni(axitarleni)
    ,.axiarbursti(axitarbursti)
    ,.axirreadyi(axitrreadyi)

    
    ,.memiaccepto(ifetchacceptw)
    ,.memivalido(ifetchvalidw)
    ,.memierroro(ifetcherrorw)
    ,.memiinsto(ifetchinstw)
    ,.memddatardo(dporttcmdatardw)
    ,.memdaccepto(dporttcmacceptw)
    ,.memdacko(dporttcmackw)
    ,.memderroro(dporttcmerrorw)
    ,.memdresptago(dporttcmresptagw)
    ,.axiawreadyo(axitawreadyo)
    ,.axiwreadyo(axitwreadyo)
    ,.axibvalido(axitbvalido)
    ,.axibrespo(axitbrespo)
    ,.axibido(axitbido)
    ,.axiarreadyo(axitarreadyo)
    ,.axirvalido(axitrvalido)
    ,.axirdatao(axitrdatao)
    ,.axirrespo(axitrrespo)
    ,.axirido(axitrido)
    ,.axirlasto(axitrlasto)
);


dportaxi
uaxi
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.memaddri(dportaxiaddrw)
    ,.memdatawri(dportaxidatawrw)
    ,.memrdi(dportaxirdw)
    ,.memwri(dportaxiwrw)
    ,.memcacheablei(dportaxicacheablew)
    ,.memreqtagi(dportaxireqtagw)
    ,.meminvalidatei(dportaxiinvalidatew)
    ,.memwritebacki(dportaxiwritebackw)
    ,.memflushi(dportaxiflushw)
    ,.axiawreadyi(axiiawreadyi)
    ,.axiwreadyi(axiiwreadyi)
    ,.axibvalidi(axiibvalidi)
    ,.axibrespi(axiibrespi)
    ,.axibidi(axiibidi)
    ,.axiarreadyi(axiiarreadyi)
    ,.axirvalidi(axiirvalidi)
    ,.axirdatai(axiirdatai)
    ,.axirrespi(axiirrespi)
    ,.axiridi(axiiridi)
    ,.axirlasti(axiirlasti)

    
    ,.memdatardo(dportaxidatardw)
    ,.memaccepto(dportaxiacceptw)
    ,.memacko(dportaxiackw)
    ,.memerroro(dportaxierrorw)
    ,.memresptago(dportaxiresptagw)
    ,.axiawvalido(axiiawvalido)
    ,.axiawaddro(axiiawaddro)
    ,.axiawido(axiiawido)
    ,.axiawleno(axiiawleno)
    ,.axiawbursto(axiiawbursto)
    ,.axiwvalido(axiiwvalido)
    ,.axiwdatao(axiiwdatao)
    ,.axiwstrbo(axiiwstrbo)
    ,.axiwlasto(axiiwlasto)
    ,.axibreadyo(axiibreadyo)
    ,.axiarvalido(axiiarvalido)
    ,.axiaraddro(axiiaraddro)
    ,.axiarido(axiiarido)
    ,.axiarleno(axiiarleno)
    ,.axiarbursto(axiiarbursto)
    ,.axirreadyo(axiirreadyo)
);



endmodule

module riscvtop
#(
     parameter COREID          = 0
    ,parameter MEMCACHEADDRMIN = 0
    ,parameter MEMCACHEADDRMAX = 32'hffffffff
)
(
    
     input           clki
    ,input           rsti
    ,input           axiiawreadyi
    ,input           axiiwreadyi
    ,input           axiibvalidi
    ,input  [  1:0]  axiibrespi
    ,input  [  3:0]  axiibidi
    ,input           axiiarreadyi
    ,input           axiirvalidi
    ,input  [ 31:0]  axiirdatai
    ,input  [  1:0]  axiirrespi
    ,input  [  3:0]  axiiridi
    ,input           axiirlasti
    ,input           axidawreadyi
    ,input           axidwreadyi
    ,input           axidbvalidi
    ,input  [  1:0]  axidbrespi
    ,input  [  3:0]  axidbidi
    ,input           axidarreadyi
    ,input           axidrvalidi
    ,input  [ 31:0]  axidrdatai
    ,input  [  1:0]  axidrrespi
    ,input  [  3:0]  axidridi
    ,input           axidrlasti
    ,input           intri
    ,input  [ 31:0]  resetvectori

    
    ,output          axiiawvalido
    ,output [ 31:0]  axiiawaddro
    ,output [  3:0]  axiiawido
    ,output [  7:0]  axiiawleno
    ,output [  1:0]  axiiawbursto
    ,output          axiiwvalido
    ,output [ 31:0]  axiiwdatao
    ,output [  3:0]  axiiwstrbo
    ,output          axiiwlasto
    ,output          axiibreadyo
    ,output          axiiarvalido
    ,output [ 31:0]  axiiaraddro
    ,output [  3:0]  axiiarido
    ,output [  7:0]  axiiarleno
    ,output [  1:0]  axiiarbursto
    ,output          axiirreadyo
    ,output          axidawvalido
    ,output [ 31:0]  axidawaddro
    ,output [  3:0]  axidawido
    ,output [  7:0]  axidawleno
    ,output [  1:0]  axidawbursto
    ,output          axidwvalido
    ,output [ 31:0]  axidwdatao
    ,output [  3:0]  axidwstrbo
    ,output          axidwlasto
    ,output          axidbreadyo
    ,output          axidarvalido
    ,output [ 31:0]  axidaraddro
    ,output [  3:0]  axidarido
    ,output [  7:0]  axidarleno
    ,output [  1:0]  axidarbursto
    ,output          axidrreadyo
);

wire           icachevalidw;
wire           icacheflushw;
wire           dcacheflushw;
wire           dcacheinvalidatew;
wire           dcacheackw;
wire  [ 10:0]  dcacheresptagw;
wire  [ 31:0]  icacheinstw;
wire  [ 31:0]  cpuidw = COREID;
wire           dcacherdw;
wire  [ 31:0]  dcacheaddrw;
wire           dcacheacceptw;
wire           icacheinvalidatew;
wire           dcachewritebackw;
wire  [ 10:0]  dcachereqtagw;
wire           dcachecacheablew;
wire           icacheerrorw;
wire  [ 31:0]  dcachedatardw;
wire           icacheacceptw;
wire  [  3:0]  dcachewrw;
wire  [ 31:0]  icachepcw;
wire           icacherdw;
wire           dcacheerrorw;
wire  [ 31:0]  dcachedatawrw;


dcache
udcache
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.memaddri(dcacheaddrw)
    ,.memdatawri(dcachedatawrw)
    ,.memrdi(dcacherdw)
    ,.memwri(dcachewrw)
    ,.memcacheablei(dcachecacheablew)
    ,.memreqtagi(dcachereqtagw)
    ,.meminvalidatei(dcacheinvalidatew)
    ,.memwritebacki(dcachewritebackw)
    ,.memflushi(dcacheflushw)
    ,.axiawreadyi(axidawreadyi)
    ,.axiwreadyi(axidwreadyi)
    ,.axibvalidi(axidbvalidi)
    ,.axibrespi(axidbrespi)
    ,.axibidi(axidbidi)
    ,.axiarreadyi(axidarreadyi)
    ,.axirvalidi(axidrvalidi)
    ,.axirdatai(axidrdatai)
    ,.axirrespi(axidrrespi)
    ,.axiridi(axidridi)
    ,.axirlasti(axidrlasti)

    
    ,.memdatardo(dcachedatardw)
    ,.memaccepto(dcacheacceptw)
    ,.memacko(dcacheackw)
    ,.memerroro(dcacheerrorw)
    ,.memresptago(dcacheresptagw)
    ,.axiawvalido(axidawvalido)
    ,.axiawaddro(axidawaddro)
    ,.axiawido(axidawido)
    ,.axiawleno(axidawleno)
    ,.axiawbursto(axidawbursto)
    ,.axiwvalido(axidwvalido)
    ,.axiwdatao(axidwdatao)
    ,.axiwstrbo(axidwstrbo)
    ,.axiwlasto(axidwlasto)
    ,.axibreadyo(axidbreadyo)
    ,.axiarvalido(axidarvalido)
    ,.axiaraddro(axidaraddro)
    ,.axiarido(axidarido)
    ,.axiarleno(axidarleno)
    ,.axiarbursto(axidarbursto)
    ,.axirreadyo(axidrreadyo)
);


riscvcore
#(
     .MEMCACHEADDRMIN(MEMCACHEADDRMIN)
    ,.MEMCACHEADDRMAX(MEMCACHEADDRMAX)
)
ucore
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.memddatardi(dcachedatardw)
    ,.memdaccepti(dcacheacceptw)
    ,.memdacki(dcacheackw)
    ,.memderrori(dcacheerrorw)
    ,.memdresptagi(dcacheresptagw)
    ,.memiaccepti(icacheacceptw)
    ,.memivalidi(icachevalidw)
    ,.memierrori(icacheerrorw)
    ,.memiinsti(icacheinstw)
    ,.intri(intri)
    ,.resetvectori(resetvectori)
    ,.cpuidi(cpuidw)

    
    ,.memdaddro(dcacheaddrw)
    ,.memddatawro(dcachedatawrw)
    ,.memdrdo(dcacherdw)
    ,.memdwro(dcachewrw)
    ,.memdcacheableo(dcachecacheablew)
    ,.memdreqtago(dcachereqtagw)
    ,.memdinvalidateo(dcacheinvalidatew)
    ,.memdwritebacko(dcachewritebackw)
    ,.memdflusho(dcacheflushw)
    ,.memirdo(icacherdw)
    ,.memiflusho(icacheflushw)
    ,.memiinvalidateo(icacheinvalidatew)
    ,.memipco(icachepcw)
);


icache
uicache
(
    
     .clki(clki)
    ,.rsti(rsti)
    ,.reqrdi(icacherdw)
    ,.reqflushi(icacheflushw)
    ,.reqinvalidatei(icacheinvalidatew)
    ,.reqpci(icachepcw)
    ,.axiawreadyi(axiiawreadyi)
    ,.axiwreadyi(axiiwreadyi)
    ,.axibvalidi(axiibvalidi)
    ,.axibrespi(axiibrespi)
    ,.axibidi(axiibidi)
    ,.axiarreadyi(axiiarreadyi)
    ,.axirvalidi(axiirvalidi)
    ,.axirdatai(axiirdatai)
    ,.axirrespi(axiirrespi)
    ,.axiridi(axiiridi)
    ,.axirlasti(axiirlasti)

    
    ,.reqaccepto(icacheacceptw)
    ,.reqvalido(icachevalidw)
    ,.reqerroro(icacheerrorw)
    ,.reqinsto(icacheinstw)
    ,.axiawvalido(axiiawvalido)
    ,.axiawaddro(axiiawaddro)
    ,.axiawido(axiiawido)
    ,.axiawleno(axiiawleno)
    ,.axiawbursto(axiiawbursto)
    ,.axiwvalido(axiiwvalido)
    ,.axiwdatao(axiiwdatao)
    ,.axiwstrbo(axiiwstrbo)
    ,.axiwlasto(axiiwlasto)
    ,.axibreadyo(axiibreadyo)
    ,.axiarvalido(axiiarvalido)
    ,.axiaraddro(axiiaraddro)
    ,.axiarido(axiiarido)
    ,.axiarleno(axiiarleno)
    ,.axiarbursto(axiiarbursto)
    ,.axirreadyo(axiirreadyo)
);



endmodule
`include "riscvdefs.v"

module riscvtracesim
(
     input                        validi
    ,input  [31:0]                pci
    ,input  [31:0]                opcodei
);

`ifdef verilator
function [79:0] getregnamestr;
    input  [4:0] regnum;
begin
    case (regnum)
        5'd0:  getregnamestr = "zero";
        5'd1:  getregnamestr = "ra";
        5'd2:  getregnamestr = "sp";
        5'd3:  getregnamestr = "gp";
        5'd4:  getregnamestr = "tp";
        5'd5:  getregnamestr = "t0";
        5'd6:  getregnamestr = "t1";
        5'd7:  getregnamestr = "t2";
        5'd8:  getregnamestr = "s0";
        5'd9:  getregnamestr = "s1";
        5'd10: getregnamestr = "a0";
        5'd11: getregnamestr = "a1";
        5'd12: getregnamestr = "a2";
        5'd13: getregnamestr = "a3";
        5'd14: getregnamestr = "a4";
        5'd15: getregnamestr = "a5";
        5'd16: getregnamestr = "a6";
        5'd17: getregnamestr = "a7";
        5'd18: getregnamestr = "s2";
        5'd19: getregnamestr = "s3";
        5'd20: getregnamestr = "s4";
        5'd21: getregnamestr = "s5";
        5'd22: getregnamestr = "s6";
        5'd23: getregnamestr = "s7";
        5'd24: getregnamestr = "s8";
        5'd25: getregnamestr = "s9";
        5'd26: getregnamestr = "s10";
        5'd27: getregnamestr = "s11";
        5'd28: getregnamestr = "t3";
        5'd29: getregnamestr = "t4";
        5'd30: getregnamestr = "t5";
        5'd31: getregnamestr = "t6";
    endcase
end
endfunction

reg [79:0] dbginststr;
reg [79:0] dbginstra;
reg [79:0] dbginstrb;
reg [79:0] dbginstrd;
reg [31:0] dbginstimm;
reg [31:0] dbginstpc;

wire [4:0] raidxw = opcodei[19:15];
wire [4:0] rbidxw = opcodei[24:20];
wire [4:0] rdidxw = opcodei[11:7];

`define DBGIMMIMM20     {opcodei[31:12], 12'b0}
`define DBGIMMIMM12     {{20{opcodei[31]}}, opcodei[31:20]}
`define DBGIMMBIMM      {{19{opcodei[31]}}, opcodei[31], opcodei[7], opcodei[30:25], opcodei[11:8], 1'b0}
`define DBGIMMJIMM20    {{12{opcodei[31]}}, opcodei[19:12], opcodei[20], opcodei[30:25], opcodei[24:21], 1'b0}
`define DBGIMMSTOREIMM  {{20{opcodei[31]}}, opcodei[31:25], opcodei[11:7]}
`define DBGIMMSHAMT     opcodei[24:20]

always @ *
begin
    dbginststr = "-";
    dbginstra  = "-";
    dbginstrb  = "-";
    dbginstrd  = "-";
    dbginstpc  = 32'bx;

    if (validi)
    begin
        dbginstpc  = pci;
        dbginstra  = getregnamestr(raidxw);
        dbginstrb  = getregnamestr(rbidxw);
        dbginstrd  = getregnamestr(rdidxw);

        case (1'b1)
            ((opcodei & `INSTANDIMASK) == `INSTANDI)   : dbginststr = "andi";
            ((opcodei & `INSTADDIMASK) == `INSTADDI)   : dbginststr = "addi";
            ((opcodei & `INSTSLTIMASK) == `INSTSLTI)   : dbginststr = "slti";
            ((opcodei & `INSTSLTIUMASK) == `INSTSLTIU)  : dbginststr = "sltiu";
            ((opcodei & `INSTORIMASK) == `INSTORI)    : dbginststr = "ori";
            ((opcodei & `INSTXORIMASK) == `INSTXORI)   : dbginststr = "xori";
            ((opcodei & `INSTSLLIMASK) == `INSTSLLI)   : dbginststr = "slli";
            ((opcodei & `INSTSRLIMASK) == `INSTSRLI)   : dbginststr = "srli";
            ((opcodei & `INSTSRAIMASK) == `INSTSRAI)   : dbginststr = "srai";
            ((opcodei & `INSTLUIMASK) == `INSTLUI)    : dbginststr = "lui";
            ((opcodei & `INSTAUIPCMASK) == `INSTAUIPC)  : dbginststr = "auipc";
            ((opcodei & `INSTADDMASK) == `INSTADD)    : dbginststr = "add";
            ((opcodei & `INSTSUBMASK) == `INSTSUB)    : dbginststr = "sub";
            ((opcodei & `INSTSLTMASK) == `INSTSLT)    : dbginststr = "slt";
            ((opcodei & `INSTSLTUMASK) == `INSTSLTU)   : dbginststr = "sltu";
            ((opcodei & `INSTXORMASK) == `INSTXOR)    : dbginststr = "xor";
            ((opcodei & `INSTORMASK) == `INSTOR)     : dbginststr = "or";
            ((opcodei & `INSTANDMASK) == `INSTAND)    : dbginststr = "and";
            ((opcodei & `INSTSLLMASK) == `INSTSLL)    : dbginststr = "sll";
            ((opcodei & `INSTSRLMASK) == `INSTSRL)    : dbginststr = "srl";
            ((opcodei & `INSTSRAMASK) == `INSTSRA)    : dbginststr = "sra";
            ((opcodei & `INSTJALMASK) == `INSTJAL)    : dbginststr = "jal";
            ((opcodei & `INSTJALRMASK) == `INSTJALR)   : dbginststr = "jalr";
            ((opcodei & `INSTBEQMASK) == `INSTBEQ)    : dbginststr = "beq";
            ((opcodei & `INSTBNEMASK) == `INSTBNE)    : dbginststr = "bne";
            ((opcodei & `INSTBLTMASK) == `INSTBLT)    : dbginststr = "blt";
            ((opcodei & `INSTBGEMASK) == `INSTBGE)    : dbginststr = "bge";
            ((opcodei & `INSTBLTUMASK) == `INSTBLTU)   : dbginststr = "bltu";
            ((opcodei & `INSTBGEUMASK) == `INSTBGEU)   : dbginststr = "bgeu";
            ((opcodei & `INSTLBMASK) == `INSTLB)     : dbginststr = "lb";
            ((opcodei & `INSTLHMASK) == `INSTLH)     : dbginststr = "lh";
            ((opcodei & `INSTLWMASK) == `INSTLW)     : dbginststr = "lw";
            ((opcodei & `INSTLBUMASK) == `INSTLBU)    : dbginststr = "lbu";
            ((opcodei & `INSTLHUMASK) == `INSTLHU)    : dbginststr = "lhu";
            ((opcodei & `INSTLWUMASK) == `INSTLWU)    : dbginststr = "lwu";
            ((opcodei & `INSTSBMASK) == `INSTSB)     : dbginststr = "sb";
            ((opcodei & `INSTSHMASK) == `INSTSH)     : dbginststr = "sh";
            ((opcodei & `INSTSWMASK) == `INSTSW)     : dbginststr = "sw";
            ((opcodei & `INSTECALLMASK) == `INSTECALL)  : dbginststr = "ecall";
            ((opcodei & `INSTEBREAKMASK) == `INSTEBREAK) : dbginststr = "ebreak";
            ((opcodei & `INSTERETMASK) == `INSTERET)   : dbginststr = "eret";
            ((opcodei & `INSTCSRRWMASK) == `INSTCSRRW)  : dbginststr = "csrrw";
            ((opcodei & `INSTCSRRSMASK) == `INSTCSRRS)  : dbginststr = "csrrs";
            ((opcodei & `INSTCSRRCMASK) == `INSTCSRRC)  : dbginststr = "csrrc";
            ((opcodei & `INSTCSRRWIMASK) == `INSTCSRRWI) : dbginststr = "csrrwi";
            ((opcodei & `INSTCSRRSIMASK) == `INSTCSRRSI) : dbginststr = "csrrsi";
            ((opcodei & `INSTCSRRCIMASK) == `INSTCSRRCI) : dbginststr = "csrrci";
            ((opcodei & `INSTMULMASK) == `INSTMUL)    : dbginststr = "mul";
            ((opcodei & `INSTMULHMASK) == `INSTMULH)   : dbginststr = "mulh";
            ((opcodei & `INSTMULHSUMASK) == `INSTMULHSU) : dbginststr = "mulhsu";
            ((opcodei & `INSTMULHUMASK) == `INSTMULHU)  : dbginststr = "mulhu";
            ((opcodei & `INSTDIVMASK) == `INSTDIV)    : dbginststr = "div";
            ((opcodei & `INSTDIVUMASK) == `INSTDIVU)   : dbginststr = "divu";
            ((opcodei & `INSTREMMASK) == `INSTREM)    : dbginststr = "rem";
            ((opcodei & `INSTREMUMASK) == `INSTREMU)   : dbginststr = "remu";
            ((opcodei & `INSTIFENCEMASK) == `INSTIFENCE)  : dbginststr = "fence.i";
        endcase

        case (1'b1)

            ((opcodei & `INSTADDIMASK) == `INSTADDI) ,  
            ((opcodei & `INSTANDIMASK) == `INSTANDI) ,  
            ((opcodei & `INSTSLTIMASK) == `INSTSLTI) ,  
            ((opcodei & `INSTSLTIUMASK) == `INSTSLTIU) , 
            ((opcodei & `INSTORIMASK) == `INSTORI) ,   
            ((opcodei & `INSTXORIMASK) == `INSTXORI) ,  
            ((opcodei & `INSTCSRRWMASK) == `INSTCSRRW) , 
            ((opcodei & `INSTCSRRSMASK) == `INSTCSRRS) , 
            ((opcodei & `INSTCSRRCMASK) == `INSTCSRRC) , 
            ((opcodei & `INSTCSRRWIMASK) == `INSTCSRRWI) ,
            ((opcodei & `INSTCSRRSIMASK) == `INSTCSRRSI) ,
            ((opcodei & `INSTCSRRCIMASK) == `INSTCSRRCI) :
            begin
                dbginstrb  = "-";
                dbginstimm = `DBGIMMIMM12;
            end

            ((opcodei & `INSTSLLIMASK) == `INSTSLLI) , 
            ((opcodei & `INSTSRLIMASK) == `INSTSRLI) , 
            ((opcodei & `INSTSRAIMASK) == `INSTSRAI) : 
            begin
                dbginstrb  = "-";
                dbginstimm = {27'b0, `DBGIMMSHAMT};
            end

            ((opcodei & `INSTLUIMASK) == `INSTLUI) : 
            begin
                dbginstra  = "-";
                dbginstrb  = "-";
                dbginstimm = `DBGIMMIMM20;
            end

            ((opcodei & `INSTAUIPCMASK) == `INSTAUIPC) : 
            begin
                dbginstra  = "pc";
                dbginstrb  = "-";
                dbginstimm = `DBGIMMIMM20;
            end   

            ((opcodei & `INSTJALMASK) == `INSTJAL) :  
            begin
                dbginstra  = "-";
                dbginstrb  = "-";
                dbginstimm = pci + `DBGIMMJIMM20;

                if (rdidxw == 5'd1)
                    dbginststr = "call";
            end

            ((opcodei & `INSTJALRMASK) == `INSTJALR) : 
            begin
                dbginstrb  = "-";
                dbginstimm = `DBGIMMIMM12;

               if (raidxw == 5'd1 && `DBGIMMIMM12 == 32'b0)
                    dbginststr = "ret";
               else if (rdidxw == 5'd1)
                    dbginststr = "call (R)";
            end

            
            ((opcodei & `INSTLBMASK) == `INSTLB) ,
            ((opcodei & `INSTLHMASK) == `INSTLH) ,
            ((opcodei & `INSTLWMASK) == `INSTLW) ,
            ((opcodei & `INSTLBUMASK) == `INSTLBU) ,
            ((opcodei & `INSTLHUMASK) == `INSTLHU) ,
            ((opcodei & `INSTLWUMASK) == `INSTLWU) :
            begin
                dbginstrb  = "-";
                dbginstimm = `DBGIMMIMM12;
            end 

            
            ((opcodei & `INSTSBMASK) == `INSTSB) ,
            ((opcodei & `INSTSHMASK) == `INSTSH) ,
            ((opcodei & `INSTSWMASK) == `INSTSW) :
            begin
                dbginstrd  = "-";
                dbginstimm = `DBGIMMSTOREIMM;
            end
        endcase        
    end
end
`endif

endmodule
module riscvxilinx2r1w
(
    
     input           clki
    ,input           rsti
    ,input  [  4:0]  rd0i
    ,input  [ 31:0]  rd0valuei
    ,input  [  4:0]  rai
    ,input  [  4:0]  rbi

    
    ,output [ 31:0]  ravalueo
    ,output [ 31:0]  rbvalueo
);


wire [31:0]     regrs1w;
wire [31:0]     regrs2w;
wire [31:0]     rs1015w;
wire [31:0]     rs11631w;
wire [31:0]     rs2015w;
wire [31:0]     rs21631w;
wire            writeenablew;
wire            writebankaw;
wire            writebankbw;

genvar i;

generate
for (i=0;i<32;i=i+1)
begin : regloop1
    RAM16X1D regbit1a(.WCLK(clki), .WE(writebankaw), .A0(rd0i[0]), .A1(rd0i[1]), .A2(rd0i[2]), .A3(rd0i[3]), .D(rd0valuei[i]), .DPRA0(rai[0]), .DPRA1(rai[1]), .DPRA2(rai[2]), .DPRA3(rai[3]), .DPO(rs1015w[i]), .SPO(/* open */));
    RAM16X1D regbit2a(.WCLK(clki), .WE(writebankaw), .A0(rd0i[0]), .A1(rd0i[1]), .A2(rd0i[2]), .A3(rd0i[3]), .D(rd0valuei[i]), .DPRA0(rbi[0]), .DPRA1(rbi[1]), .DPRA2(rbi[2]), .DPRA3(rbi[3]), .DPO(rs2015w[i]), .SPO(/* open */));
end
endgenerate

generate
for (i=0;i<32;i=i+1)
begin : regloop2
    RAM16X1D regbit1b(.WCLK(clki), .WE(writebankbw), .A0(rd0i[0]), .A1(rd0i[1]), .A2(rd0i[2]), .A3(rd0i[3]), .D(rd0valuei[i]), .DPRA0(rai[0]), .DPRA1(rai[1]), .DPRA2(rai[2]), .DPRA3(rai[3]), .DPO(rs11631w[i]), .SPO(/* open */));
    RAM16X1D regbit2b(.WCLK(clki), .WE(writebankbw), .A0(rd0i[0]), .A1(rd0i[1]), .A2(rd0i[2]), .A3(rd0i[3]), .D(rd0valuei[i]), .DPRA0(rbi[0]), .DPRA1(rbi[1]), .DPRA2(rbi[2]), .DPRA3(rbi[3]), .DPO(rs21631w[i]), .SPO(/* open */));
end
endgenerate

assign regrs1w       = (rai[4] == 1'b0) ? rs1015w : rs11631w;
assign regrs2w       = (rbi[4] == 1'b0) ? rs2015w : rs21631w;

assign writeenablew = (rd0i != 5'b00000);

assign writebankaw  = (writeenablew & (~rd0i[4]));
assign writebankbw  = (writeenablew & rd0i[4]);

reg [31:0] ravaluer;
reg [31:0] rbvaluer;

always @ *
begin
    if (rai == 5'b00000)
        ravaluer = 32'h00000000;
    else
        ravaluer = regrs1w;

    if (rbi == 5'b00000)
        rbvaluer = 32'h00000000;
    else
        rbvaluer = regrs2w;
end

assign ravalueo = ravaluer;
assign rbvalueo = rbvaluer;

endmodule

`ifdef verilator
module RAM16X1D (DPO, SPO, A0, A1, A2, A3, D, DPRA0, DPRA1, DPRA2, DPRA3, WCLK, WE);

    parameter INIT = 16'h0000;

    output DPO, SPO;

    input  A0, A1, A2, A3, D, DPRA0, DPRA1, DPRA2, DPRA3, WCLK, WE;

    reg  [15:0] mem;
    wire [3:0] adr;

    assign adr = {A3, A2, A1, A0};
    assign SPO = mem[adr];
    assign DPO = mem[{DPRA3, DPRA2, DPRA1, DPRA0}];

    initial 
        mem = INIT;

    always @(posedge WCLK) 
        if (WE == 1'b1)
            mem[adr] <= D;

endmodule
`endif

module tcmmem
(
    
     input           clki
    ,input           rsti
    ,input           memirdi
    ,input           memiflushi
    ,input           memiinvalidatei
    ,input  [ 31:0]  memipci
    ,input  [ 31:0]  memdaddri
    ,input  [ 31:0]  memddatawri
    ,input           memdrdi
    ,input  [  3:0]  memdwri
    ,input           memdcacheablei
    ,input  [ 10:0]  memdreqtagi
    ,input           memdinvalidatei
    ,input           memdwritebacki
    ,input           memdflushi
    ,input           axiawvalidi
    ,input  [ 31:0]  axiawaddri
    ,input  [  3:0]  axiawidi
    ,input  [  7:0]  axiawleni
    ,input  [  1:0]  axiawbursti
    ,input           axiwvalidi
    ,input  [ 31:0]  axiwdatai
    ,input  [  3:0]  axiwstrbi
    ,input           axiwlasti
    ,input           axibreadyi
    ,input           axiarvalidi
    ,input  [ 31:0]  axiaraddri
    ,input  [  3:0]  axiaridi
    ,input  [  7:0]  axiarleni
    ,input  [  1:0]  axiarbursti
    ,input           axirreadyi

    
    ,output          memiaccepto
    ,output          memivalido
    ,output          memierroro
    ,output [ 31:0]  memiinsto
    ,output [ 31:0]  memddatardo
    ,output          memdaccepto
    ,output          memdacko
    ,output          memderroro
    ,output [ 10:0]  memdresptago
    ,output          axiawreadyo
    ,output          axiwreadyo
    ,output          axibvalido
    ,output [  1:0]  axibrespo
    ,output [  3:0]  axibido
    ,output          axiarreadyo
    ,output          axirvalido
    ,output [ 31:0]  axirdatao
    ,output [  1:0]  axirrespo
    ,output [  3:0]  axirido
    ,output          axirlasto
);



wire          extacceptw;
wire          extackw;
wire [ 31:0]  extreaddataw;
wire [  3:0]  extwrw;
wire          extrdw;
wire [  7:0]  extlenw;
wire [ 31:0]  extaddrw;
wire [ 31:0]  extwritedataw;

tcmmempmem
uconv
(
    
    .clki(clki),
    .rsti(rsti),
    .axiawvalidi(axiawvalidi),
    .axiawaddri(axiawaddri),
    .axiawidi(axiawidi),
    .axiawleni(axiawleni),
    .axiawbursti(axiawbursti),
    .axiwvalidi(axiwvalidi),
    .axiwdatai(axiwdatai),
    .axiwstrbi(axiwstrbi),
    .axiwlasti(axiwlasti),
    .axibreadyi(axibreadyi),
    .axiarvalidi(axiarvalidi),
    .axiaraddri(axiaraddri),
    .axiaridi(axiaridi),
    .axiarleni(axiarleni),
    .axiarbursti(axiarbursti),
    .axirreadyi(axirreadyi),
    .ramaccepti(extacceptw),
    .ramacki(extackw),
    .ramerrori(1'b0),
    .ramreaddatai(extreaddataw),

    
    .axiawreadyo(axiawreadyo),
    .axiwreadyo(axiwreadyo),
    .axibvalido(axibvalido),
    .axibrespo(axibrespo),
    .axibido(axibido),
    .axiarreadyo(axiarreadyo),
    .axirvalido(axirvalido),
    .axirdatao(axirdatao),
    .axirrespo(axirrespo),
    .axirido(axirido),
    .axirlasto(axirlasto),
    .ramwro(extwrw),
    .ramrdo(extrdw),
    .ramleno(extlenw),
    .ramaddro(extaddrw),
    .ramwritedatao(extwritedataw)
);


wire [13:0] muxedaddrw = extacceptw ? extaddrw[15:2] : memdaddri[15:2];
wire [31:0] muxeddataw = extacceptw ? extwritedataw : memddatawri;
wire [3:0]  muxedwrw   = extacceptw ? extwrw         : memdwri;
wire [31:0] datarw;

tcmmemram
uram
(
    
     .clk0i(clki)
    ,.rst0i(rsti)
    ,.addr0i(memipci[15:2])
    ,.data0i(32'b0)
    ,.wr0i(4'b0)

    
    ,.clk1i(clki)
    ,.rst1i(rsti)
    ,.addr1i(muxedaddrw)
    ,.data1i(muxeddataw)
    ,.wr1i(muxedwrw)

    
    ,.data0o(memiinsto)
    ,.data1o(datarw)
);

assign extreaddataw = datarw;

reg        memivalidq;

always @ (posedge clki or posedge rsti)
if (rsti)
    memivalidq <= 1'b0;
else
    memivalidq <= memirdi;

assign memiaccepto  = 1'b1;
assign memivalido   = memivalidq;
assign memierroro   = 1'b0;

reg        memdacceptq;
reg [10:0] memdtagq;
reg        memdackq;
reg        extackq;

always @ (posedge clki or posedge rsti)
if (rsti)
    memdacceptq <= 1'b1;
else if (extrdw || extwrw != 4'b0)
    memdacceptq <= 1'b0;
else
    memdacceptq <= 1'b1;

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    memdackq    <= 1'b0;
    memdtagq    <= 11'b0;
end
else if ((memdrdi || memdwri != 4'b0 || memdflushi || memdinvalidatei || memdwritebacki) && memdaccepto)
begin
    memdackq    <= 1'b1;
    memdtagq    <= memdreqtagi;
end
else
    memdackq    <= 1'b0;

always @ (posedge clki or posedge rsti)
if (rsti)
    extackq <= 1'b0;
else if ((extrdw || extwrw != 4'b0) && extacceptw)
    extackq <= 1'b1;
else
    extackq <= 1'b0;

assign memdacko          = memdackq;
assign memdresptago     = memdtagq;
assign memddatardo      = datarw;
assign memderroro        = 1'b0;

assign memdaccepto       = memdacceptq;
assign extacceptw         = !memdacceptq;
assign extackw            = extackq;

`ifdef verilator
function write; /*verilator public*/
    input [31:0] addr;
    input [7:0]  data;
begin
    case (addr[1:0])
    2'd0: uram.ram[addr/4][7:0]   = data;
    2'd1: uram.ram[addr/4][15:8]  = data;
    2'd2: uram.ram[addr/4][23:16] = data;
    2'd3: uram.ram[addr/4][31:24] = data;
    endcase
end
endfunction
function [7:0] read; /*verilator public*/
    input [31:0] addr;
begin
    case (addr[1:0])
    2'd0: read = uram.ram[addr/4][7:0];
    2'd1: read = uram.ram[addr/4][15:8];
    2'd2: read = uram.ram[addr/4][23:16];
    2'd3: read = uram.ram[addr/4][31:24];
    endcase
end
endfunction
`endif



endmodule

module tcmmempmem
(
    
     input           clki
    ,input           rsti
    ,input           axiawvalidi
    ,input  [ 31:0]  axiawaddri
    ,input  [  3:0]  axiawidi
    ,input  [  7:0]  axiawleni
    ,input  [  1:0]  axiawbursti
    ,input           axiwvalidi
    ,input  [ 31:0]  axiwdatai
    ,input  [  3:0]  axiwstrbi
    ,input           axiwlasti
    ,input           axibreadyi
    ,input           axiarvalidi
    ,input  [ 31:0]  axiaraddri
    ,input  [  3:0]  axiaridi
    ,input  [  7:0]  axiarleni
    ,input  [  1:0]  axiarbursti
    ,input           axirreadyi
    ,input           ramaccepti
    ,input           ramacki
    ,input           ramerrori
    ,input  [ 31:0]  ramreaddatai

    
    ,output          axiawreadyo
    ,output          axiwreadyo
    ,output          axibvalido
    ,output [  1:0]  axibrespo
    ,output [  3:0]  axibido
    ,output          axiarreadyo
    ,output          axirvalido
    ,output [ 31:0]  axirdatao
    ,output [  1:0]  axirrespo
    ,output [  3:0]  axirido
    ,output          axirlasto
    ,output [  3:0]  ramwro
    ,output          ramrdo
    ,output [  7:0]  ramleno
    ,output [ 31:0]  ramaddro
    ,output [ 31:0]  ramwritedatao
);



function [31:0] calculateaddrnext;
    input [31:0] addr;
    input [1:0]  axtype;
    input [7:0]  axlen;

    reg [31:0]   mask;
begin
    mask = 0;

    case (axtype)
`ifdef SUPPORTFIXEDBURST
    2'd0: 
    begin
        calculateaddrnext = addr;
    end
`endif
`ifdef SUPPORTWRAPBURST
    2'd2: 
    begin
        case (axlen)
        8'd0:      mask = 32'h03;
        8'd1:      mask = 32'h07;
        8'd3:      mask = 32'h0F;
        8'd7:      mask = 32'h1F;
        8'd15:     mask = 32'h3F;
        default:   mask = 32'h3F;
        endcase

        calculateaddrnext = (addr & ~mask) | ((addr + 4) & mask);
    end
`endif
    default: 
        calculateaddrnext = addr + 4;
    endcase
end
endfunction

reg [7:0]   reqlenq;
reg [31:0]  reqaddrq;
reg         reqrdq;
reg         reqwrq;
reg [3:0]   reqidq;
reg [1:0]   reqaxburstq;
reg [7:0]   reqaxlenq;
reg         reqprioq;
reg         reqholdrdq;
reg         reqholdwrq;

wire        reqfifoacceptw;

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    reqlenq     <= 8'b0;
    reqaddrq    <= 32'b0;
    reqwrq      <= 1'b0;
    reqrdq      <= 1'b0;
    reqidq      <= 4'b0;
    reqaxburstq <= 2'b0;
    reqaxlenq   <= 8'b0;
    reqprioq    <= 1'b0;
end
else
begin
    
    if ((ramwro != 4'b0 || ramrdo) && ramaccepti)
    begin
        if (reqlenq == 8'd0)
        begin
            reqrdq   <= 1'b0;
            reqwrq   <= 1'b0;
        end
        else
        begin
            reqaddrq <= calculateaddrnext(reqaddrq, reqaxburstq, reqaxlenq);
            reqlenq  <= reqlenq - 8'd1;
        end
    end

    
    if (axiawvalidi && axiawreadyo)
    begin
        
        if (axiwvalidi && axiwreadyo)
        begin
            reqwrq      <= !axiwlasti;
            reqlenq     <= axiawleni - 8'd1;
            reqidq      <= axiawidi;
            reqaxburstq <= axiawbursti;
            reqaxlenq   <= axiawleni;
            reqaddrq    <= calculateaddrnext(axiawaddri, axiawbursti, axiawleni);
        end
        
        else
        begin
            reqwrq      <= 1'b1;
            reqlenq     <= axiawleni;
            reqidq      <= axiawidi;
            reqaxburstq <= axiawbursti;
            reqaxlenq   <= axiawleni;
            reqaddrq    <= axiawaddri;
        end
        reqprioq    <= !reqprioq;
    end
    
    else if (axiarvalidi && axiarreadyo)
    begin
        reqrdq      <= (axiarleni != 0);
        reqlenq     <= axiarleni - 8'd1;
        reqaddrq    <= calculateaddrnext(axiaraddri, axiarbursti, axiarleni);
        reqidq      <= axiaridi;
        reqaxburstq <= axiarbursti;
        reqaxlenq   <= axiarleni;
        reqprioq    <= !reqprioq;
    end
end

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    reqholdrdq   <= 1'b0;
    reqholdwrq   <= 1'b0;
end
else
begin
    if (ramrdo && !ramaccepti)
        reqholdrdq   <= 1'b1;
    else if (ramaccepti)
        reqholdrdq   <= 1'b0;

    if ((|ramwro) && !ramaccepti)
        reqholdwrq   <= 1'b1;
    else if (ramaccepti)
        reqholdwrq   <= 1'b0;
end

wire       reqpushw = (ramrdo || (ramwro != 4'b0)) && ramaccepti;
reg [5:0]  reqinr;

wire       reqoutvalidw;
wire [5:0] reqoutw;
wire       respacceptw;


always @ *
begin
    reqinr = 6'b0;

    
    if (axiarvalidi && axiarreadyo)
        reqinr = {1'b1, (axiarleni == 8'd0), axiaridi};
    
    else if (axiawvalidi && axiawreadyo)
        reqinr = {1'b0, (axiawleni == 8'd0), axiawidi};
    
    else
        reqinr = {ramrdo, (reqlenq == 8'd0), reqidq};
end

tcmmempmemfifo2
#( .WIDTH(1 + 1 + 4) )
urequests
(
    .clki(clki),
    .rsti(rsti),

    
    .dataini(reqinr),
    .pushi(reqpushw),
    .accepto(reqfifoacceptw),

    
    .popi(respacceptw),
    .dataouto(reqoutw),
    .valido(reqoutvalidw)
);

wire respiswritew = reqoutvalidw ? ~reqoutw[5] : 1'b0;
wire respisreadw  = reqoutvalidw ? reqoutw[5]  : 1'b0;
wire respislastw  = reqoutw[4];
wire [3:0] respidw = reqoutw[3:0];

wire respvalidw;

tcmmempmemfifo2
#( .WIDTH(32) )
uresponse
(
    .clki(clki),
    .rsti(rsti),

    
    .dataini(ramreaddatai),
    .pushi(ramacki),
    .accepto(),

    
    .popi(respacceptw),
    .dataouto(axirdatao),
    .valido(respvalidw)
);


wire writepriow   = ((reqprioq  & !reqholdrdq) | reqholdwrq);
wire readpriow    = ((!reqprioq & !reqholdwrq) | reqholdrdq);

wire writeactivew  = (axiawvalidi || reqwrq) && !reqrdq && reqfifoacceptw && (writepriow || reqwrq || !axiarvalidi);
wire readactivew   = (axiarvalidi || reqrdq) && !reqwrq && reqfifoacceptw && (readpriow || reqrdq || !axiawvalidi);

assign axiawreadyo = writeactivew && !reqwrq && ramaccepti && reqfifoacceptw;
assign axiwreadyo  = writeactivew &&              ramaccepti && reqfifoacceptw;
assign axiarreadyo = readactivew  && !reqrdq && ramaccepti && reqfifoacceptw;

wire [31:0] addrw   = ((reqwrq || reqrdq) ? reqaddrq:
                        writeactivew ? axiawaddri : axiaraddri);

wire wrw    = writeactivew && axiwvalidi;
wire rdw    = readactivew;

assign ramaddro       = addrw;
assign ramwritedatao = axiwdatai;
assign ramrdo         = rdw;
assign ramwro         = wrw ? axiwstrbi : 4'b0;
assign ramleno        = axiawvalidi ? axiawleni:
                          axiarvalidi ? axiarleni : 8'b0;

assign axibvalido  = respvalidw & respiswritew & respislastw;
assign axibrespo   = 2'b0;
assign axibido     = respidw;

assign axirvalido  = respvalidw & respisreadw;
assign axirrespo   = 2'b0;
assign axirido     = respidw;
assign axirlasto   = respislastw;

assign respacceptw    = (axirvalido & axirreadyi) | 
                          (axibvalido & axibreadyi) |
                          (respvalidw & respiswritew & !respislastw); 

endmodule

module tcmmempmemfifo2

#(
    parameter WIDTH   = 8,
    parameter DEPTH   = 4,
    parameter ADDRW  = 2
)
(
    
     input               clki
    ,input               rsti
    ,input  [WIDTH-1:0]  dataini
    ,input               pushi
    ,input               popi

    
    ,output [WIDTH-1:0]  dataouto
    ,output              accepto
    ,output              valido
);

localparam COUNTW = ADDRW + 1;

reg [WIDTH-1:0]         ram [DEPTH-1:0];
reg [ADDRW-1:0]        rdptr;
reg [ADDRW-1:0]        wrptr;
reg [COUNTW-1:0]       count;

always @ (posedge clki or posedge rsti)
if (rsti)
begin
    count   <= {(COUNTW) {1'b0}};
    rdptr  <= {(ADDRW) {1'b0}};
    wrptr  <= {(ADDRW) {1'b0}};
end
else
begin
    
    if (pushi & accepto)
    begin
        ram[wrptr] <= dataini;
        wrptr      <= wrptr + 1;
    end

    
    if (popi & valido)
        rdptr      <= rdptr + 1;

    
    if ((pushi & accepto) & ~(popi & valido))
        count <= count + 1;
    
    else if (~(pushi & accepto) & (popi & valido))
        count <= count - 1;
end

/* verilator lintoff WIDTH */
assign accepto   = (count != DEPTH);
assign valido    = (count != 0);
/* verilator linton WIDTH */

assign dataouto = ram[rdptr];



endmodule

module tcmmemram
(
    
     input           clk0i
    ,input           rst0i
    ,input  [ 13:0]  addr0i
    ,input  [ 31:0]  data0i
    ,input  [  3:0]  wr0i
    ,input           clk1i
    ,input           rst1i
    ,input  [ 13:0]  addr1i
    ,input  [ 31:0]  data1i
    ,input  [  3:0]  wr1i

    
    ,output [ 31:0]  data0o
    ,output [ 31:0]  data1o
);



/* verilator lintoff MULTIDRIVEN */
reg [31:0]   ram [16383:0] /*verilator public*/;
/* verilator linton MULTIDRIVEN */

reg [31:0] ramread0q;
reg [31:0] ramread1q;


always @ (posedge clk0i)
begin
    if (wr0i[0])
        ram[addr0i][7:0] <= data0i[7:0];
    if (wr0i[1])
        ram[addr0i][15:8] <= data0i[15:8];
    if (wr0i[2])
        ram[addr0i][23:16] <= data0i[23:16];
    if (wr0i[3])
        ram[addr0i][31:24] <= data0i[31:24];

    ramread0q <= ram[addr0i];
end

always @ (posedge clk1i)
begin
    if (wr1i[0])
        ram[addr1i][7:0] <= data1i[7:0];
    if (wr1i[1])
        ram[addr1i][15:8] <= data1i[15:8];
    if (wr1i[2])
        ram[addr1i][23:16] <= data1i[23:16];
    if (wr1i[3])
        ram[addr1i][31:24] <= data1i[31:24];

    ramread1q <= ram[addr1i];
end

assign data0o = ramread0q;
assign data1o = ramread1q;



endmodule


