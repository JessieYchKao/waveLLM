/*-------------------------------------------------------------------------
File name   : uart_seq_lib.sv
Title       : sequence library file for uart uvc
Project     :
Created     :
Description : describes all UART UVC sequences
Notes       :  
----------------------------------------------------------------------*/
//   Copyright 1999-2010 Cadence Design Systems, Inc.
//   All Rights Reserved Worldwide
//
//   Licensed under the Apache License, Version 2.0 (the
//   "License"); you may not use this file except in
//   compliance with the License.  You may obtain a copy of
//   the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
//   Unless required by applicable law or agreed to in
//   writing, software distributed under the License is
//   distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
//   CONDITIONS OF ANY KIND, either express or implied.  See
//   the License for the specific language governing
//   permissions and limitations under the License.
//----------------------------------------------------------------------
//-------------------------------------------------
// SEQUENCE: uart_traffic_seq
//-------------------------------------------------
class uart_traffic_seq extends uart_base_seq;

   rand int unsigned num_of_tx;
   // register sequence with a sequencer 
   `uvm_object_utils(uart_traffic_seq)
   `uvm_declare_p_sequencer(uart_sequencer)
   
   function new(string name="uart_traffic_seq");
      super.new(name);
   endfunction

   constraint num_of_tx_ct { num_of_tx inside {[5:10]};  }   // REDUCE NUMBER FOR THE LAB

   virtual task body();
     `uvm_info(get_type_name(), $psprintf("UART sequencer: Executing %0d Frames", num_of_tx), UVM_LOW)
     for (int i = 0; i < num_of_tx; i++) begin
        `uvm_do(req)
     end
   endtask: body
endclass: uart_traffic_seq
