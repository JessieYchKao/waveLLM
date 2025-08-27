/*-------------------------------------------------------------------------
File name   : lab2_top.sv
Title       : 
Project     : SystemVerilog UVM Lab
Created     :
Description : Simple UVM Sequencer/Driver Test
Notes       :  
----------------------------------------------------------------------
Copyright  200*-2011 Cadence Design Systems, Inc. All rights reserved worldwide.
Please refer to the terms and conditions in the Kit documentation.
-------------------------------------------------------------------------*/

//---------------------------------------------------------------//
// LAB 2: Simple UVM Sequencer/Driver Test
//---------------------------------------------------------------//
module lab2_top;

import uvm_pkg::*;            // import the UVM library
`include "uvm_macros.svh"     // Include the UVM macros
`include "uart_frame.sv"  // includes the uart_frame definition

//---------------------------------------------------------------//
//  SEQUENCER DEFINITION
//---------------------------------------------------------------//
class uart_sequencer extends uvm_sequencer #(uart_frame);  //lab2_note1

// Required macro for UVM automation and utilities
`uvm_component_utils(uart_sequencer)           //lab2_note2

// Constructor: Required UVM syntax
function new(string name, uvm_component parent);
  super.new(name, parent);
endfunction : new

endclass : uart_sequencer

//---------------------------------------------------------------//
//  DRIVER DEFINITION
//---------------------------------------------------------------//
class uart_tx_driver extends uvm_driver #(uart_frame);    //lab2_note3

int frames_sent;

// Provides automation and utilities
`uvm_component_utils(uart_tx_driver)         //lab2_note4

// UVM run_phase()
task run_phase(uvm_phase phase); 
  forever begin
    // get item from the sequencer
    seq_item_port.get_next_item(req);
    frames_sent++;
    // send the item to the DUT
    send_to_dut(req);
    // call sequencer's item_done
    seq_item_port.item_done();
  end
endtask : run_phase

task send_to_dut(uart_frame frame);
  // This simple driver, waits the delay and then prints the frame
  #10  void'(begin_tr(frame, "Driver Frame"));
  `uvm_info(get_type_name(), $psprintf("Driver Sending Frame %0d\n%s",
            frames_sent, frame.sprint()), UVM_LOW)
  repeat (frame.delay)
    #10;
  `uvm_info(get_type_name(), $psprintf("Frame Sent with delay of %0d clocks",
            frame.delay), UVM_MEDIUM)
  end_tr(frame);
endtask : send_to_dut

// Constructor - Required syntax
function new(string name, uvm_component parent);
  super.new(name, parent);
endfunction : new

function void report_phase(uvm_phase phase);
  `uvm_info(get_type_name(), "----------------------------------", UVM_NONE)
  `uvm_info(get_type_name(), $psprintf("End of Test: Driver Sent %0d Frames", frames_sent), UVM_NONE)
  `uvm_info(get_type_name(),  "----------------------------------\n", UVM_NONE)
endfunction : report_phase

endclass : uart_tx_driver

//---------------------------------------------------------------//
//  SIMPLE SEQUENCE DEFINITION
//---------------------------------------------------------------//
class simple_sequence  extends uvm_sequence #(uart_frame); // lab_note5
  
  // Required macro for sequences automation
  `uvm_object_utils(simple_sequence)

  // Constructor
  function new(string name="simple_sequence");
    super.new(name);
  endfunction

  task pre_body();
    starting_phase.raise_objection(this, get_type_name());
    uvm_test_done.set_drain_time(this, 200ns);
    `uvm_info(get_type_name(), "End-of-test Objection Raised", UVM_MEDIUM)
  endtask : pre_body
  
  task body();
    for (int i=0; i<5; i++) begin
      req = uart_frame::type_id::create("req");
      start_item(req);
      void'(req.randomize());
      finish_item(req);
      //NOTE: The four lines above can be replaced with this UVM macro:
      //  `uvm_do(req)
    end
  endtask

  task post_body();
    starting_phase.drop_objection(this, get_type_name());
    `uvm_info(get_type_name(), "End-of-test Objection Dropped", UVM_MEDIUM)
  endtask : post_body

endclass : simple_sequence


//---------------------------------------------------------------//
// LAB 2B: SEQUENCE LIBRARY - Uncomment the next line for Lab2B
//---------------------------------------------------------------//
//  `include "uart_seq_lib.sv"                   //lab2_note10

//lab2_note6
//---------------------------------------------------------------//
//  Simple Sequencer/Driver Test
//---------------------------------------------------------------//
// Driver and Sequencer Instances
uart_sequencer  sequencer;
uart_tx_driver  driver;

initial begin
  // Enable Transaction Recording
  set_config_int("*", "recording_detail", 1);

  //Specify sequence to be executed
   uvm_config_wrapper::set(null, "sequencer.run_phase", "default_sequence",
                           simple_sequence::type_id::get());     //lab2_note7
  //-----------------------------------------------------------------------//
  // LAB 2B: set the default sequence to be uart_incr_payload_seq (comment out above)
  //-----------------------------------------------------------------------//
  // uvm_config_wrapper::set(null, "sequencer.run_phase", "default_sequence",
  //                         uart_nested_seq::type_id::get());     //lab2_note11

  // Construct the driver and sequencer
  sequencer = new("sequencer", null);
  driver = new("driver", null);
  
  // Connect the driver to the sequencer
  driver.seq_item_port.connect(sequencer.seq_item_export);   //lab2_note8
  
  // Print the driver and sequencer using UVM built-in automation
  `uvm_info("lab2_top", "\n**** Printing the Driver ****", UVM_LOW)
  driver.print();
  `uvm_info("lab2_top", "\n**** Printing the Sequencer ****", UVM_LOW)
  sequencer.print();
   
  // Global task that is part of UVM - starts a simulation
  run_test(); //lab2_note9
end

endmodule : lab2_top
