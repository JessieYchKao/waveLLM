uvm_set -config "*" "recording_detail" UVM_FULL
uvm_phase -stop_at run_phase
run
run -clean
stop -delete 1
save -simulation build
probe -create -shm worklib.uvm_pkg::uvm_top -depth all -all
run
exit

#
# visualize waves in post-processing mode
# simvision -waves ncsim.shm -snapshot build 
