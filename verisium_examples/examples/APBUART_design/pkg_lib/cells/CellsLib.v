`timescale 1ns/10ps

`celldefine
module INV(Y,A);
input A;
output Y;

specify
    specparam block_delay=0.42;
    (A=>Y)=(block_delay, block_delay);
endspecify
    
    buf(Y, O_int);
assign
        O_int =  ~A;
endmodule
`endcelldefine


`celldefine

`celldefine
module DFFR(CLR_,CLK,Q,Q_,D);
    input    CLR_;  // master clear asynchronous
    input    CLK; // clock
    output Q, Q_;
    input  D;

    reg    Q_int;

specify
    specparam block_delay = 1.10;
    (CLK=>Q)=(block_delay, block_delay);
    (CLK=>Q_)=(block_delay, block_delay);
    (CLR_=>Q)=(block_delay, block_delay);
    (CLR_=>Q_)=(block_delay, block_delay);
       specparam D$CLK$SU = 1;
       specparam D$CLK$HLD = 1;
        $setuphold(posedge CLK, posedge D, D$CLK$SU,D$CLK$HLD);
endspecify

    buf(Q, Q_int);
    not(Q_, Q_int);
   always @(CLR_)
      if (CLR_ == 0)
              assign Q_int = 1'b0;
           else
              deassign Q_int;

  always  @(posedge CLK) Q_int=D;
endmodule
`endcelldefine
