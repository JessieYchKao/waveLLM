
#-------------------------------------------------------------------------
# File name   : Makefile
# Title       :
# Project     : UART Block Level Verification
# Created     :
# Description :
# Notes       :
#----------------------------------------------------------------------
# Copyright  200*-2008 Cadence Design Systems, Inc. All rights reserved worldwide.
# Please refer to the terms and conditions in the Kit documentation.
#----------------------------------------------------------------------


## Variables and scripts
NCROOT            = `ncroot`
TEST_NAME         = uart_ctrl_heap_test 
SVSEED            = 100
NCLIBDIRPATH      = .
TB_FILENAME       = ./uart_ctrl_top.sv
VERBOSITY         = MEDIUM
WORKSHOP_MODE     = NONE
UVM_HOME = `ncroot`/tools/uvm-1.1

OPTIONS    = -incdir ${SOCV_KIT_HOME}/soc_verification_lib/sv_cb_ex_lib/interface_uvc_lib/apb/sv \
             -incdir ${SOCV_KIT_HOME}/soc_verification_lib/sv_cb_ex_lib/interface_uvc_lib/uart/sv \
             -incdir . \
             -incdir ./uart_ctrl/sv  \
             -incdir ./uart_ctrl/tb/tests      \
             -incdir ${SOCV_KIT_HOME}/soc_verification_lib/sv_cb_ex_lib/uart_ctrl/tb/sv  \
             ${SOCV_KIT_HOME}/util_lib/config_pkg/sv/uvm_config_prop_pkg.sv \
             ${SOCV_KIT_HOME}/soc_verification_lib/sv_cb_ex_lib/interface_uvc_lib/apb/sv/apb_pkg.sv \
             ${SOCV_KIT_HOME}/soc_verification_lib/sv_cb_ex_lib/interface_uvc_lib/uart/sv/uart_pkg.sv \
             ${SOCV_KIT_HOME}/designs/socv/rtl/rtl_lpw/opencores/uart16550/rtl/uart_defines.v \
             -F ${SOCV_KIT_HOME}/designs/socv/rtl/rtl_lpw/opencores/oc_uart.irunargs \
             ./uart_ctrl/sv/uart_ctrl_defines.svh \
             ./uart_ctrl/sv/uart_ctrl_pkg.sv \
             +svseed+${SVSEED} \
             -nclibdirpath $(NCLIBDIRPATH) \
             +UVM_VERBOSITY=$(VERBOSITY) \
             +UVM_TESTNAME=$(TEST_NAME) \
             +define+LITLE_ENDIAN \
             -linedebug \
             -access +rwc \
             +define+DYNAMIC_SIM \
             -propfile_vlog ${SOCV_KIT_HOME}/designs/socv/rtl/rtl_lpw/opencores/uart16550/assertions/receiver_vunit.psl \
             -propfile_vlog ${SOCV_KIT_HOME}/designs/socv/rtl/rtl_lpw/opencores/uart16550/assertions/rx_fifo_vunit.psl \
             -propfile_vlog ${SOCV_KIT_HOME}/designs/socv/rtl/rtl_lpw/opencores/uart16550/assertions/transmitter_vunit.psl \
             -propfile_vlog ${SOCV_KIT_HOME}/designs/socv/rtl/rtl_lpw/opencores/uart16550/assertions/tx_fifo_vunit.psl \
             $(TB_FILENAME)

GUI_OPTIONS = $(OPTIONS) \
              -gui

IRUN = irun -uvmhome ${UVM_HOME} -sv -define $(WORKSHOP_MODE) -input assert_opt.tcl

#******************************************************************************#
# Targets
#******************************************************************************#

# use with run_mode=batch
test       : run_nogui

# use with run_mode=interactive and run_mode=interactive_debug
test_gui : run_gui 

# use with run_mode=interactive and run_mode=interactive_debug
run_gui : 
	${IRUN} $(GUI_OPTIONS)

# use with run_mode=batch
run_nogui : 
	${IRUN} $(OPTIONS)

clean:
	rm -rf INCA* *.log *.key .simvis* waves* *.shm  *~ cov_work

