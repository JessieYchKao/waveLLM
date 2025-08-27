#!/bin/csh -f

setenv SIMDEBUG_WS ../../
setenv CUR_LABDIR ../
setenv XMROOT `xmroot`
cd ../../pkg_lib/dpi_code
./make_so.csh
cd -
xrun -f ${CUR_LABDIR}/scripts/xrun.args -input ${CUR_LABDIR}/scripts/probe.tcl +UVM_TESTNAME=uart_bad_parity_test $*
