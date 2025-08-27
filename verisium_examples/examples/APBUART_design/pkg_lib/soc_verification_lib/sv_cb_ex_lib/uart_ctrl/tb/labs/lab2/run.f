//-------------------------------------------------------------------------
// File name   : run.f
// Title       : 
// Project     : SystemVerilog UVM Lab
// Created     :
// Description :
// Notes       :  
//----------------------------------------------------------------------
// Copyright  200*-2008 Cadence Design Systems, Inc. All rights reserved worldwide.
// Please refer to the terms and conditions in the Kit documentation.
//-------------------------------------------------------------------------

-uvmhome ${UVM_HOME}

-access rwc
-linedebug
-timescale 1ns/1ns

lab2_top.sv

//+UVM_VERBOSITY=UVM_FULL
//+UVM_VERBOSITY=UVM_HIGH
+UVM_VERBOSITY=UVM_MEDIUM
//+UVM_VERBOSITY=UVM_LOW
//+UVM_VERBOSITY=UVM_NONE
