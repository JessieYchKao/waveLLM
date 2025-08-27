
/*
<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
Standalone test file to test generated register definition file
 To simlulate : 
    irun -clean -uvmhome $UVM_HOME \
      +incdir+. \
      ./quickTest.sv
<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
*/
module test();
  import uvm_pkg::*;
  `include "uvm_macros.svh"
  `include "./uart_ctrl_regs.sv"

class test extends uvm_test;
  uart_ctrl_addr_map_c reg_block;
  
  function void build();
    uvm_reg::include_coverage("*", UVM_CVR_ALL);
    reg_block=uart_ctrl_addr_map_c::type_id::create("reg_block", this);
    reg_block.build();
  endfunction
  
  task run();
    reg_block.reset();
    reg_block.print();
    global_stop_request();
  endtask
  `uvm_component_utils(test)
  function new(string name, uvm_component parent);
    super.new(name,parent);
  endfunction
endclass
  initial run_test("test");
endmodule
