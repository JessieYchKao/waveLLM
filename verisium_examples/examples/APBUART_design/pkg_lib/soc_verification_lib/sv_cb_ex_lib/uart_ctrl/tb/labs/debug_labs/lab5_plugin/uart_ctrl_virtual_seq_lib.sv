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
            : The intrpt_seq needs to be modified to take interrupt into account.
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/


`ifndef APB_UART_VIRTUAL_SEQ_LIB_SV
`define APB_UART_VIRTUAL_SEQ_LIB_SV

class base_vseq extends uvm_sequence;
  function new(string name="base_vseq");
    super.new(name);
  endfunction

  `uvm_object_utils(base_vseq)
 `uvm_declare_p_sequencer(apb_uart_virtual_sequencer)

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
//class concurrent_u2a_a2u_rand_trans_vseq extends uvm_sequence;
class concurrent_u2a_a2u_rand_trans_vseq extends base_vseq;

  rand int unsigned num_a2u_wr;
  rand int unsigned num_u2a_wr;
  rand uart_pkg::uart_config dut_csr;

  function new(string name="concurrent_u2a_a2u_rand_trans_vseq");
      super.new(name);
      if (!$cast(dut_csr, factory.create_object_by_name("uart_config", "", "dut_csr")))
        uvm_report_fatal ("CASTFL", "Failed to cast uart_config to dut_csr in new");
  endfunction : new

  // Register sequence with a sequencer 
// `uvm_sequence_utils(concurrent_u2a_a2u_rand_trans_vseq, apb_uart_virtual_sequencer)
 `uvm_object_utils(concurrent_u2a_a2u_rand_trans_vseq)    //lab4_note1

  constraint num_a2u_wr_ct {(num_a2u_wr <= 7);}
  constraint num_u2a_wr_ct {(num_u2a_wr <= 4);}

  // APB sequences
  program_dut_csr_seq config_dut;
  apb_to_uart_wr raw_seq;
  // UART sequences
  uart_transmit_seq uart_seq;
  intrpt_seq rd_rx_fifo;

  virtual task body();
    uvm_test_done.raise_objection(this);

    p_sequencer.dut_cfg_port_o.write(dut_csr);
    `uvm_info("LAB",  $psprintf("Printing dut_csr:\n%s", dut_csr.sprint()), UVM_LOW);

    `uvm_info("LAB",  $psprintf("Number of APB->UART Transaction = %d", num_a2u_wr), UVM_LOW);
    `uvm_info("LAB",  $psprintf("Number of UART->APB Transaction = %d", num_u2a_wr), UVM_LOW);
    `uvm_info("LAB",  $psprintf("Total Number of APB<->UART Transaction = %d", num_u2a_wr + num_a2u_wr), UVM_LOW);

    // configure UART DUT
    `uvm_do_on_with(config_dut, p_sequencer.apb_seqr, {csr_s == dut_csr.csr_s;} )

    // Write UART DUT TX FIFO from APB UVC and transmit data from UART UVC
    // Adding for loop to simulate a memory leakage
    `ifdef HEAP
    for (int i = 0; i < 200; i++)
    begin
    `endif
    fork
      `uvm_do_on_with(raw_seq, p_sequencer.apb_seqr, {num_of_wr == num_a2u_wr;})
      `uvm_do_on_with(uart_seq, p_sequencer.uart_seqr, {num_of_tx == num_u2a_wr;})
    join
    // Read UART DUT RX FIFO from APB UVC
    `uvm_do_on_with(rd_rx_fifo, p_sequencer.apb_seqr, {num_of_rd == num_u2a_wr;})
    `ifdef HEAP
    end
    `endif

    uvm_test_done.drop_objection(this);
  endtask : body

endclass : concurrent_u2a_a2u_rand_trans_vseq

//class u2a_incr_payload extends uvm_sequence;
class u2a_incr_payload extends base_vseq;

  //bit success;
  rand int unsigned num_u2a_wr;
  rand int unsigned num_a2u_wr;
  rand uart_config dut_csr; // donot use new() instead use create_object in body()

  function new(string name="u2a_incr_payload");
      super.new(name);
      if (!$cast(dut_csr, factory.create_object_by_name("uart_config", "", "dut_csr")))
        uvm_report_fatal ("CASTFL", "Failed to cast uart_config to dut_csr in new");
  endfunction : new

  // Register sequence with a sequencer 
// `uvm_sequence_utils(u2a_incr_payload, apb_uart_virtual_sequencer)    
 `uvm_object_utils(u2a_incr_payload)

  constraint num_u2a_wr_ct {(num_u2a_wr > 2) && (num_u2a_wr <= 7);}
  constraint num_a2u_wr_ct {(num_a2u_wr == 0);}

  // APB and UART UVC sequences
  program_dut_csr_seq config_dut;
  uart_incr_payload_seq uart_seq;
  intrpt_seq rd_rx_fifo;

  virtual task body();
    uvm_test_done.raise_objection(this);

    p_sequencer.dut_cfg_port_o.write(dut_csr);
    `uvm_info("LAB",  $psprintf("Printing dut_csr:\n%s", dut_csr.sprint()), UVM_LOW);

    `uvm_info("LAB",  $psprintf("Number of APB->UART Transaction = %d", num_a2u_wr), UVM_LOW);
    `uvm_info("LAB",  $psprintf("Number of UART->APB Transaction = %d", num_u2a_wr), UVM_LOW);
    `uvm_info("LAB",  $psprintf("Total Number of APB<->UART Transaction = %d", num_u2a_wr + num_a2u_wr), UVM_LOW);

    `uvm_do_on_with(config_dut, p_sequencer.apb_seqr, {csr_s == dut_csr.csr_s;})
    `uvm_do_on_with(uart_seq, p_sequencer.uart_seqr, {cnt == num_u2a_wr;})
    `uvm_do_on_with(rd_rx_fifo, p_sequencer.apb_seqr, {num_of_rd == num_u2a_wr;})

    uvm_test_done.drop_objection(this);
  endtask : body

endclass : u2a_incr_payload

//class u2a_bad_parity extends uvm_sequence;
class u2a_bad_parity extends base_vseq;

  //bit success;
  rand int unsigned num_u2a_wr;
  rand int unsigned num_a2u_wr;
  rand uart_config dut_csr; //new();

  function new(string name="u2a_bad_parity");
      super.new(name);
      if (!$cast(dut_csr, factory.create_object_by_name("uart_config", "", "dut_csr")))
        uvm_report_fatal ("CASTFL", "Failed to cast uart_config to dut_csr in new");
  endfunction : new

  // Register sequence with a sequencer 
// `uvm_sequence_utils(u2a_bad_parity, apb_uart_virtual_sequencer)    
 `uvm_object_utils(u2a_bad_parity)

  constraint num_u2a_wr_ct {(num_u2a_wr <= 7);}
  constraint num_a2u_wr_ct {(num_a2u_wr == 0);}

  // APB and UART UVC sequences
  program_dut_csr_seq config_dut;
  uart_bad_parity_seq uart_seq;
  intrpt_seq rd_rx_fifo;

  virtual task body();
    uvm_test_done.raise_objection(this);

    p_sequencer.dut_cfg_port_o.write(dut_csr);
    `uvm_info("LAB",  $psprintf("Printing dut_csr:\n%s", dut_csr.sprint()), UVM_LOW);

    `uvm_info("LAB",  $psprintf("Number of APB->UART Transaction = %d", num_a2u_wr), UVM_LOW);
    `uvm_info("LAB",  $psprintf("Number of UART->APB Transaction = %d", num_u2a_wr), UVM_LOW);
    `uvm_info("LAB",  $psprintf("Total Number of APB<->UART Transaction = %d", num_u2a_wr + num_a2u_wr), UVM_LOW);

    `uvm_do_on_with(config_dut, p_sequencer.apb_seqr, {csr_s == dut_csr.csr_s;})
    `uvm_do_on_with(uart_seq, p_sequencer.uart_seqr, {cnt == num_u2a_wr;})
    `uvm_do_on_with(rd_rx_fifo, p_sequencer.apb_seqr, {num_of_rd == num_u2a_wr;})

    uvm_test_done.drop_objection(this);
  endtask : body

endclass : u2a_bad_parity

//class uart_1_stopbit_rx_traffic extends uvm_sequence;
class uart_1_stopbit_rx_traffic extends base_vseq;

  class uart_1_stopbit extends uart_config;
    constraint c_num_stop_bits  { nbstop == 1'b0; }
    `uvm_object_utils(uart_1_stopbit)  
  endclass : uart_1_stopbit

  //bit success;
  rand int unsigned num_a2u_wr;
  rand int unsigned num_u2a_wr;
  rand uart_1_stopbit dut_csr; // = new();

  function new(string name="uart_1_stopbit_rx_traffic");
      super.new(name);
      if (!$cast(dut_csr, factory.create_object_by_name("uart_1_stopbit", "", "dut_csr")))
        uvm_report_fatal ("CASTFL", "Failed to cast uart_1_stopbit to dut_csr in new");
  endfunction : new

  // Register sequence with a sequencer 
//  `uvm_sequence_utils(uart_1_stopbit_rx_traffic, apb_uart_virtual_sequencer)    
  `uvm_object_utils(uart_1_stopbit_rx_traffic)

  constraint num_a2u_wr_ct {(num_a2u_wr <= 7);}
  constraint num_u2a_wr_ct {(num_u2a_wr == 0);}

  // APB  sequences
  program_dut_csr_seq config_dut;
  apb_to_uart_wr raw_seq;

  virtual task body();
    uvm_test_done.raise_objection(this);

    p_sequencer.dut_cfg_port_o.write(dut_csr);
    `uvm_info("LAB",  $psprintf("Printing dut_csr:\n%s", dut_csr.sprint()), UVM_LOW);

    `uvm_info("LAB",  $psprintf("Number of APB->UART Transaction = %d", num_a2u_wr), UVM_LOW);
    `uvm_info("LAB",  $psprintf("Number of UART->APB Transaction = %d", num_u2a_wr), UVM_LOW);
    `uvm_info("LAB",  $psprintf("Total Number of APB<->UART Transaction = %d", num_u2a_wr + num_a2u_wr), UVM_LOW);

    `uvm_do_on_with(config_dut, p_sequencer.apb_seqr, {csr_s == dut_csr.csr_s;})
    `uvm_do_on_with(raw_seq, p_sequencer.apb_seqr, {num_of_wr == num_a2u_wr;})

    uvm_test_done.drop_objection(this);
  endtask : body

endclass : uart_1_stopbit_rx_traffic

//class uart_rx_tx_fifo_coverage extends uvm_sequence;
class uart_rx_tx_fifo_coverage extends base_vseq;

  class uart_rx_tx_fifodepth_8 extends uart_config;
    `uvm_object_utils(uart_rx_tx_fifodepth_8)  
  endclass : uart_rx_tx_fifodepth_8

  rand int unsigned num_a2u_wr;
  rand int unsigned num_u2a_wr;
  rand uart_rx_tx_fifodepth_8 dut_csr; //new();

  function new(string name="uart_rx_tx_fifo_coverage");
      super.new(name);
      if (!$cast(dut_csr, factory.create_object_by_name("uart_rx_tx_fifodepth_8", "", "dut_csr")))
        uvm_report_fatal ("CASTFL", "Failed to cast uart_rx_tx_fifodepth_8 to dut_csr in new");
  endfunction : new

  // Register sequence with a sequencer 
//  `uvm_sequence_utils(uart_rx_tx_fifo_coverage, apb_uart_virtual_sequencer)    
  `uvm_object_utils(uart_rx_tx_fifo_coverage)

  constraint num_a2u_wr_ct {(num_a2u_wr ==`UA_TX_FIFO_DEPTH + 1 );}
  constraint num_u2a_wr_ct {(num_u2a_wr == `UA_TX_FIFO_DEPTH + 1 );}

  // APB and UART UVC sequences
  program_dut_csr_seq config_dut;
  apb_to_uart_wr raw_seq;
  uart_transmit_seq uart_seq;
  intrpt_seq rd_rx_fifo;

  virtual task body();
    uvm_test_done.raise_objection(this);

    p_sequencer.dut_cfg_port_o.write(dut_csr);
    `uvm_info("LAB",  $psprintf("Printing dut_csr:\n%s", dut_csr.sprint()), UVM_LOW);

    `uvm_info("LAB",  $psprintf("Number of APB->UART Transaction = %d", num_a2u_wr), UVM_LOW);
    `uvm_info("LAB",  $psprintf("Number of UART->APB Transaction = %d", num_u2a_wr), UVM_LOW);
    `uvm_info("LAB",  $psprintf("Total Number of APB<->UART Transaction = %d", num_u2a_wr + num_a2u_wr), UVM_LOW);

    `uvm_do_on_with(config_dut, p_sequencer.apb_seqr, {csr_s == dut_csr.csr_s;})
    fork
      `uvm_do_on_with(raw_seq, p_sequencer.apb_seqr, {num_of_wr == num_a2u_wr;})
      `uvm_do_on_with(uart_seq, p_sequencer.uart_seqr, {num_of_tx == num_u2a_wr;})
    join
    `uvm_do_on_with(rd_rx_fifo, p_sequencer.apb_seqr, {num_of_rd == num_u2a_wr;})

    uvm_test_done.drop_objection(this);
  endtask : body

endclass : uart_rx_tx_fifo_coverage

`endif
