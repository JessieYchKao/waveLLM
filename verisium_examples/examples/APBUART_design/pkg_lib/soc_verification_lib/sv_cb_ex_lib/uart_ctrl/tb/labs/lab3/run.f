//-------------------------------------------------------------------------
// File name   : run.f
// Title       :
// Project     : SystemVerilog UVM Lab
// Created     :
// Description :
// Notes       :  
//----------------------------------------------------------------------
// Copyright  200*-2011 Cadence Design Systems, Inc. All rights reserved worldwide.
// Please refer to the terms and conditions in the Kit documentation.
//-------------------------------------------------------------------------

-uvmhome ${UVM_HOME}

-access RWC
-linedebug

// UART UVC Files
${SOCV_KIT_HOME}/soc_verification_lib/sv_cb_ex_lib/interface_uvc_lib/uart/sv/uart_pkg.sv
-incdir ./uart_uvc   

-input run_batch.tcl

// Top-Level Testbench
./uart_top.sv

+svseed=random

// Messaging Options:
//+UVM_VERBOSITY=UVM_MEDIUM
//+UVM_VERBOSITY=UVM_HIGH
