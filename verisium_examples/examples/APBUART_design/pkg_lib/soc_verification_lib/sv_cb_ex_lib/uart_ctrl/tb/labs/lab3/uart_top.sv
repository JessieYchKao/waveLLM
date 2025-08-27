/*-------------------------------------------------------------------------
File name   : uart_top.sv
Title       : Top level file
Project     : SystemVerilog UVM Lab
Created     :
Description : This file implements the top level test bench for the 
            : UART environment
Notes       :  
            : 
----------------------------------------------------------------------
Copyright  200*-2008 Cadence Design Systems, Inc. All rights reserved worldwide.
Please refer to the terms and conditions in the Kit documentation.
-------------------------------------------------------------------------*/

`define APB_ADDR_WIDTH 16

`include "uart_if.sv"

module uart_top;

  import uvm_pkg::*;             //UVM Library Package
  `include "uvm_macros.svh"

  import uart_pkg::*;       //UART UVC Package
  `include "uart_traffic_seq.sv"

  // UART Interface: Connects to driver/monitor/sequencer via a virtual interface
  // Also connects to DUT when it is included ( not in this lab)
  reg clock;
  reg reset;

  uart_if uif0(.reset(reset), .clock(clock));

  //  UART UVC
  uart_env uart0;    // Instance of the UART UVC    //lab3_note1
  uart_config dut_csr;  // UART Configuration

  initial begin     //lab3_note2
    set_config_int("*", "recording_detail", 1);
    // Create the UART instance
    uart0 = uart_env::type_id::create("uart0", null);     //lab3_note3

    //Create and assign the UART UVC config after building the environment
    dut_csr = uart_config::type_id::create("dut_csr");     //lab3_note4
    void'(dut_csr.randomize());                          

    //--------------------------------------------------------------//
    // LAB 3 - Configure the UVC before building it's sub-components
    //--------------------------------------------------------------//
    //dut_csr.is_tx_active = UVM_PASSIVE;    //lab3_note4
    //dut_csr.is_rx_active = UVM_PASSIVE;    //lab3_note4

    uvm_config_db#(uart_config)::set(null, "uart0.*", "cfg", dut_csr); // lab3_note5

    // Virtual Interface Assignments
    uvm_config_db#(virtual uart_if)::set(null,"uart0*","vif", uif0);  // lab3_note6
   
    // Specify sequence to be executed
    uvm_config_wrapper::set(null, "*.Tx.sequencer.run_phase", "default_sequence",
                            uart_traffic_seq::type_id::get());        // lab3_note7
 
    // Global UVM task - starts the simulation
     run_test();
 end

  initial begin     //lab3_note3d
    uif0.has_checks = 0;
    reset <= 1'b0;
    clock <= 1'b0;

    // Print topology; objection is used to ensure that it is always printed
    //  even if no sequence is exec. 
    uvm_test_done.raise_objection(null); 
    #1 uart0.print(); 
       dut_csr.print();
       uvm_test_done.drop_objection(null); 
    #50 reset <= 1'b1;
  end

  //Generate Clock
  always #5 clock = ~clock;

endmodule
