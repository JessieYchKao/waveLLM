/*-------------------------------------------------------------------------
File name   : uart_seq_lib.sv
Title       : sequence library file for uart uvc
Project     : SystemVerilog UVM Lab
Created     :
Description : describes UART UVC sequences
Notes       :  
----------------------------------------------------------------------
Copyright  200*-2011 Cadence Design Systems, Inc. All rights reserved worldwide.
Please refer to the terms and conditions in the Kit documentation.
-------------------------------------------------------------------------*/

////////////////////////////////////////////////////////////////////////////////
// UART SEQUENCE LIBRARY
////////////////////////////////////////////////////////////////////////////////  

//=========================================================================
//  SEQUENCE: uart_base_seq : This BASE sequence incorporates the objection
//  mechanism into the pre/post_body() tasks.  All active UART sequences
//  can extend from this to get the objection mechanism .
//=========================================================================
class uart_base_seq extends uvm_sequence #(uart_frame);  // lab2_note1
  
  // Required macro for sequences automation
  `uvm_object_utils(uart_base_seq)

  // Constructor
  function new(string name="uart_base_seq");
    super.new(name);
  endfunction

  task pre_body();
    starting_phase.raise_objection(this, get_type_name());
    `uvm_info(get_type_name(), "raise objection", UVM_MEDIUM)
    uvm_test_done.set_drain_time(this, 200ns);
  endtask : pre_body

  task post_body();
    starting_phase.drop_objection(this, get_type_name());
    `uvm_info(get_type_name(), "drop objection", UVM_MEDIUM)
  endtask : post_body

endclass : uart_base_seq

//=========================================================================
//  SEQUENCE: uart_incr_payload_seq
//  Generates random frames with consecutive incrementing payload (+3)
//=========================================================================
class uart_incr_payload_seq extends uart_base_seq;

    function new(string name="uart_incr_payload_seq");
      super.new(name);
    endfunction
   // register sequence with a sequencer 
   `uvm_object_utils(uart_incr_payload_seq)  //PH>

    rand int unsigned cnt;
    rand bit [7:0] start_payload;

    constraint count_ct {cnt >1; cnt <= 5;}   // modified for Workshop Lab

    virtual task body();
      uvm_report_info("uart_incr_payload_seq",$psprintf("Executing %0d times", cnt), UVM_LOW);
      for (int i = 0; i < cnt; i++)
      begin
        `uvm_do_with(req, {payload == start_payload +i*3; })
      end
    endtask
endclass: uart_incr_payload_seq

//=========================================================================
//  SEQUENCE: uart_bad_parity_seq
//  Generates random frames with BAD parity
//=========================================================================
class uart_bad_parity_seq extends uart_base_seq;  //PH>

    function new(string name="uart_bad_parity_seq");
      super.new(name);
    endfunction
   // register sequence with a sequencer 
   `uvm_object_utils(uart_bad_parity_seq)  //PH>

    rand int unsigned cnt;
    rand bit [7:0] start_payload;
    constraint count_ct {cnt >0; cnt <= 3;}   // Modified for Workshop labs

    virtual task body();
      uvm_report_info("uart_bad_parity_seq", $psprintf("Executing %0d times", cnt), UVM_LOW);
      // Create the frame ONLY once
      `uvm_create(req)
      // Disable the constraint on the parity
      req.default_parity_type.constraint_mode(0);
      for (int i = 0; i < cnt; i++)
      begin
        // Now send the packed with parity constrained to BAD_PARITY
        `uvm_rand_send_with(req, { parity_type == BAD_PARITY;})
      end
    endtask
endclass: uart_bad_parity_seq

//=========================================================================
//  SEQUENCE: uart_transmit_seq
//  Generates a random stream of frames
//=========================================================================
class uart_transmit_seq extends uart_base_seq;  //PH>
   // register sequence with a sequencer 
  `uvm_object_utils(uart_transmit_seq)  //PH>

   rand int unsigned NumOfTx;
   
   function new(string name="uart_transmit_seq");
      super.new(name);
   endfunction

   constraint NumOfTx_ct { NumOfTx >0; NumOfTx <= 10; }

   virtual task body();
     uvm_report_info("uart_transmit_seq", $psprintf("Executing %0d times", NumOfTx), UVM_LOW);
     for (int i = 0; i < NumOfTx; i++) begin
        `uvm_do(req)
     end
   endtask: body
endclass: uart_transmit_seq

//=========================================================================
//  SEQUENCE: uart_nested_seq :executes three sequences 
//=========================================================================
class uart_nested_seq extends uart_base_seq;  // lab2_note2

  uart_incr_payload_seq incr_payload_seq;    
  uart_bad_parity_seq   bad_parity_seq;
  uart_transmit_seq     transmit_seq;

  `uvm_object_utils(uart_nested_seq)

   virtual task body();
     uvm_report_info(get_type_name(), "Executing", UVM_LOW);
       `uvm_do_with(incr_payload_seq, {cnt==3;})
       `uvm_do(bad_parity_seq)
       `uvm_do_with(transmit_seq, {NumOfTx==3;})
   endtask: body
endclass: uart_nested_seq

//lab2_note3
//-------------------------------------------------------------------//
// LAB2 - OPTIONAL:  Create Your Own Sequence
//-------------------------------------------------------------------//
/*
class YOUR_SEQUENCE extends uvm_sequence #(uart_frame);

// uvm_SEQUENCE_utils registers a sequence with a sequencer
`uvm_object_utils(YOUR_SEQUENCE) 

// Constructor: Required syntax for UVM automation and utilities
  function new(string name = "YOUR_SEQUENCE");
    super.new(name);
  endfunction

virtual task body();
  begin
    uvm_report_info("YOUR_SEQUENCE", "Executing", UVM_LOW);
     // YOUR BODY GOES HERE
     // `uvm_do(req)
     // `uvm_do_with(req, {....;})
  end
endtask : body

endclass
*/
