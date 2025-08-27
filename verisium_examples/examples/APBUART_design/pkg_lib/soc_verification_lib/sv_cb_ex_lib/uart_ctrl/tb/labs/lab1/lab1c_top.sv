/*-------------------------------------------------------------------------
File name   : lab1c_top.sv
Title       : 
Project     : SystemVerilog UVM Lab
Created     :
Description : A simple frame generator test
Notes       :  
----------------------------------------------------------------------
Copyright  200*-2008 Cadence Design Systems, Inc. All rights reserved worldwide.
Please refer to the terms and conditions in the Kit documentation.
-------------------------------------------------------------------------*/

//----------------------------------------------------------------------//
// LAB 1: A simple frame generator test
//----------------------------------------------------------------------//
module lab1c_top;

import uvm_pkg::*;              // import the UVM library
`include "uvm_macros.svh"       // Include the UVM macros
`include "uart_frame.sv"    // include the packet definition

//-------------------------------------------------------------------
// Simple frame generator class: In a loop, generates random frames
// and sends them via a send_to_dut() task.
//-------------------------------------------------------------------
class frame_generator;
  uart_frame uart_frame;
  rand int count = 5;
  // default constraint for count
  constraint c1 { count > 0; count <= 10; }

  task gen_and_push();
    `uvm_info("frame_generator", ("Entering gen_and_push() task"), UVM_HIGH)
    uart_frame = new();
    for(int i = 0; i < count; i++) begin
      `uvm_info("frame_generator", $psprintf("Generating Data item %0d for uart frame ", i+1), UVM_LOW)
      void'(uart_frame.randomize());
      // Send the frame to the DUT
      send_to_dut(uart_frame);
    end
  endtask : gen_and_push
endclass : frame_generator

// Instance of the Frame Generator
frame_generator generator;

//-------------------------------------------------------------------
// Test:  Construct and randomize the generator and then call the
//        generator's gen_and_push() task.
//--------------------------------------------------------------------
initial begin
// Construct the generator
  generator = new();
// Randomize the generator - randomizes the number of frames to generate
  void'(generator.randomize());
// Generate Stimulus 
  generator.gen_and_push();
// End the simulation
  #10 `uvm_info("lab1c_top",("----------------------------------------------------------"), UVM_NONE)
      `uvm_info("lab1c_top", $psprintf(" Test Completed: Generator Sent %0d Frames", generator.count), UVM_NONE)
      `uvm_info("lab1c_top", ("-----------------------------------------------------------\n"), UVM_NONE)
  $finish;
end
//----------------------------------------------------------------
// Simple Implementation of send_to_dut()
// This implementation shows the UVM built-in automation
//----------------------------------------------------------------
task send_to_dut (input uart_frame frame);
uart_frame frame1, frame2;  // for UVM automation
static int     frame_count;
    // UVM AUTOMATION: Print the frame using the default_tree_printer
   `uvm_info("send_to_dut", $psprintf("Printing the UART frame\n%s", 
             frame.sprint(uvm_default_tree_printer)),    //lab1c_note_1
              UVM_MEDIUM)
endtask : send_to_dut

endmodule : lab1c_top
