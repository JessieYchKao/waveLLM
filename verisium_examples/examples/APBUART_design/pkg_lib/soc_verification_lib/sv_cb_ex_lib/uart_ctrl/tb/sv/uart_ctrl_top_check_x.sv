/*-------------------------------------------------------------------------
File name   : uart_ctrl_top.sv
Title       : Top level file
Description : This file implements the top level test bench for the 
            : UART Controller environment
Notes       : The uart_ctrl_top module instantiates the UART DUT, 
            : APB master interface, UART interface and connects 
            : them appropriatly
----------------------------------------------------------------------*/
//   Copyright 1999-2010 Cadence Design Systems, Inc.
//   All Rights Reserved Worldwide
//
//   Licensed under the Apache License, Version 2.0 (the
//   "License"); you may not use this file except in
//   compliance with the License.  You may obtain a copy of
//   the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
//   Unless required by applicable law or agreed to in
//   writing, software distributed under the License is
//   distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
//   CONDITIONS OF ANY KIND, either express or implied.  See
//   the License for the specific language governing
//   permissions and limitations under the License.

// Interfaces
`include "apb_if.sv"
`include "apb_master_if.sv"
`include "apb_slave_if.sv"
`include "uart_if.sv"
`include "coverage/uart_ctrl_internal_if.sv"

module uart_ctrl_top;

  // c_write will call a C method that will, in turn, call the drive task
  // implemented within this module
  import "DPI-C" context task c_write(input int address, input int data);

  // print_it will print the address and data from C
  import "DPI-C" context function void print_it(input int address, input int data);

  // C code will call the drive task, to drive address and data onto the
  // c_addr and c_data lines
  export "DPI-C" task drive;  // Note – not a function prototype

  // Import the UVM Library and UVM macros
  import uvm_pkg::*;             //UVM Library Package
  `include "uvm_macros.svh"

  // Other packages
  import uart_pkg::*;       //UART UVC Package
  import apb_pkg::*;        //APB UVC Package
  import uart_ctrl_pkg::*;  //UART MODULE UVC Package

  // UART Controller testbench
  `include "uart_ctrl_tb.sv"

  // UART Controller tests (in ../tests directory)
  `include "test_lib.sv"
 
  reg clock;
  reg reset;
  
  // signals put in place to illustrate DPI calling
  reg [31:0] c_addr = 0;
  reg [31:0] c_data = 0;
  integer i = 0;


  wire [3:0] wb_sel;
  wire [31:0] dbus;
  wire [31:0] rdbus;
  wire [31:0] cbus;
  reg [2:0] div8_clk;

  apb_if                apb_if0(.pclock(clock), .preset(reset)); 
  //apb_if                apb_if0(.pclock(clock), .preset(reset), .prdata(rdbus[7:0]));
  apb_master_if         apb_mi0(.pclock(clock), .preset(reset));
  apb_slave_if          apb_si0(.pclock(clock), .preset(reset));
  uart_if               uart_if0(.clock(div8_clk[2]), .reset(reset));
  uart_ctrl_internal_if uart_int0(.clock(div8_clk[2]));

  assign cbus = rdbus;

  assign wb_sel = (apb_if0.paddr[1:0] == 0) ? 4'b0001 : (apb_if0.paddr[1:0] == 1 ? 4'b0010 : (apb_if0.paddr[1:0] == 2 ? 4'b0100 : 4'b1000)); 
  assign dbus = {4{apb_if0.pwdata[7:0]}};
  assign apb_if0.prdata[7:0] = rdbus[31:24] | rdbus[23:16] | rdbus[15:8] | rdbus[7:0];

  assign uart_int0.tx_fifo_ptr = uart_dut.regs.transmitter.tf_count;
  assign uart_int0.rx_fifo_ptr = uart_dut.regs.receiver.rf_count;

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
        .wb_adr_i(apb_if0.paddr[4:0]),
        .wb_dat_i(dbus),
        .wb_dat_o(rdbus),
        .wb_we_i(apb_if0.prwd),
        .wb_stb_i(apb_if0.psel[0]),
        .wb_cyc_i(apb_if0.psel[0]),
        .wb_ack_o(apb_if0.pready),
        .wb_sel_i(wb_sel),
	.int_o(), // interrupt request

	// UART	signals
	// serial input/output
	.stx_pad_o(uart_if0.rxd),
        .srx_pad_i(uart_if0.txd),

	// modem signals
	.rts_pad_o(rts_n),
        .cts_pad_i(uart_if0.cts_n),
        .dtr_pad_o(uart_if0.dtr_n),
        .dsr_pad_i(uart_if0.dsr_n),
        .ri_pad_i(uart_if0.ri_n),
        .dcd_pad_i(uart_if0.dcd_n)
  );

  // implement X checking in the test harness for the dummy rdbus
  check_x rdbus_x_checker(.reset(reset), .clock(clock), .select(wb_sel), .bus(rdbus));

  function bit _init_vif_function();
  // Configure Virtual Interfaces
  uvm_config_db#(virtual uart_ctrl_internal_if)::set(null, "uvm_test_top.uart_ctrl_tb0.uart_ctrl0.*", "vif", uart_int0);
  uvm_config_db#(virtual apb_if)::set(null, "uvm_test_top.uart_ctrl_tb0.apb0*", "vif", apb_if0);
  uvm_config_db#(virtual uart_if)::set(null, "uvm_test_top.uart_ctrl_tb0.uart0*", "vif", uart_if0);
  endfunction

  bit init_vif = _init_vif_function();

  initial begin
    // Set the time format for printed messages 
    $timeformat(-9,0,"ns",20);
    fork 
      // Run the UVM Test
      run_test();
    join
  end

  initial begin
    $display("%m: Driving %m.reset low at start of simulation");
    reset <= 1'b0;
    clock <= 1'b0;
`ifdef RESET_50 
    $display("%m: Holding %m.reset low for 50 time units");
    #50 reset <= 1'b1;
`else 
    $display("%m: Holding %m.reset low for 200 time units");
    #200 reset <= 1'b1;
    $display("%m: Driving %m.reset high");
`endif 
 
  end

  //Generate Clock
  always
    #5 clock = ~clock;

  final begin
    $display("=======================================================");
    $display("UART CONTROLLER DUT REGISTERS:");
    $displayh("uart_ctrl_top.uart_dut.regs.dl  =", uart_ctrl_top.uart_dut.regs.dl);
    $displayh("uart_ctrl_top.uart_dut.regs.fcr = ", uart_ctrl_top.uart_dut.regs.fcr);
    $displayh("uart_ctrl_top.uart_dut.regs.ier = ", uart_ctrl_top.uart_dut.regs.ier);
    $displayh("uart_ctrl_top.uart_dut.regs.iir = ", uart_ctrl_top.uart_dut.regs.iir);
    $displayh("uart_ctrl_top.uart_dut.regs.lcr = ", uart_ctrl_top.uart_dut.regs.lcr);
    $display("=======================================================");
  end


 // This SystemVerilog function calls the c_write
  // function, which is implemented in C code and 
  // accessed through the DPI 
  task write;
    input int addr;
    input int data;

    // call the imported DPI-C function c_write
    c_write(addr, data); 

    // call the imported DPI-C function print_it to
    // print the address and data to the screen/file 
    print_it(addr,data);
//kkaldjfkladjslkfajlksdj

  endtask


  // This task will simply drive the lines.  This task
  // is exported out to the C side to be called directly 
  // from C code 
  task drive; 
    input int addr;
    input int data;
    begin
     // simply place the values onto the lines
     c_addr <= addr;
     c_data <= data;
     #1;
    end  
  endtask

  initial begin
     forever begin
        @(posedge clock);
        // Loop forever, continously calling the write task
        // to send values into the c world
        write(i,i+1);
        i = i + 2;
     end // forever
  end // initial



endmodule : uart_ctrl_top
