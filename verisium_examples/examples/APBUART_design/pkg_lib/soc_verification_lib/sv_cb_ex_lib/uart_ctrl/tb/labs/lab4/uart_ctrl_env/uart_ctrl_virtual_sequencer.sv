/*-------------------------------------------------------------------------
File name   : uart_ctrl_virtual_sequencer.sv
Title       : Virtual sequencer
Project     :
Created     :
Description : This virtual sequencer for UART Controller environment
Notes       : 
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/

class uart_ctrl_virtual_sequencer extends uvm_sequencer;

    uvm_analysis_port #(uart_config) dut_cfg_port_o;

    apb_master_sequencer apb_seqr;
    uart_sequencer uart_seqr;

   
    function new (input string name="uart_ctrl_virtual_sequencer", input uvm_component parent=null);
      super.new(name, parent);
      dut_cfg_port_o = new ("dut_cfg_port_o", this);
    endfunction : new

    `uvm_component_utils(uart_ctrl_virtual_sequencer)

endclass : uart_ctrl_virtual_sequencer

