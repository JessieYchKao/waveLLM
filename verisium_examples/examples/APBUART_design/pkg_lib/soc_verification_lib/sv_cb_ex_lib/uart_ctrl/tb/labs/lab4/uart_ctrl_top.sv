/*-------------------------------------------------------------------------
File name   : uart_ctrl_top.sv
Title       : Top level file
Description : This file implements the top level test bench for the 
            : APB-UART environment
Notes       : The uart_tb_top module instantiates the UART DUT, 
            : APB master interface, UART interface and connects 
            : them appropriatly
----------------------------------------------------------------------*/

`define APB_ADDR_WIDTH 16
`define HAS_SCBD

`include "apb_if.sv"
`include "uart_if.sv"
`include "coverage/uart_ctrl_internal_if.sv"


module uart_tb_top;
  import uvm_pkg::*;         //UVM Library Package

  import uart_pkg::*;        //UART UVC Package
  import apb_pkg::*;         //APB UVC Package
  import uart_ctrl_pkg::*;

  `include "uart_ctrl_tb.sv"
  `include "test_lib.sv"
 
  reg clock;
  reg reset;

  wire [3:0] wb_sel;
  wire [31:0] dummy_dbus;
  reg [2:0] div8_clk;

  apb_if apbi0(.pclock(clock), .preset(reset));
  uart_if uif0(.clock(div8_clk[2]), .reset(reset));
  uart_ctrl_internal_if uart_int0(.clock(div8_clk[2]));

  assign wb_sel = (apbi0.paddr[1:0] == 0) ? 4'b0001 : (apbi0.paddr[1:0] == 1 ? 4'b0010 : (apbi0.paddr[1:0] == 2 ? 4'b0100 : 4'b1000)); 
  assign dummy_dbus = {4{apbi0.pwdata[7:0]}};

// assign uart_int0.tx_fifo_ptr  = uart_tb_top.uart_dut.ua_tx_fifo1.byte_counter;  
// assign uart_int0.rx_fifo_ptr  = uart_tb_top.uart_dut.ua_rx_fifo1.byte_counter ;  

//--------------------------------------------------------------
initial begin
    uvm_config_db#(virtual apb_if)::set(null,"uvm_test_top.ve.apb0*","vif", apbi0); 
    uvm_config_db#(virtual uart_if)::set(null,"uvm_test_top.ve.uart0*","vif", uif0); 
    uvm_config_db#(virtual uart_ctrl_internal_if)::set(null,"*.uart_ctrl0.*","vif", uart_int0); 
end
//-------------------------------------------------------------

 always @(posedge clock) begin
   if (!reset)
     div8_clk = 3'b000;
   else
     div8_clk = div8_clk + 1;
 end

  //RTL Instantiation
  uart_top uart_dut(
	.wb_clk_i(clock), 
	
	// Wishbone signals
	.wb_rst_i(~reset),
    .wb_adr_i(apbi0.paddr[4:0]),
    .wb_dat_i(dummy_dbus),
    .wb_dat_o(apbi0.prdata[15:0]),
    .wb_we_i(apbi0.prwd),
    .wb_stb_i(apbi0.psel[0]),
    .wb_cyc_i(apbi0.psel[0]),
    .wb_ack_o(apbi0.pready),
    .wb_sel_i(wb_sel),
//	.int_o(apbi0.ua_int), // interrupt request

	// UART	signals
	// serial input/output
	.stx_pad_o(uif0.rxd),
    .srx_pad_i(uif0.txd),

	// modem signals
	.rts_pad_o(rts_n),
    .cts_pad_i(uif0.cts_n),
    .dtr_pad_o(uif0.dtr_n),
    .dsr_pad_i(uif0.dsr_n),
    .ri_pad_i(uif0.ri_n),
    .dcd_pad_i(uif0.dcd_n)
  );


  initial begin
    run_test();
  end

  initial begin
    reset <= 1'b0;
    clock <= 1'b0;
    #51 reset <= 1'b1;
  end

  //Generate Clock
  always
    #5 clock = ~clock;

endmodule
