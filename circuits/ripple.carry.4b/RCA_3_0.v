/*
 * \file RCA_3_0.v 
 * \author Jorge Castro-Godinez <jorge.castro-godinez@kit.edu>
 * Chair for Embedded Systems (CES)
 * Karlsruhe Institute of Technology (KIT), Germany
 * Prof. Dr. Joerg Henkel
 *
 * \brief Verilog implementation of a 4-bit Ripple Carry Adder (RCA)
 *
 */

module fullAdder (
		input a, 
		input b,
		input ci,
		output s,
		output co
	);

	wire p,g;

	// propagation signal
	xor (p,a,b);
	// generation signal
	and (g,a,b);

	// sum calculation
	assign s = p ^ ci;
	//carry output array calculation
	assign co = g | (p & ci);

endmodule


module RCA_3_0(
		input [3:0] in1, 
		input [3:0] in2,
	    	input cin,
		output [4:0] out
);

	wire c0,c1,c2,c3;

	fullAdder FA0(in1[0],in2[0],cin,out[0],c0);
	fullAdder FA1(in1[1],in2[1],c0,out[1],c1);
	fullAdder FA2(in1[2],in2[2],c1,out[2],c2);
	fullAdder FA3(in1[3],in2[3],c2,out[3],c3);
  
	assign out[4] = c3;
endmodule
