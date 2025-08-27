//-------------------------------------------------------------------------
// File name   : run1.f
// Title       :
// Project     : SystemVerilog UVM Lab
// Created     :
// Description :
// Notes       :
//----------------------------------------------------------------------
// Copyright  200*-2011 Cadence Design Systems, Inc. All rights reserved worldwide.
// Please refer to the terms and conditions in the Kit documentation.
//----------------------------------------------------------------------

-uvmhome ${UVM_HOME}
-access RWC

-incdir ${SOCV_KIT_HOME}/soc_verification_lib/sv_cb_ex_lib/interface_uvc_lib/apb/sv
-incdir ./uart_uvc
-incdir ./uart_ctrl_env
-incdir ./tests
-svseed random
+define+LITLE_ENDIAN \

${SOCV_KIT_HOME}/soc_verification_lib/sv_cb_ex_lib/interface_uvc_lib/apb/sv/apb_pkg.sv
${SOCV_KIT_HOME}/soc_verification_lib/sv_cb_ex_lib/interface_uvc_lib/uart/sv/uart_pkg.sv
${SOCV_KIT_HOME}/designs/socv/rtl/rtl_lpw/opencores/uart16550/rtl/uart_defines.v 
-F ${SOCV_KIT_HOME}/designs/socv/rtl/rtl_lpw/opencores/oc_uart.irunargs 
${SOCV_KIT_HOME}/soc_verification_lib/sv_cb_ex_lib/uart_ctrl/sv/uart_ctrl_defines.svh 
./uart_ctrl_env/uart_ctrl_pkg.sv

//+tcl+run.tcl

./uart_ctrl_top.sv

// Messaging Options:
+UVM_VERBOSITY=MEDIUM

// Test Options:
+UVM_TESTNAME=u2a_a2u_full_rand_test
//+UVM_TESTNAME=uart_incr_payload_test
