/*-------------------------------------------------------------------------
File name   : test.sv
Title       : LAB 1
Project     : SystemVerilog UVM Debug Lab
Created     : 01/08/2009
Description : This file implements a simple test for class library and 
            : related methods to focus on SV class debug
Notes       :  
----------------------------------------------------------------------*/
//   Copyright 1999-2010 Cadence Design Systems, Inc.
//   All Rights Reserved Worldwide
//
//   Licensed under the Apache License, Version 2.0 (the
//   "License"); you may not use this file except in
//   compliance with the License.  You may obtain a copy of
//   the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
//   Unless required by applicable law or agreed to in
//   writing, software distributed under the License is
//   distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
//   CONDITIONS OF ANY KIND, either express or implied.  See
//   the License for the specific language governing
//   permissions and limitations under the License.
//----------------------------------------------------------------------

module top;

  class parent;

    integer int_var;
    int q_int[$:10]; //queue, max size = 10
    int d_int[]; //dynamic array
    int aa_int[string]; //AA with string index

    function new(int dsize = 10);
      d_int = new[dsize];
    endfunction: new

    function void del;
      q_int.delete();
      d_int.delete();
      aa_int.delete();
    endfunction: del

    task set_var (integer i);
      int_var = i;
    endtask: set_var

    virtual function integer get_var ();
      get_var = int_var;
    endfunction: get_var

  endclass: parent

  class child extends parent;
    integer child_int_var;

    task set_var (integer i);
      int_var = 2 * i;
      child_int_var = 4 * i;
    endtask: set_var

    virtual function integer get_var ();
      get_var = this.int_var + 1;
    endfunction: get_var

  endclass: child

  integer int1, int2 , int3, int4;
  parent parent1, parent2;
  child child1;

  initial begin
    parent1 = new;
    child1 = new;
    parent2 = child1;
    child1 = new;
    
    #10 parent1.set_var(1);
    set_arr();
    int1 = parent1.get_var();        // should == 1
    
    #10 parent2.set_var(1);
    int2 = parent2.get_var();        // should == 2
    for (int i = 0; i < 10; i=i+2)
      begin
        #10;
	parent1.q_int.delete(9-i);
        parent1.aa_int.delete($psprintf("REG%0d",i)); 
      end
    #10 child1.set_var(1);
    int3 = child1.get_var();        // should == 3
    int4 = child1.child_int_var;    // should == 4
    parent1.del();

    #10 parent1.int_var = 0;
    child1.child_int_var = 0;

    #10 parent1 = null;
    parent2 = null;
    child1 = null;
    
    #10 $display ("int1 = ", int1);
    $display ("int2 = ", int2);
    $display ("int3 = ", int3);
    $display ("int4 = ", int4);

    #10 $finish;
  end

  task set_arr();
    begin
      for (int i = 0; i < 10; i++)
      begin
        #10;
        parent1.q_int.push_front(i);
        parent1.d_int[i] = i*2;
        parent1.aa_int[$psprintf("REG%0d",i)] = i*4;
      end
    end
  endtask: set_arr

endmodule

