/*-------------------------------------------------------------------------
File name   : uart_ctrl_virtual_sequencer.sv
Title       : Virtual sequencer
Project     :
Created     :
Description : This file implements the Virtual sequencer for APB-UART environment
Notes       : 
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/

class apb_uart_virtual_sequencer extends uvm_sequencer;

    uvm_analysis_port #(uart_config) dut_cfg_port_o;

    apb_master_sequencer apb_seqr;
    uart_sequencer uart_seqr;

   
    function new (input string name="apb_uart_virtual_sequencer", input uvm_component parent=null);
      super.new(name, parent);
//      `uvm_update_sequence_lib
      dut_cfg_port_o = new ("dut_cfg_port_o", this);
    endfunction : new

//    `uvm_sequencer_utils(apb_uart_virtual_sequencer)
    `uvm_component_utils(apb_uart_virtual_sequencer)


endclass : apb_uart_virtual_sequencer

