database -open -shm -into waves.shm waves -default
probe -create -database waves uart_tb_top.uif0.clock uart_tb_top.uif0.cts_n uart_tb_top.uif0.dcd_n uart_tb_top.uif0.dsr_n uart_tb_top.uif0.dtr_n uart_tb_top.uif0.has_checks uart_tb_top.uif0.has_coverage uart_tb_top.uif0.intrpt uart_tb_top.uif0.reset uart_tb_top.uif0.ri_n uart_tb_top.uif0.rts_n uart_tb_top.uif0.rxd uart_tb_top.uif0.txd uart_tb_top.apbi0.paddr uart_tb_top.apbi0.pclock uart_tb_top.apbi0.penable uart_tb_top.apbi0.prdata uart_tb_top.apbi0.pready uart_tb_top.apbi0.preset uart_tb_top.apbi0.prwd uart_tb_top.apbi0.psel uart_tb_top.apbi0.pwdata

run 4000ns
simvision -input lab4.svcf
