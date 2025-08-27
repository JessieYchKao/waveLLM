/*-------------------------------------------------------------------------
File name   : uart_ctrl_tb.sv
Title       : Simulation and Verification Environment
Project     :
Created     :
Description : This file implements the SVE for the APB-UART Environment
Notes       : The uart_ctrl_tb creates the UART env, the 
            : APB env and the scoreboard. It also randomizes the UART 
            : CSR settings and passes it to both the env's.
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/


`include "uart_ctrl_virtual_sequencer.sv"
`include "uart_ctrl_virtual_seq_lib.sv"


//--------------------------------------------------------------
//  Simulation Verification Environment (SVE)
//--------------------------------------------------------------
class uart_ctrl_tb extends uvm_env;

  apb_uart_virtual_sequencer virtual_sequencer;  // multi-channel sequencer
  apb_env apb0;                    // APB UVC
  uart_env uart0;              // UART UVC
  uart_ctrl_env apb_uart0;

  apb_config cfg;

  // enable automation for  uart_ctrl_tb
  `uvm_component_utils(uart_ctrl_tb)
    
  uvm_table_printer printer = new();

  function new(input string name, input uvm_component parent=null);
    super.new(name,parent);
  endfunction

  //lab4_note6
  function void start_of_simulation_phase(uvm_phase phase);
    uvm_test_done.set_drain_time(this, 1000);
    uvm_test_done.set_report_verbosity_level(UVM_HIGH);
  endfunction : start_of_simulation_phase

  virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);

    // Configure UVCs
    cfg = new();
    cfg.add_master("master", UVM_ACTIVE);
//    set_config_object("apb0", "cfg", cfg);
    uvm_config_db#(apb_config)::set(apb0, "apb0", "cfg", cfg);
    set_config_int("*uart0.Tx","is_active", UVM_ACTIVE);  
    set_config_int("*uart0.Rx","is_active", UVM_PASSIVE);

//    set_config_int("*uart0.Tx.sequencer", "count", 0);
//    set_config_int("apb0.master.sequencer", "count", 0);


    virtual_sequencer = apb_uart_virtual_sequencer::type_id::create("virtual_sequencer",this);
    apb0              = apb_env::type_id::create("apb0",this);
    uart0            = uart_env::type_id::create("uart0",this);
    apb_uart0        = uart_ctrl_env::type_id::create("apb_uart0",this);

  endfunction : build_phase

  function void connect_phase(uvm_phase phase);
    super.connect_phase(phase);

    // ***********************************************************
    //  Hookup virtual sequencer to interface sequencers
    // ***********************************************************
    virtual_sequencer.apb_seqr =  apb0.master.sequencer;

   if (uart0.Tx.is_active == UVM_ACTIVE)  
     virtual_sequencer.uart_seqr =  uart0.Tx.sequencer;


    // ***********************************************************
    // Set the virtual interfaces
    // ***********************************************************
//    apb0.assign_vi(uart_tb_top.apbi0);
//    uart0.assign_vi(uart_tb_top.uif0);
//    apb_uart0.assign_vi(uart_tb_top.uart_int0);

    // ***********************************************************
    // Connect TLM ports
    // ***********************************************************
    uart0.Rx.monitor.frame_collected_port.connect(apb_uart0.scbd.uart_in);
    uart0.Tx.monitor.frame_collected_port.connect(apb_uart0.scbd.uart_in_tx_mon);
    apb0.bus_monitor.item_collected_port.connect(apb_uart0.scbd.apb_in);

    // ***********************************************************
    // Connect the dut_csr ports
    // ***********************************************************
    virtual_sequencer.dut_cfg_port_o.connect(uart0.dut_cfg_port_in);
    virtual_sequencer.dut_cfg_port_o.connect(apb_uart0.dut_csr_port_in);
  endfunction : connect_phase

  task run_phase(uvm_phase phase);
    `uvm_info("LAB", $psprintf("APB_UVC<->UART_RTL<->UART_UVC Virtual Sequence Testbench Topology:"), UVM_LOW);
    printer.knobs.depth = 5;
    printer.knobs.name_width = 25;
    printer.knobs.type_width = 20;
    printer.knobs.value_width = 20;
    this.print(printer);

    #4500000;
    `uvm_info("LAB", $psprintf("User activated end of simulation"), UVM_LOW);
    global_stop_request();
  endtask

endclass
