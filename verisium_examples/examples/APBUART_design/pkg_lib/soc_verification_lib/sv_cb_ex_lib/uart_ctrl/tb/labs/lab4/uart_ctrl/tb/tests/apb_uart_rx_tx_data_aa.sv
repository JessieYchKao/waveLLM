/*-------------------------------------------------------------------------
File name   : apb_uart_rx_tx_data_aa.sv
Title       : Test Case
Project     :
Created     :
Description : One test case for the APB-UART Environment
Notes       : The test creates a uart_ctrl_tb and sets the default
            : sequence for the sequencer as concurrent_u2a_a2u_rand_trans
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/

class uart_frame_aa extends uart_pkg::uart_frame;
  `uvm_object_utils(uart_frame_aa)  
  constraint payload_ct  { payload == 8'haa; }
endclass : uart_frame_aa

class apb_uart_rx_tx_data_aa extends u2a_a2u_full_rand_test;

  `uvm_component_utils(apb_uart_rx_tx_data_aa)

  function new(input string name, 
                input uvm_component parent=null);
      super.new(name,parent);
  endfunction

  virtual function void build_phase(uvm_phase phase);
    set_type_override_by_type(uart_pkg::uart_frame::get_type(), uart_frame_aa::get_type());
    super.build_phase(phase);
  endfunction : build_phase

endclass
