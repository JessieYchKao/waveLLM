/*-------------------------------------------------------------------------
File name   : u2a_incr_payload.sv
Title       : Test Case
Project     :
Created     :
Description : One test case for the APB-UART Environment
Notes       : The test creates a uart_ctrl_tb and sets the default
            : sequence for the sequencer as u2a_incr_payload
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/

class uart_incr_payload_test extends uvm_test;

  uart_ctrl_tb ve;

  `uvm_component_utils(uart_incr_payload_test)

  function new(input string name, 
                input uvm_component parent=null);
      super.new(name,parent);
  endfunction

  virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);

    //Move set_string to be a config parameter
    uvm_config_db#(uvm_object_wrapper)::set(this, "ve.virtual_sequencer.run_phase",
          "default_sequence", u2a_incr_payload::type_id::get());

    ve = uart_ctrl_tb::type_id::create("ve",this);
  endfunction : build_phase

endclass
