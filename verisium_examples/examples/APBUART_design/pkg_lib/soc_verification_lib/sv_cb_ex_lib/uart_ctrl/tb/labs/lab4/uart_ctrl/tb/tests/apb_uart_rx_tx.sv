/*-------------------------------------------------------------------------
File name   : apb_uart_rx_tx.sv
Title       : Test Case
Project     :
Created     :
Description : One test case for the APB-UART Environment
Notes       : The test creates a uart_ctrl_tb and sets the default
            : sequence for the sequencer as concurrent_u2a_a2u_rand_trans
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/

class u2a_a2u_full_rand_test extends uvm_test;

  uart_ctrl_tb ve;

  `uvm_component_utils(u2a_a2u_full_rand_test)

  function new(input string name, 
                input uvm_component parent=null);
      super.new(name,parent);
  endfunction

  virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);

    uvm_config_db#(uvm_object_wrapper)::set(this, "ve.virtual_sequencer.run_phase",
          "default_sequence", concurrent_u2a_a2u_rand_trans::type_id::get());

    ve = uart_ctrl_tb::type_id::create("ve",this);

  endfunction : build_phase

endclass
