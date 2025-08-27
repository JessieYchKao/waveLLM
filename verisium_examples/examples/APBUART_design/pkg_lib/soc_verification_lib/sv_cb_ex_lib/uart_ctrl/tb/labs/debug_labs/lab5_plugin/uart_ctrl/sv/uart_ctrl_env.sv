/*-------------------------------------------------------------------------
File name   : uart_ctrl_env.sv
Title       : 
Project     :
Created     :
Description : Module env, contains the instance of scoreboard and coverage model
Notes       : 
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/


class uart_ctrl_env extends uvm_env;
  
  uart_ctrl_scoreboard scbd ;
  uart_ctrl_cover uart_cover;

  uvm_analysis_imp#(uart_pkg::uart_config, uart_ctrl_env) dut_csr_port_in;

  `uvm_component_utils(uart_ctrl_env)

  // new constructor defined
  function new(input string name, input uvm_component parent=null);
    super.new(name,parent);
    dut_csr_port_in = new("dut_csr_port_in", this);
  endfunction

  virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    // build scoreboard
    scbd = uart_ctrl_scoreboard::type_id::create("scbd",this);
    // build coverage
    uart_cover = uart_ctrl_cover::type_id::create("uart_cover",this);
  endfunction : build_phase
  
  // passing csr_setting to scoreboard and coverage
  function void write(uart_pkg::uart_config csr_setting);
    scbd.assign_csr(csr_setting);
    uart_cover.uart_cfg = csr_setting;
  endfunction

  // assign the virtual interface of module UVC //could have multiple assign_vi's for different interfaces
//  function void assign_vi(virtual interface uart_ctrl_internal_if fifo_if);
//      uart_cover.uart_int0 = fifo_if;
//  endfunction

endclass : uart_ctrl_env

