class my_class;
   integer i, j, k;
   rand reg [7:0] my_3D_class_array [2][3][2];

   // testing
   function bla();
   endfunction

    function new();
       for (i=0; i<2; i++) begin
         for (j=0; j<3; j++) begin
            for (k=0; k<2; k++) begin
              my_3D_class_array[i][j][k] = i+j+k;
            end
         end
      end
    endfunction
endclass

class my_top_class;

 //my_class mdc = new();

 // simple queue
 rand reg [7:0] my_q [$];
 rand reg [7:0] my_2D_q [2][3];
 rand int i, j, k;
 rand reg [7:0] corey; 
 //`rand reg [7:0] my_3D_q [2][3][$];

endclass 

module md_top(); 

   my_top_class my_top = new();
   integer i, j, k;
   integer zero_time_loop = 0;

   // 2D array of classes, each containing a 3D array 
   // within 
   my_class my_2D_class_array [4][3];

   // push some items onto the queue 
   initial begin
     forever begin 
        for(int num_to_push = 0; num_to_push <= 100; num_to_push++) begin
           #1000;
           my_top.my_q.push_front(num_to_push);
        end //for 
     end // forever 
   end 

   initial begin
      //my_top.my_2D_q = new();
      assert(my_top.randomize());
      //my_top.my_3D_q = new();
      //assert(my_top.my_3D_q.randomize());

      //my_top.mdc = new();
      #100;
      //assert(my_top.mdc.randomize()); 

      for (integer i=0; i<4; i++) begin
         for (integer j=0; j<3; j++) begin
            my_2D_class_array[i][j] = new();
            assert(my_2D_class_array[i][j].randomize());
         end 
      end 

      //assert(md_class_array.randomize()); 
      for (i=0; i<2; i++) begin
         for (j=0; j<3; j++) begin
            for (k=0; k<2; k++) begin
              //$display("Here are the array elements: my_3D_class_array[%0d][%0d][%0d]", i, j, k, my_top.mdc.my_3D_class_array[i][j][k]);
            end 
         end 
      end
      #150000;
   end // initial 


  initial begin 
     for (zero_time_loop = 0; zero_time_loop < 200; zero_time_loop++) begin
         zero_time_loop++;
     end // for
  end //initial
endmodule
