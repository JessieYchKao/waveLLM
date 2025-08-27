
======================================================================
Title: Cadence SimVision Debug Demo Package 
======================================================================

=====================
1.0 - General Notes:
=====================

Please read this README file completely, and perform any needed steps in 
order to ensure a successful workshop.  These demos were tested on Xcelium 
17.09.001. They should function with earlier releases as well however, this 
is not guaranteed.


=====================
2.0 - Dependencies: 
=====================

Before running any of these labs, ensure that you've set up all needed tools 
correctly (installed version of Xcelium and paths updated to point to the
tools).

The labs make use of the following environment variables within their scripts.
Both of these environment variables are set automatically for you when you run
a simulation with the run scripts mentioned below. 

        - $SIMDEBUG_WS        - Points to the Workshop directory from the
                                simulation directory 
        - $CUR_LABDIR         - Points to the current demo directory  

The demos require the following SystemVerilog packages, all of which are
included within the NYSimVisionTrainingOct_2017/pkg_lib directory:

        - apb_pkg 
        - uart_ctrl_pkg 
        - uart_pkg 
        - uvm_pkg 

=============================
3.0 - Demo directory details:
=============================

NYSimVisionTrainingOct_2017/
        pkg_lib/		- Contains packages needed to run the demos 
	demo/	        	- Directory containing the demo code 
           /scripts		- Contains the scripts needed to run simulations 
              run.csh   	- Run script for all demos
              run_indago.csh   	- Run script to run with Indago recording
              module_irun.args 	- Arguments file that run.csh pulls in
              probe.tcl         - TCL script that contains probe and simulator
                                  commands to execute at the start of a simulation 
              indago_probe.tcl  - TCL script that contains probe and simulator
                                  commands to probe simulation data for Indago 
           /sim			- Directory in which to run simulations
  	   /pkg_lib		- Contains custom packages needed for demos 
   
=======================================================
4.0 - To run various demo examples: 
=======================================================

1.	Indago debug of assertion error (with wave/SmartLog DB)	
        %> cd demo/sim
        %> ../scripts/run_indago.csh 
        %> indago -db SmartLogWaves.db &

2.      Run a really long test with Indago dumping of waves/SmartLog (good for generating large waveform DB)
        %> cd demo/sim
	%> ../scripts/run_indago.csh -define NO_ASSERTION 

3.	Indago UVM Interactive Debug	
        %> cd demo/sim
	%> ../scripts/run_indago.csh -gui -indago 

4. 	SimVision C/C++/SC Demo: 
        %> cd demo/sim
	%> ../scripts/run.csh -gui  

5.	SimVision UVM Interactive Debug	
        %> cd demo/sim
	%> ../scripts/run.csh -gui  

6.	SimVision UVM Post Process Debug	
        %> cd demo/sim
        %> ../scripts/run.csh 
        %> simvision waves.shm &
        
7.	SimVision Debugging a hang between two always blocks 
        %> cd demo/sim
        %> ../scripts/run.csh -define PING_PONG -gui       

8.	SimVision Debugging a hang in a clock generation block 
        %> cd demo/sim
        %> ../scripts/run.csh -define HANG -gui       
