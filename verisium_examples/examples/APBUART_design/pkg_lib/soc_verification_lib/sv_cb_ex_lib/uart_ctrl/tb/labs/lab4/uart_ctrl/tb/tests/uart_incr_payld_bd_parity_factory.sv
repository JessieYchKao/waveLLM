/*-------------------------------------------------------------------------
File name   : uart_incr_payld_bd_parity_factory.sv
Title       : Test Case
Project     :
Created     :
Description : One test case for the APB-UART Environment
Notes       : The test creates a uart_ctrl_tb and sets the default
            : sequence for the sequencer as concurrent_u2a_a2u_rand_trans
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/

class uart_bd_parity_frame extends uart_frame;
  `uvm_object_utils(uart_bd_parity_frame)  
   
  constraint default_parity_type { 
               parity_type dist {GOOD_PARITY := 10,
                                 BAD_PARITY  := 90};
              }

  function new(string name = "");
	  super.new(name);
  endfunction 

endclass : uart_bd_parity_frame

class uart_parity_en extends uart_config;
  `uvm_object_utils(uart_parity_en)  
   
  constraint c_parity_en  { parity_en == 1'b1; }

  function new(string name = "");
	  super.new(name);
  endfunction 
endclass : uart_parity_en

class uart_bd_parity_frame_test extends u2a_a2u_full_rand_test;

  `uvm_component_utils(uart_bd_parity_frame_test)

  function new(input string name, 
                input uvm_component parent=null);
      super.new(name,parent);
  endfunction

  virtual function void build_phase(uvm_phase phase);
    set_type_override_by_type(uart_frame::get_type(), uart_bd_parity_frame::get_type());
    set_type_override_by_type(uart_config::get_type(), uart_parity_en::get_type());
    super.build_phase(phase);
  endfunction : build_phase

endclass
