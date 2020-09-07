/*
 * \file halfAdder.v 
 * \author Jorge Castro-Godinez <jorge.castro-godinez@kit.edu>
 * Chair for Embedded Systems (CES)
 * Karlsruhe Institute of Technology (KIT), Germany
 * Prof. Dr. Joerg Henkel
 *
 * \brief Verilog implementation of a Half Adder (HA) 
 *
 */

module halfAdder (
    input a, 
    input b,
    output s,
    output co
	);

	// sum calculation
	assign s = a ^ b;
	//carry output array calculation
	assign co = a & b;

endmodule

/*
 * \file fullAdder.v 
 * \author Jorge Castro-Godinez <jorge.castro-godinez@kit.edu>
 * Chair for Embedded Systems (CES)
 * Karlsruhe Institute of Technology (KIT), Germany
 * Prof. Dr. Joerg Henkel
 *
 * \brief Verilog implementation of a Full Adder (FA) 
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


module WT_8b(
    output [15:0] S,
    input [7:0] A, B
  );
  
  wire s00,s01,s02,s03,s04,s05,s06,s07,s10,s11,s12,s13,s14,s15,s16,s17,s20,s21,s22,s23,s24,s25,s26,s27,s30,s31,s32,s33,s34,s35,s36,s37,s40,s41,s42,s43,s44,s45,s46,s47,s50,s51,s52,s53,s54,s55,s56,s57,s60,s61,s62,s63,s64,s65,s66,s67,s70,s71,s72,s73,s74,s75,s76,s77;
  
  wire k01,k02,k03,k04,k05,k06,k07,k08,k09,k10,k11,k12,k13,k14,k15,k16,k17,k18,k19,k20,k21,k22,k23,k24,k25,k26,k27,k28,k29,k30,k31,k32,k33,k34,k35,k36,k37,k38,k39,k40,k41,k42,k43,k44,k45,k46,k47,k48,k49,k50,k51,k52,k53,k54,k55,k56,k57,k58,k59,k60,k61,k62,k63,k64,k65,k66,k67,k68;
  
  wire c01,c02,c03,c04,c05,c06,c07,c08,c09,c10,c11,c12,c13,c14,c15,c16,c17,c18,c19,c20,c21,c22,c23,c24,c25,c26,c27,c28,c29,c30,c31,c32,c33,c34,c35,c36,c37,c38,c39,c40,c41,c42,c43,c44,c45,c46,c47,c48,c49,c50,c51,c52,c53,c54,c55,c56,c57,c58,c59,c60,c61,c62,c63,c64,c65,c66,c67,c68;

  // Partial product generation
  assign s00 = A[0] & B[0];
  assign s10 = A[1] & B[0];
  assign s20 = A[2] & B[0];
  assign s30 = A[3] & B[0];
  assign s40 = A[4] & B[0];
  assign s50 = A[5] & B[0];
  assign s60 = A[6] & B[0];
  assign s70 = A[7] & B[0];

  assign s01 = A[0] & B[1];
  assign s11 = A[1] & B[1];
  assign s21 = A[2] & B[1];
  assign s31 = A[3] & B[1];
  assign s41 = A[4] & B[1];
  assign s51 = A[5] & B[1];
  assign s61 = A[6] & B[1];
  assign s71 = A[7] & B[1];

  assign s02 = A[0] & B[2];
  assign s12 = A[1] & B[2];
  assign s22 = A[2] & B[2];
  assign s32 = A[3] & B[2];
  assign s42 = A[4] & B[2];
  assign s52 = A[5] & B[2];
  assign s62 = A[6] & B[2];
  assign s72 = A[7] & B[2];

  assign s03 = A[0] & B[3];
  assign s13 = A[1] & B[3];
  assign s23 = A[2] & B[3];
  assign s33 = A[3] & B[3];
  assign s43 = A[4] & B[3];
  assign s53 = A[5] & B[3];
  assign s63 = A[6] & B[3];
  assign s73 = A[7] & B[3];

  assign s04 = A[0] & B[4];
  assign s14 = A[1] & B[4];
  assign s24 = A[2] & B[4];
  assign s34 = A[3] & B[4];
  assign s44 = A[4] & B[4];
  assign s54 = A[5] & B[4];
  assign s64 = A[6] & B[4];
  assign s74 = A[7] & B[4];

  assign s05 = A[0] & B[5];
  assign s15 = A[1] & B[5];
  assign s25 = A[2] & B[5];
  assign s35 = A[3] & B[5];
  assign s45 = A[4] & B[5];
  assign s55 = A[5] & B[5];
  assign s65 = A[6] & B[5];
  assign s75 = A[7] & B[5];

  assign s06 = A[0] & B[6];
  assign s16 = A[1] & B[6];
  assign s26 = A[2] & B[6];
  assign s36 = A[3] & B[6];
  assign s46 = A[4] & B[6];
  assign s56 = A[5] & B[6];
  assign s66 = A[6] & B[6];
  assign s76 = A[7] & B[6];

  assign s07 = A[0] & B[7];
  assign s17 = A[1] & B[7];
  assign s27 = A[2] & B[7];
  assign s37 = A[3] & B[7];
  assign s47 = A[4] & B[7];
  assign s57 = A[5] & B[7];
  assign s67 = A[6] & B[7];
  assign s77 = A[7] & B[7];

  //Stage zero
  halfAdder ha00(s01,s10,k01,c01);
  fullAdder fa00(s20,s02,s11,k02,c02);
  fullAdder fa01(s30,s21,s12,k03,c03);
  fullAdder fa02(s40,s31,s22,k04,c04);
  halfAdder ha01(s13,s04,k05,c05);
  fullAdder fa03(s50,s41,s32,k06,c06);
  fullAdder fa04(s23,s14,s05,k07,c07);
  fullAdder fa05(s60,s51,s42,k08,c08);
  fullAdder fa06(s33,s24,s15,k09,c09);
  fullAdder fa07(s70,s61,s52,k10,c10);
  fullAdder fa08(s43,s34,s25,k11,c11);
  halfAdder ha02(s16,s07,k12,c12);
  fullAdder fa09(s71,s62,s53,k13,c13);
  fullAdder fa90(s44,s35,s26,k14,c14);
  fullAdder fa31(s72,s63,s54,k15,c15);
  fullAdder fa32(s45,s36,s27,k16,c16);
  fullAdder fa33(s73,s64,s55,k17,c17);
  halfAdder ha03(s46,s37,k18,c18);
  fullAdder fa34(s74,s65,s56,k19,c19);
  fullAdder fa35(s75,s66,s57,k20,c20);
  halfAdder ha04(s76,s67,k21,c21);

  //Stage one
  halfAdder ha10(k02,c01,k22,c22);
  fullAdder fa10(s03,c02,k03,k23,c23);
  fullAdder fa11(k04,k05,c03,k24,c24);
  fullAdder fa12(k06,k07,c04,k25,c25);
  fullAdder fa13(k08,k09,s06,k26,c26);
  halfAdder ha11(c06,c07,k27,c27);
  fullAdder fa14(k10,k11,k12,k28,c28);
  halfAdder ha12(c08,c09,k29,c29);
  fullAdder fa15(k13,k14,s17,k30,c30);
  fullAdder fa16(c10,c11,c12,k31,c31);
  fullAdder fa17(k15,k16,c13,k32,c32);
  fullAdder fa18(k17,k18,c15,k33,c33);
  fullAdder fa19(k19,c17,c18,k34,c34);
  halfAdder ha13(k20,c19,k35,c35);
  halfAdder ha14(k21,c20,k36,c36);

  //Stage two
  halfAdder ha40(k23,c22,k37,c37);
  halfAdder ha41(c23,k24,k38,c38);
  fullAdder fa40(c24,k25,c05,k39,c39);
  fullAdder fa41(c25,k26,k27,k40,c40);
  fullAdder fa42(c26,c27,k28,k41,c41);
  fullAdder fa43(c28,c29,k30,k42,c42);
  fullAdder fa44(c30,c31,k32,k43,c43);
  fullAdder fa45(c32,c16,k33,k44,c44);
  fullAdder fa46(c33,s47,k34,k45,c45);
  halfAdder ha42(k35,c34,k46,c46);
  halfAdder ha43(c35,k36,k47,c47);
  fullAdder fa47(s77,c21,c36,k48,c48);

  //Stage three
  halfAdder ha50(c37,k38,k49,c49);
  fullAdder fa50(k39,c38,c49,k50,c50);
  fullAdder fa51(k40,c39,c50,k51,c51);
  fullAdder fa52(c40,k41,k29,k52,c52);
  fullAdder fa53(c41,k31,k42,k53,c53);
  fullAdder fa54(c14,c42,k43,k54,c54);
  fullAdder fa55(k44,c43,c54,k55,c55);
  fullAdder fa56(c44,k45,c55,k56,c56);
  fullAdder fa57(k46,c45,c56,k57,c57);
  fullAdder fa58(c46,k47,c57,k58,c58);
  fullAdder fa59(k48,c47,c58,k59,c59);

  //Stage four
  halfAdder ha70(c51,k52,k60,c60);
  fullAdder fa70(c52,k53,c60,k61,c61);
  fullAdder fa71(c53,k54,c61,k62,c62);
  halfAdder ha71(k55,c62,k63,c63);
  halfAdder ha72(k56,c63,k64,c64);
  halfAdder ha73(k57,c64,k65,c65);
  halfAdder ha74(k58,c65,k66,c66);
  halfAdder ha75(k59,c66,k67,c67);
  fullAdder fa81(c48,c59,c67,k68,c68);

  assign S[0] = s00;
  assign S[1] = k01;
  assign S[2] = k22;
  assign S[3] = k37;
  assign S[4] = k49;
  assign S[5] = k50;
  assign S[6] = k51;
  assign S[7] = k60;
  assign S[8] = k61;
  assign S[9] = k62;
  assign S[10] = k63;
  assign S[11] = k64;
  assign S[12] = k65;
  assign S[13] = k66;
  assign S[14] = k67;
  assign S[15] = k68 | c68;

endmodule
