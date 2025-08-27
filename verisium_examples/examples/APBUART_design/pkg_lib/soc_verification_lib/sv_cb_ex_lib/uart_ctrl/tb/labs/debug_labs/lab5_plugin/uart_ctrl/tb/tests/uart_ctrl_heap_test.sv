/*-------------------------------------------------------------------------
File name   : uart_ctrl_heap_test.sv 
Title       : Test Case
Project     :
Created     :
Description : Simple memoery leakage tests for the uart_ctrl device
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/

//----------------------------------------------------------------------------
// SEQUENCE: do_something_seq - for the virtual sequencer
//----------------------------------------------------------------------------
//class do_something_seq extends uvm_sequence;
class do_something_seq extends base_vseq;
  concurrent_u2a_a2u_rand_trans_vseq my_vseq;

//  `uvm_sequence_utils(do_something_seq,apb_uart_virtual_sequencer )
  `uvm_object_utils(do_something_seq)
   task body();
    uvm_report_info("do_something_seq","Doing Nothing First", UVM_NONE);
#2000
    uvm_report_info("do_something_seq",
                  "Doing concurrent_u2a_a2u_rand_trans_vseq sequence NOW", UVM_NONE);
    `uvm_do(my_vseq);
   endtask
endclass

//-------------------------------------------------------------------------//
// TEST: uart_ctrl_heap_test - runs the nested sequences for heap analyzer
//-------------------------------------------------------------------------//
class uart_ctrl_heap_test extends uvm_test;

  uart_ctrl_tb ve;

  `uvm_component_utils(uart_ctrl_heap_test)

  function new(input string name, input uvm_component parent=null);
      super.new(name,parent);
  endfunction

  virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);
//    set_config_string("ve.virtual_sequencer", "default_sequence", "do_something_seq");
    uvm_config_db#(uvm_object_wrapper)::set(this, "ve.virtual_sequencer.run_phase",
          "default_sequence", do_something_seq::type_id::get());
    
    set_config_int("*", "recording_detail", UVM_FULL);
    ve = uart_ctrl_tb::type_id::create("ve",this);
    // uvm_top.set_report_verbosity_level_hier(UVM_NONE);
    // uvm_top.tb.apb0.bus_monitor.set_report_verbosity_level_hier(UVM_FULL);
  endfunction : build_phase

  task run();
	  factory.print(0);
  endtask

endclass :  uart_ctrl_heap_test
