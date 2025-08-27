`timescale 1 ns / 10 ps
module gl_top;
 reg t_d,t_clr,start;

 dff I1(.clr(t_clr), .ck(t_ck), .d(t_d), .q(t_q), .qb(t_qb), .fjk(tmp));
 dff I2(.clr(t_clr), .ck(t_ck), .d(t_d), .q(t_q), .qb(t_qb), .fjk(tmp));
 dff I3(.clr(t_clr), .ck(t_ck), .d(t_d), .q(t_q), .qb(t_qb), .fjk(tmp));
 nand #20 (t_ck,t_ck,start);

 initial
  begin
   start =0;
   forever begin 
      #20 start = ~start;
   //#20 start =1;
   end //forever
 end

 initial
  begin
   for (int i = 0; i< 5; i++) begin 
      t_clr =1;
      t_d = 1;
      #15 t_clr =0;
      //#3 t_clr =1;
      @(negedge t_ck) t_d =0;
       #10 t_d =1;
      @(negedge t_ck) #6 t_d =0;
      @(posedge t_ck) #5 t_d =1;
      #50; 
   end // for 
  // $finish;
 end

 //INV_A xx(.Y(tmp), .A(t_d));
endmodule
