/*-------------------------------------------------------------------------
File name   : uart_bad_driver_factory_lab3.sv
Title       : Test Case
Project     :
Created     :
Description : One test case for the APB-UART Environment
Notes       : The test creates a uart_ctrl_tb and sets the default
            : sequence for the sequencer as concurrent_u2a_a2u_rand_trans
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/

class uart_bad_driver_factory extends u2a_a2u_full_rand_test;

  `uvm_component_utils(uart_bad_driver_factory)

  function new(input string name, 
                input uvm_component parent=null);
      super.new(name,parent);
  endfunction

  virtual function void build_phase(uvm_phase phase);
    // uncomment the next line to replace Good Bfm with Bad Bfm that will corrupt the parity bit
    // set_type_override_by_type(uart_tx_driver::get_type(), uart_tx_bad_driver::get_type());
    set_type_override_by_type(uart_config::get_type(), uart_parity_en::get_type());
    super.build_phase(phase);
  endfunction : build_phase

endclass
