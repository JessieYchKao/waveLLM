#Open a waveform DB with event (glitch information) 
ida_database -open -name=SmartLogWaves.db

#Probe log messages to SmartLog DB
ida_probe -log 

# Probe all HDL, all levels
ida_probe -wave -wave_probe_args="uart_ctrl_top -all -depth all -memories -packed 0 -unpacked 0 -tasks"

# Perobe the UVM Hierarchy, all levels, all content including dynamic queues/arrays
ida_probe -wave -wave_probe_args="$uvm:{uvm_test_top.uart_ctrl_tb0.apb0} -depth all -all -dynamic"

# Run to end of build 
uvm_phase -stop_at build -end
run

#Enable transaction recording for all UVM components
uvm_set "*" "recording_detail" UVM_FULL

if {!$simvision_attached} {
   run;
   exit;
};

