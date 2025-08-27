uvm_phase -stop_at -begin run_phase; run
stop -delete 1
stop -create -condition {#uart_ctrl_top.apb_if0.paddr[7:0] == 'h01}
run
run
