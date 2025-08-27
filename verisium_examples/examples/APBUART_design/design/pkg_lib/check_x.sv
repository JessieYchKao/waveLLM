`ifdef PING_PONG
// This module will create a zero width glitch delay that will cause a ping pong
// to occur between the two always blocks below
module ping_pong();
  reg a, b;
  reg corey, corey1;

  initial begin
    #1 b = 1'b1;
    #1;
    $finish;
  end

  always @(*)
    begin
      //$display("Entering first block");
      a = 1'b0;
      case(b)
        1'b1 : a = 1'b1;
      endcase
    end

  always @(*)
    begin
      //$display("Entering second block");
      b = 1'b0;
      case(a)
        1'b1 : b = 1'b1;
      endcase
    end
endmodule
`endif








//This module is a simple X checker for any 32 bit bus
module check_x(reset, clock, select, bus);

  parameter check_x_startup_delay = 400; 
  input reset;
  input clock;
  input wire [3:0] select;
  input wire [31:0] bus;

`ifdef PING_PONG
  ping_pong ping_pong_inst();
`endif

  bit check_x_enable = 1'b0;
  bit local_clk = 0;
  integer clock_counter = 0;
  bit local_clk_inv = 1;
  
  property x7_0; 
     @(negedge clock & check_x_enable & reset & select == 4'b0001)(^bus[7:0]   !== 1'bx);
  endproperty
  property x15_8; 
     @(negedge clock & check_x_enable & reset & select == 4'b0010) (^bus[15:8]  !== 1'bx);
  endproperty
  property x23_16; 
    @(negedge clock & check_x_enable & reset & select == 4'b0100) (^bus[23:16] !== 1'bx);
  endproperty
  property x31_24; 
    @(negedge clock & check_x_enable & reset & select == 4'b1000) (^bus[31:24] !== 1'bx);
  endproperty
  property x31_0; 
    @(posedge clock & check_x_enable & reset & select == 4'b1111) (^bus[31:0]  !== 1'bx);
  endproperty

  assert property(x7_0);
  assert property(x15_8);
  assert property(x23_16);
  assert property(x31_24);
  assert property(x31_0);

  //bus_check_x7_0:   assert property (@(negedge clock & check_x_enable & reset & select == 4'b0001) (^bus[7:0]   !== 1'bx)); 
  //bus_check_x15_8:  assert property (@(negedge clock & check_x_enable & reset & select == 4'b0010) (^bus[15:8]  !== 1'bx)); 
  //bus_check_x23_16: assert property (@(negedge clock & check_x_enable & reset & select == 4'b0100) (^bus[23:16] !== 1'bx)); 
  //bus_check_x31_24: assert property (@(negedge clock & check_x_enable & reset & select == 4'b1000) (^bus[31:24] !== 1'bx)); 
  //bus_check_x31_0:  assert property (@(posedge clock & check_x_enable & reset & select == 4'b1111) (^bus[31:0]  !== 1'bx)); 

  initial begin
   //wait a delay at the beginning to avoid startup conditions
   #check_x_startup_delay;
   check_x_enable = 1'b1;
  end // initial 

`ifdef HANG 
  initial begin 
     #10000;
     forever begin 
        local_clk = ~local_clk;
        clock_counter += 1;  
        local_clk_inv = ~local_clk;
     end // forever 
  end // initial 
`endif  
 
endmodule
