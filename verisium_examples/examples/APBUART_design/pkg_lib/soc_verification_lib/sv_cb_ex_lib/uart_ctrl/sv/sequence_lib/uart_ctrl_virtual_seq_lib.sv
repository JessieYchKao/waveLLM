/*-------------------------------------------------------------------------
File name   : uart_ctrl_virtual_seq_lib.sv
Title       : Virtual Sequence
Project     :
Created     :
Description : This file implements the virtual sequence for the APB-UART env.
Notes       : The concurrent_u2a_a2u_rand_trans_vseq sequence first configures
            : the UART RTL. Once the configuration sequence is completed
            : random read/write sequences from both the UVCs are enabled
            : in parallel. At the end a Rx FIFO read sequence is executed.
            : The read_rx_fifo_seq needs to be modified to take interrupt into account.
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/


`ifndef UART_CTRL_VIRTUAL_SEQ_LIB_SV
`define UART_CTRL_VIRTUAL_SEQ_LIB_SV

class base_vseq extends uvm_sequence;
  function new(string name="base_vseq");
    super.new(name);
  endfunction

  `uvm_object_utils(base_vseq)
 `uvm_declare_p_sequencer(uart_ctrl_virtual_sequencer)

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
endclass : base_vseq

// sequence having UART UVC transmitting data and receiving data
class concurrent_u2a_a2u_rand_trans_vseq extends base_vseq;

  rand int unsigned num_a2u_wr;
  rand int unsigned num_u2a_wr;

  function new(string name="concurrent_u2a_a2u_rand_trans_vseq");
      super.new(name);
  endfunction : new

  // Register sequence with a sequencer 
 `uvm_object_utils(concurrent_u2a_a2u_rand_trans_vseq)

  constraint num_a2u_wr_ct {num_a2u_wr inside {[10:15]};}
  constraint num_u2a_wr_ct {num_u2a_wr inside {[10:15]};}

  //UART Controller Configuration Sequence
  uart_ctrl_config_reg_seq  config_seq;

  // Configure the latch  
  uart_ctrl_config_latch_reg_seq config_latch;

  // APB sequences
  apb_to_uart_wr raw_seq;

  // UART sequences
  uart_transmit_seq uart_seq;
  read_rx_fifo_seq rd_rx_fifo;

  virtual task body();                      //lab4_note2
    `uvm_info(get_type_name(), "UART Controller Virtual Sequencer Executing", UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Number of APB->UART Transaction = %0d", num_a2u_wr), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Number of UART->APB Transaction = %0d", num_u2a_wr), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Total Number of APB<->UART Transaction = %0d", num_u2a_wr + num_a2u_wr), UVM_LOW)

    // configure UART DUT
    `uvm_do_on(config_seq, p_sequencer.reg_seqr)  // register sequencer

    fork
      // Write UART DUT TX FIFO from APB UVC and transmit data from UART UVC
      `uvm_do_on_with(raw_seq, p_sequencer.apb_seqr, {num_of_wr == num_a2u_wr;})
      `uvm_do_on_with(uart_seq, p_sequencer.uart_seqr, {num_of_tx == num_u2a_wr;})
    join

    // Write a new latch value 
    `uvm_do_on(config_latch, p_sequencer.reg_seqr)  // register sequencer

    #10000;

    // Read UART DUT RX FIFO from APB UVC
    `uvm_do_on_with(rd_rx_fifo, p_sequencer.apb_seqr, {num_of_rd == num_u2a_wr;})

  endtask : body

endclass : concurrent_u2a_a2u_rand_trans_vseq

class u2a_incr_payload_vseq extends base_vseq;

  rand int unsigned num_u2a_wr;
  rand int unsigned num_a2u_wr;

  function new(string name="u2a_incr_payload_vseq");
      super.new(name);
  endfunction : new

  // Register sequence with a sequencer 
 `uvm_object_utils(u2a_incr_payload_vseq)

  constraint num_u2a_wr_ct {(num_u2a_wr > 2) && (num_u2a_wr <= 10);}
  constraint num_a2u_wr_ct {(num_a2u_wr == 0);}

  // APB and UART UVC sequences
  uart_incr_payload_seq uart_seq;
  read_rx_fifo_seq rd_rx_fifo;

  //UART Controller Configuration Sequence
  uart_ctrl_config_reg_seq  config_seq;

  virtual task body();
    `uvm_info(get_type_name(), "UART Controller Virtual Sequencer Executing", UVM_LOW)

    `uvm_info(get_type_name(), $psprintf("Number of APB->UART Transaction = %0d", num_a2u_wr), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Number of UART->APB Transaction = %0d", num_u2a_wr), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Total Number of APB<->UART Transaction = %0d", num_u2a_wr + num_a2u_wr), UVM_LOW)

    // Create the UART config sequence, set the register model and start
    `uvm_do_on(config_seq, p_sequencer.reg_seqr)  // register sequencer

    `uvm_do_on_with(uart_seq, p_sequencer.uart_seqr, {cnt == num_u2a_wr;})
    `uvm_do_on_with(rd_rx_fifo, p_sequencer.apb_seqr, {num_of_rd == num_u2a_wr;})

  endtask : body

endclass : u2a_incr_payload_vseq


// Send a nested sequence of writes into the DUT
class send_lots_of_sequences extends base_vseq;

  rand int unsigned num_items;

  function new(string name="send_lots_of_sequences");
      super.new(name);
  endfunction : new

  // Register sequence with a sequencer
 `uvm_object_utils(send_lots_of_sequences)

  constraint num_items_c {num_items inside {[10:15]};}

  //UART Controller Configuration Sequence
  uart_ctrl_config_reg_seq  config_seq;

  // APB and UART UVC sequences

  // Sequence to add items to the fifo, injecting an X at a random
  // location
  uart_send_frames_then_seq uart_write_seq;

  // Sequence to read items from the fifo
  read_rx_fifo_seq apb_read_seq;

  virtual task body();
    `uvm_info(get_type_name(), "UART Controller Virtual Sequencer Executing send_lots_of_sequences sequence", UVM_LOW)

    `uvm_info(get_type_name(), $psprintf("Number of APB->UART items = %d", num_items), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Number of UART->APB items = %d", num_items), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Total Number of APB<->UART sequences = %d", num_items*2), UVM_LOW)

    // Create the UART config sequence, set the register model and start
    `uvm_do_on(config_seq, p_sequencer.reg_seqr)  // register sequencer

    `uvm_do_on_with(uart_write_seq, p_sequencer.uart_seqr, {num_of_items == num_items;})
    `uvm_do_on_with(apb_read_seq,   p_sequencer.apb_seqr, {num_of_rd == num_items;})

  endtask : body

endclass :send_lots_of_sequences

class send_u2a_data extends base_vseq;
 
  rand int unsigned num_trans;
 
  function new(string name="send_u2a_data");
      super.new(name);
  endfunction : new
 
  // Register sequence with a sequencer 
 `uvm_object_utils(send_u2a_data)
 
  constraint num_trans_c {num_trans inside {[12:15]};}
 
  //UART Controller Configuration Sequence
  uart_ctrl_config_reg_seq  config_seq;
 
  // Sequence to add items to the fifo, injecting an X at a random 
  // location 
  rx_fifo_injectX uart_seq;
  
  // Sequence to read items from the fifo 
  read_rx_fifo_then_error_reg_seq rd_rx_fifo;
 
  virtual task body();
    `uvm_info(get_type_name(), "UART Controller Virtual Sequencer Executing send_u2a_data sequence", UVM_LOW)
 
    `uvm_info(get_type_name(), $psprintf("Number of APB->UART Transaction = %d", num_trans), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Number of UART->APB Transaction = %d", num_trans), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Total Number of APB<->UART Transaction = %d", num_trans*2), UVM_LOW)
 
    // Create the UART config sequence, set the register model and start
    `uvm_do_on(config_seq, p_sequencer.reg_seqr)  // register sequencer
 
    `uvm_do_on_with(uart_seq, p_sequencer.uart_seqr, {cnt == num_trans;})
    `uvm_do_on_with(rd_rx_fifo, p_sequencer.apb_seqr, {num_of_rd == num_trans;})
 
  endtask : body
 
endclass :send_u2a_data 

class u2a_traffic_seq extends base_vseq;

  rand int unsigned num_u2a_wr;
  rand int unsigned num_a2u_wr;

  function new(string name="u2a_traffic_seq");
      super.new(name);
  endfunction : new

  // Register sequence with a sequencer
 `uvm_object_utils(u2a_traffic_seq)

  constraint num_u2a_wr_ct {num_u2a_wr inside {[5:10]};}
  constraint num_a2u_wr_ct {num_a2u_wr inside {[5:10]};}

  //UART Controller Configuration Sequence
  uart_ctrl_config_reg_seq  config_seq;

  //Read from the Modem Control register
  read_modem_control_seq read_modem_seq;

  // APB and UART UVC sequences
  uart_transmit_seq uart_seq;
  read_rx_fifo_seq rd_rx_fifo;

  virtual task body();
    `uvm_info(get_type_name(), "UART Controller Virtual Sequencer Executing", UVM_LOW)

    `uvm_info(get_type_name(), $psprintf("Number of APB->UART Transaction = %d", num_a2u_wr), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Number of UART->APB Transaction = %d", num_u2a_wr), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Total Number of APB<->UART Transaction = %d", num_u2a_wr + num_a2u_wr), UVM_LOW)

    // Create the UART config sequence, set the register model and start
    `uvm_do_on(config_seq, p_sequencer.reg_seqr)  // register sequencer
    
    // Read the modem control register
    `uvm_do_on(read_modem_seq, p_sequencer.apb_seqr)   

    `uvm_do_on_with(uart_seq, p_sequencer.uart_seqr, {num_of_tx == num_u2a_wr;})
    `uvm_do_on_with(rd_rx_fifo, p_sequencer.apb_seqr, {num_of_rd == num_u2a_wr;})

  endtask : body

endclass : u2a_bad_parity_vseq


class u2a_bad_parity_vseq extends base_vseq;

  rand int unsigned num_u2a_wr;
  rand int unsigned num_a2u_wr;

  function new(string name="u2a_bad_parity_vseq");
      super.new(name);
  endfunction : new

  // Register sequence with a sequencer 
 `uvm_object_utils(u2a_bad_parity_vseq)

  constraint num_u2a_wr_ct {num_u2a_wr inside {[5:10]};}
  constraint num_a2u_wr_ct {num_a2u_wr inside {[5:10]};}

  //UART Controller Configuration Sequence
  uart_ctrl_config_reg_seq  config_seq;

  // APB and UART UVC sequences
  uart_bad_parity_seq uart_seq;
  read_rx_fifo_then_error_reg_seq rd_rx_fifo;

  virtual task body();
    //cgoss
    for (int i = 0; i<50; i++) begin 
    `uvm_info(get_type_name(), "UART Controller Virtual Sequencer Executing", UVM_LOW)

    `uvm_info(get_type_name(), $psprintf("Number of APB->UART Transaction = %d", num_a2u_wr), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Number of UART->APB Transaction = %d", num_u2a_wr), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Total Number of APB<->UART Transaction = %d", num_u2a_wr + num_a2u_wr), UVM_LOW)

    // Create the UART config sequence, set the register model and start
    `uvm_do_on(config_seq, p_sequencer.reg_seqr)  // register sequencer

    `uvm_do_on_with(uart_seq, p_sequencer.uart_seqr, {cnt == num_u2a_wr;})
    `uvm_do_on_with(rd_rx_fifo, p_sequencer.apb_seqr, {num_of_rd == num_u2a_wr;})
   //cgoss
   end //for 

  endtask : body

endclass : u2a_bad_parity_vseq

class error_reg_vseq extends base_vseq;

  rand int unsigned num_u2a_wr;
  rand int unsigned num_a2u_wr;

  function new(string name="error_reg_vseq");
      super.new(name);
  endfunction : new

  // Register sequence with a sequencer 
 `uvm_object_utils(error_reg_vseq)

  constraint num_u2a_wr_ct {(num_u2a_wr <= 10);}
  constraint num_a2u_wr_ct {(num_a2u_wr == 0);}

  //UART Controller Configuration Sequence
  uart_ctrl_config_reg_seq  config_seq;

  // APB and UART UVC sequences
  uart_bad_parity_seq uart_seq;
  read_rx_fifo_then_error_reg_seq rd_rx_fifo;  

  virtual task body();
    `uvm_info(get_type_name(), "UART Controller Virtual Sequencer Executing", UVM_LOW)

    `uvm_info(get_type_name(), $psprintf("Number of APB->UART Transaction = %d", num_a2u_wr), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Number of UART->APB Transaction = %d", num_u2a_wr), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Total Number of APB<->UART Transaction = %d", num_u2a_wr + num_a2u_wr), UVM_LOW)

    // Create the UART config sequence, set the register model and start
    `uvm_do_on(config_seq, p_sequencer.reg_seqr)  // register sequencer

    `uvm_do_on_with(uart_seq, p_sequencer.uart_seqr, {cnt == num_u2a_wr;})
    `uvm_do_on_with(rd_rx_fifo, p_sequencer.apb_seqr, {num_of_rd == num_u2a_wr;})

  endtask : body

endclass : error_reg_vseq  

class uart_1_stopbit_rx_traffic_vseq extends base_vseq;

  rand int unsigned num_a2u_wr;
  rand int unsigned num_u2a_wr;

  function new(string name="uart_1_stopbit_rx_traffic_vseq");
      super.new(name);
  endfunction : new

  // Register sequence with a sequencer 
  `uvm_object_utils(uart_1_stopbit_rx_traffic_vseq)

  constraint num_a2u_wr_ct {(num_a2u_wr == 1);}
  constraint num_u2a_wr_ct {(num_u2a_wr == 0);}

  //UART Controller Configuration Sequence
  uart_ctrl_1stopbit_reg_seq  config_seq;

  // APB  sequences
  apb_to_uart_wr raw_seq;

  virtual task body();
    `uvm_info(get_type_name(), "UART Controller Virtual Sequencer Executing", UVM_LOW)

    `uvm_info(get_type_name(), $psprintf("Number of APB->UART Transaction = %0d", num_a2u_wr), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Number of UART->APB Transaction = %0d", num_u2a_wr), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Total Number of APB<->UART Transaction = %0d", num_u2a_wr + num_a2u_wr), UVM_LOW)

    // Create the UART config sequence, set the register model and start
    `uvm_do_on(config_seq, p_sequencer.reg_seqr)  // register sequencer

    `uvm_do_on_with(raw_seq, p_sequencer.apb_seqr, {num_of_wr == num_a2u_wr;})

    #800000;

  endtask : body

endclass : uart_1_stopbit_rx_traffic_vseq

// sequence having UART UVC transmitting data and receiving data
class uart_rx_tx_fifo_coverage_vseq extends base_vseq;

  rand int unsigned num_a2u_wr;
  rand int unsigned num_u2a_wr;

  function new(string name="uart_rx_tx_fifo_coverage_vseq");
      super.new(name);
  endfunction : new

  // Register sequence with a sequencer 
 `uvm_object_utils(uart_rx_tx_fifo_coverage_vseq)

  constraint num_a2u_wr_ct {(num_a2u_wr == 17);}
  constraint num_u2a_wr_ct {(num_u2a_wr == 16);}

  //UART Controller Configuration Sequence
  uart_ctrl_config_reg_seq  config_seq;

  // APB sequences
  apb_to_uart_wr raw_seq;

  // UART sequences
  uart_transmit_seq uart_seq;
  read_rx_fifo_seq rd_rx_fifo;

  virtual task body();                      //lab4_note2
    `uvm_info(get_type_name(), "UART Controller Virtual Sequencer Executing", UVM_LOW)

    `uvm_info(get_type_name(), $psprintf("Number of APB->UART Transaction = %0d", num_a2u_wr), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Number of UART->APB Transaction = %0d", num_u2a_wr), UVM_LOW)
    `uvm_info(get_type_name(), $psprintf("Total Number of APB<->UART Transaction = %0d", num_u2a_wr + num_a2u_wr), UVM_LOW)

    // Create the UART config sequence, set the register model and start
    `uvm_do_on(config_seq, p_sequencer.reg_seqr)  // register sequencer

    fork
      // Write UART DUT TX FIFO from APB UVC and transmit data from UART UVC
      `uvm_do_on_with(raw_seq, p_sequencer.apb_seqr, {num_of_wr == num_a2u_wr;})
      `uvm_do_on_with(uart_seq, p_sequencer.uart_seqr, {num_of_tx == num_u2a_wr;})
    join
    #10000;
    // Read UART DUT RX FIFO from APB UVC
    `uvm_do_on_with(rd_rx_fifo, p_sequencer.apb_seqr, {num_of_rd == num_u2a_wr;})

  endtask : body

endclass : uart_rx_tx_fifo_coverage_vseq

`endif  // UART_CTRL_VIRTUAL_SEQ_LIB_SV
