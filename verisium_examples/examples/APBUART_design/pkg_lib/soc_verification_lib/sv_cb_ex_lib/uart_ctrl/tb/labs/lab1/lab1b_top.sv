/*-------------------------------------------------------------------------
File name   : lab1b_top.sv
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
module lab1_top;

import uvm_pkg::*;              // import the UVM library
`include "uvm_macros.svh"       // Include the UVM macros
`include "uart_frame.sv"    // include the packet definition

//==================================================================
//LAB 1B: Extending the uart_frame class with constraints
//==================================================================
// class test1_frame extends uart_frame;
//   "YOUR CONSTRAINT HERE"
// endclass : test1_frame
//==================================================================

//-------------------------------------------------------------------
// Simple frame generator class: In a loop, generates random frames
// and sends them via a send_to_dut() task.
//-------------------------------------------------------------------
class frame_generator;
//==================================================================
// LAB 1B: replace uart_frame with test1_frame
//==================================================================
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
  #10 `uvm_info("lab1_top",("----------------------------------------------------------"), UVM_NONE)
      `uvm_info("lab1_top", $psprintf(" Test Completed Successfully: Generator Sent %0d Frames", generator.count), UVM_NONE)
      `uvm_info("lab1_top", ("-----------------------------------------------------------\n"), UVM_NONE)
  $finish;
end

//----------------------------------------------------------------
// Simple Implementation of send_to_dut()
// This implementation shows the UVM built-in automation
//----------------------------------------------------------------
task send_to_dut (input uart_frame frame);
uart_frame frame1, frame2;  // for UVM automation
static int     frame_count;
  begin
    // UVM AUTOMATION: Print the frame
   `uvm_info("send_to_dut", $psprintf("Printing the UART frame\n%s", frame.sprint()), UVM_MEDIUM)
  
    // Create a new frame1
    frame1 = new();
    // UVM AUTOMATION: Copy Usage
    `uvm_info("send_to_dut", ("Copying the UART frame"), UVM_HIGH)
    frame1.copy(frame);
    `uvm_info("send_to_dut", $psprintf("Copied Frame is: \n%s", frame1.sprint()), UVM_HIGH)
    
    // UVM AUTOMATION: Clone Usage
    `uvm_info("send_to_dut", ("Cloning the UART frame"), UVM_HIGH)
    if (!$cast(frame2, frame.clone()))
      `uvm_fatal ("CASTFL", "Failed to cast frame to frame2 in send_to_dut")
  
    // UVM AUTOMATION:  Rename the cloned frame
    frame2.set_name($sformatf("FRAME[%0d]",frame_count++));
    `uvm_info("send_to_dut", $psprintf("Cloned Frame is: \n%s", frame2.sprint()), UVM_HIGH)
  end
endtask : send_to_dut

endmodule : lab1_top
