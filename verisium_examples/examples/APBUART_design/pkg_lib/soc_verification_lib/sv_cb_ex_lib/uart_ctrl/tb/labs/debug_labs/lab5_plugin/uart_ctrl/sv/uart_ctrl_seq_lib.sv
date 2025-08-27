/*-------------------------------------------------------------------------
File name   : uart_ctrl_seq_lib.sv
Title       : 
Project     :
Created     :
Description : This file implements APB Sequences specific to UART 
            : CSR programming and Tx/Rx FIFO write/read
Notes       : The interrupt sequence in this file is not yet complete.
            : The interrupt sequence should be triggred by the Rx fifo 
            : full event from the UART RTL.
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

class apb_base_seq extends uvm_sequence #(apb_pkg::apb_transfer);

  function new(string name="apb_base_seq");
    super.new(name);
  endfunction

  `uvm_object_utils(apb_base_seq)
  `uvm_declare_p_sequencer(apb_pkg::apb_master_sequencer)

// Use a base sequence to raise/drop objections if this is a default sequence
  virtual task pre_body(); 
     if (starting_phase != null)
        starting_phase.raise_objection(this, {"Running sequence '",
                                              get_full_name(), "'"});
  endtask
  
  virtual task post_body();
     if (starting_phase != null)
        starting_phase.drop_objection(this, {"Completed sequence '",
                                             get_full_name(), "'"});
  endtask
endclass : apb_base_seq

//class apb_to_uart_rd_after_wr extends uvm_sequence #(apb_pkg::apb_transfer);
class apb_to_uart_rd_after_wr extends apb_base_seq;

    function new(string name="apb_to_uart_rd_after_wr");
      super.new(name);
    endfunction

    // Register sequence with a sequencer 
//    `uvm_sequence_utils(apb_to_uart_rd_after_wr, apb_pkg::apb_master_sequencer)    
    `uvm_object_utils(apb_to_uart_rd_after_wr)


    rand bit [31:0] start_addr;
    rand int unsigned del = 0;
    constraint del_ct { (del <= 10); }
    constraint addr_ct {(start_addr[1:0] == 0); }

    virtual task body();
      response_queue_error_report_disabled = 1;
      start_addr = `TX_FIFO_REG;
        `uvm_do_with(req, 
          { req.addr == start_addr;
            req.direction == APB_WRITE;
            req.delay == del; } )

      start_addr = `TX_FIFO_REG;
        `uvm_do_with(req, 
          { req.addr == start_addr;
            req.direction == APB_READ;
            req.delay == del; } )
    endtask
  
endclass : apb_to_uart_rd_after_wr

// writes 0-150 data in UART TX FIFO
//class apb_to_uart_wr extends uvm_sequence #(apb_pkg::apb_transfer);
class apb_to_uart_wr extends apb_base_seq;

    function new(string name="apb_to_uart_wr");
      super.new(name);
    endfunction

    // Register sequence with a sequencer 
//    `uvm_sequence_utils(apb_to_uart_wr, apb_pkg::apb_master_sequencer)    
    `uvm_object_utils(apb_to_uart_wr)

    // Memory leakage example
    static apb_pkg::apb_transfer transfer_heap[$];

    rand bit [31:0] start_addr;
    rand int unsigned del = 0;
    rand int unsigned num_of_wr;
    constraint num_of_wr_ct { (num_of_wr <= 150); }
    constraint del_ct { (del <= 10); }
    constraint addr_ct {(start_addr[1:0] == 0); }

    virtual task body();
      response_queue_error_report_disabled = 1;
      start_addr = `TX_FIFO_REG;
        for (int i = 0; i < num_of_wr; i++) begin
          `uvm_do_with(req, 
            { req.addr == start_addr;
              req.direction == APB_WRITE;
              req.delay == del; } )
	    transfer_heap.push_back(req);
        end
    endtask
  
endclass : apb_to_uart_wr


// configures UART DUT Registers 
//class program_dut_csr_seq extends uvm_sequence #(apb_pkg::apb_transfer);
class program_dut_csr_seq extends apb_base_seq;

    function new(string name="program_dut_csr_seq");
      super.new(name);
    endfunction
  
    rand uart_pkg::uart_cfg_s csr_s;

    // Register sequence with a sequencer 
//    `uvm_sequence_utils(program_dut_csr_seq, apb_pkg::apb_master_sequencer)    
    `uvm_object_utils(program_dut_csr_seq)

    //apb_transfer this_transfer;

    bit success;
    bit [31:0] start_addr;
    bit [31:0] write_data;
    rand int unsigned del = 0;
    constraint del_ct { (del <= 10); }
    constraint addr_ct {(start_addr == 0); }

    virtual task body();

      start_addr = `LINE_CTRL;
      write_data = {24'h0, 1'b1, 1'b0, csr_s.parity_mode, csr_s.parity_en, csr_s.nbstop, csr_s.char_length};
        `uvm_do_with(req, 
          { req.addr == start_addr;
            req.direction == APB_WRITE;
            req.data == write_data;
            req.delay == del; } )

      start_addr = `DIVD_LATCH2;
      write_data = {24'h0, csr_s.baud_rate_div};
        `uvm_do_with(req, 
          { req.addr == start_addr;
            req.direction == APB_WRITE;
            req.data == write_data;
            req.delay == del; } )

      start_addr = `DIVD_LATCH1;
      write_data = {16'h0, csr_s.baud_rate_gen};
        `uvm_do_with(req, 
          { req.addr == start_addr;
            req.direction == APB_WRITE;
            req.data == write_data;
            req.delay == del; } )

      start_addr = `LINE_CTRL;
      write_data = {24'h0, 1'b0, 1'b0, csr_s.parity_mode, csr_s.parity_en, csr_s.nbstop, csr_s.char_length};
        `uvm_do_with(req, 
          { req.addr == start_addr;
            req.direction == APB_WRITE;
            req.data == write_data;
            req.delay == del; } )

    endtask
  
endclass : program_dut_csr_seq


// Reads UART RX FIFO
//class intrpt_seq extends uvm_sequence #(apb_pkg::apb_transfer);
class intrpt_seq extends apb_base_seq;

    function new(string name="intrpt_seq");
      super.new(name);
    endfunction

    // Register sequence with a sequencer 
//    `uvm_sequence_utils(intrpt_seq, apb_pkg::apb_master_sequencer)    
    `uvm_object_utils(intrpt_seq)

    rand bit [31:0] read_addr;
    rand int unsigned del = 0;
    rand int unsigned num_of_rd;
    constraint num_of_rd_ct { (num_of_rd <= 150); }
    constraint del_ct { (del <= 10); }
    constraint addr_ct {(read_addr[1:0] == 0); }

    virtual task body();
      response_queue_error_report_disabled = 1;

      `uvm_info("UART_APB_SEQLIB", $psprintf("Doing intrpt_seq sequence"), UVM_LOW);
      for (int i = 0; i < num_of_rd; i++) begin
        read_addr = `RX_FIFO_REG;      //rx fifo address
          `uvm_do_with(req, 
            { req.addr == read_addr;
              req.direction == APB_READ;
              req.delay == del; } )
      end
    endtask
  
endclass : intrpt_seq

