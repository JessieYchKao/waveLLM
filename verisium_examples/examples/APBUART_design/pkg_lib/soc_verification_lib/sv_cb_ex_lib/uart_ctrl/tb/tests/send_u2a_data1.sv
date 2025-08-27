/*-------------------------------------------------------------------------
File name   : send_u2a_data1.sv
Title       : Test Case
Project     :
Created     :
Description : One test case for the APB-UART Environment
Notes       : The test creates a uart_ctrl_tb and sets the default
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/

class send_u2a_data1_test extends uvm_test;

  uart_ctrl_tb uart_ctrl_tb0;

  `uvm_component_utils(send_u2a_data1_test)

  function new(input string name, input uvm_component parent);
      super.new(name,parent);
  endfunction

  virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);

    //set_config_int("uart_ctrl_tb0.uart0.Tx.monitor", "checks_enable", 0);

    // set the default sequence for the virtual sequencer 
    uvm_config_db#(uvm_object_wrapper)::set(this, "uart_ctrl_tb0.virtual_sequencer.run_phase",
          "default_sequence", u2a_traffic_seq::type_id::get());
    uart_ctrl_tb0 = uart_ctrl_tb::type_id::create("uart_ctrl_tb0",this);
  endfunction : build_phase

endclass
