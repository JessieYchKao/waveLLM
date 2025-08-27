module lv_asserts;

	reg a=1,c=1;
	reg clk = 0;
	reg b=0,d=1;
	
	always #10 clk = ~clk;
        initial begin
	  #200 $finish;
        end	
	property Pl; 
		int lv = 0;
		@(posedge clk) 
		a ##1 (!b, lv++) |=> ##1 (c,lv=lv-1) ##1 d ##1 !lv;
	endproperty

	A1: assert property(Pl);
	

endmodule
