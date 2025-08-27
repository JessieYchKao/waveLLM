/*-------------------------------------------------------------------------
File name   : test_lib.sv
Title       : Library of tests
Project     :
Created     :
Description : Library of tests for the APB-UART Environment
Notes       : Includes all the test files. Whenever a new test case file is 
            : created the file has to be included here
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/

`include "u2a_incr_payload.sv"
`include "apb_uart_rx_tx.sv"
`include "u2a_incr_payld_bd_parity.sv"
`include "uart_data_auto_lab1.sv"
`include "uart_incr_payld_bd_parity_factory.sv"
`include "uart_bad_driver_factory_lab3.sv"
`include "apb_to_uart_1stopbit.sv"
`include "uart_rx_tx_fifo_coverage.sv"
`include "apb_uart_rx_tx_data_aa.sv"
