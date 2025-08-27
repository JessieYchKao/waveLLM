/*-------------------------------------------------------------------------
File name   : uart_ctrl_pkg.svh
Title       : Module UVC Files
Project     : UART Block Level
Created     :
Description : 
Notes       : 
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/

`ifndef UART_CRTL_PKG_SV
`define UART_CRTL_PKG_SV

package uart_ctrl_pkg;

import uvm_pkg::*;
`include "uvm_macros.svh"

import apb_pkg::*;
import uart_pkg::*;

`include "uart_ctrl_scoreboard.sv"
`include "coverage/uart_ctrl_cover.sv"
`include "uart_ctrl_seq_lib.sv"
`include "uart_ctrl_env.sv"

endpackage : uart_ctrl_pkg

`endif //UART_CTRL_PKG_SV
