`timescale 1 ns / 10 ps
module dff (clr,ck,d,q,qb,fjk);
 input clr,ck,d,fjk;
 output q,qb;

 DFFR u1(.CLR_(clr1), .CLK(ck1), .Q(q1), .Q_(qb1), .D(d1));
 INV u2(.Y(clr1), .A(clr));
 INV u3(.Y(ck1), .A(ck));
 INV u4(.Y(q), .A(q1));
 INV u5(.Y(qb), .A(qb1));
 INV u6(.Y(d1), .A(d));
 INV u7(.Y(xx), .A(fjk));
initial $sdf_annotate("/export/home/cgoss/demos/latest/Debug/pkg_lib/cells/ncv.sdf",,,"/export/home/cgoss/demos/latest/Debug/pkg_lib/cells/a.log");

endmodule

