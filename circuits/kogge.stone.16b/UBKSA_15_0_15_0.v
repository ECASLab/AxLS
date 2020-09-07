/*----------------------------------------------------------------------------
  Copyright (c) 2004 Aoki laboratory. All rights reserved.

  Top module: UBKSA_15_0_15_0

  Operand-1 length: 16
  Operand-2 length: 16
  Two-operand addition algorithm: Kogge-Stone adder
----------------------------------------------------------------------------*/

module GPGenerator(Go, Po, A, B);
  output Go;
  output Po;
  input A;
  input B;
  assign Go = A & B;
  assign Po = A ^ B;
endmodule

module CarryOperator(Go, Po, Gi1, Pi1, Gi2, Pi2);
  output Go;
  output Po;
  input Gi1;
  input Gi2;
  input Pi1;
  input Pi2;
  assign Go = Gi1 | ( Gi2 & Pi1 );
  assign Po = Pi1 & Pi2;
endmodule

module UBPriKSA_15_0(S, X, Y, Cin);
  output [16:0] S;
  input Cin;
  input [15:0] X;
  input [15:0] Y;
  wire [15:0] G0;
  wire [15:0] G1;
  wire [15:0] G2;
  wire [15:0] G3;
  wire [15:0] G4;
  wire [15:0] P0;
  wire [15:0] P1;
  wire [15:0] P2;
  wire [15:0] P3;
  wire [15:0] P4;
  assign P1[0] = P0[0];
  assign G1[0] = G0[0];
  assign P2[0] = P1[0];
  assign G2[0] = G1[0];
  assign P2[1] = P1[1];
  assign G2[1] = G1[1];
  assign P3[0] = P2[0];
  assign G3[0] = G2[0];
  assign P3[1] = P2[1];
  assign G3[1] = G2[1];
  assign P3[2] = P2[2];
  assign G3[2] = G2[2];
  assign P3[3] = P2[3];
  assign G3[3] = G2[3];
  assign P4[0] = P3[0];
  assign G4[0] = G3[0];
  assign P4[1] = P3[1];
  assign G4[1] = G3[1];
  assign P4[2] = P3[2];
  assign G4[2] = G3[2];
  assign P4[3] = P3[3];
  assign G4[3] = G3[3];
  assign P4[4] = P3[4];
  assign G4[4] = G3[4];
  assign P4[5] = P3[5];
  assign G4[5] = G3[5];
  assign P4[6] = P3[6];
  assign G4[6] = G3[6];
  assign P4[7] = P3[7];
  assign G4[7] = G3[7];
  assign S[0] = Cin ^ P0[0];
  assign S[1] = ( G4[0] | ( P4[0] & Cin ) ) ^ P0[1];
  assign S[2] = ( G4[1] | ( P4[1] & Cin ) ) ^ P0[2];
  assign S[3] = ( G4[2] | ( P4[2] & Cin ) ) ^ P0[3];
  assign S[4] = ( G4[3] | ( P4[3] & Cin ) ) ^ P0[4];
  assign S[5] = ( G4[4] | ( P4[4] & Cin ) ) ^ P0[5];
  assign S[6] = ( G4[5] | ( P4[5] & Cin ) ) ^ P0[6];
  assign S[7] = ( G4[6] | ( P4[6] & Cin ) ) ^ P0[7];
  assign S[8] = ( G4[7] | ( P4[7] & Cin ) ) ^ P0[8];
  assign S[9] = ( G4[8] | ( P4[8] & Cin ) ) ^ P0[9];
  assign S[10] = ( G4[9] | ( P4[9] & Cin ) ) ^ P0[10];
  assign S[11] = ( G4[10] | ( P4[10] & Cin ) ) ^ P0[11];
  assign S[12] = ( G4[11] | ( P4[11] & Cin ) ) ^ P0[12];
  assign S[13] = ( G4[12] | ( P4[12] & Cin ) ) ^ P0[13];
  assign S[14] = ( G4[13] | ( P4[13] & Cin ) ) ^ P0[14];
  assign S[15] = ( G4[14] | ( P4[14] & Cin ) ) ^ P0[15];
  assign S[16] = G4[15] | ( P4[15] & Cin );
  GPGenerator U0 (G0[0], P0[0], X[0], Y[0]);
  GPGenerator U1 (G0[1], P0[1], X[1], Y[1]);
  GPGenerator U2 (G0[2], P0[2], X[2], Y[2]);
  GPGenerator U3 (G0[3], P0[3], X[3], Y[3]);
  GPGenerator U4 (G0[4], P0[4], X[4], Y[4]);
  GPGenerator U5 (G0[5], P0[5], X[5], Y[5]);
  GPGenerator U6 (G0[6], P0[6], X[6], Y[6]);
  GPGenerator U7 (G0[7], P0[7], X[7], Y[7]);
  GPGenerator U8 (G0[8], P0[8], X[8], Y[8]);
  GPGenerator U9 (G0[9], P0[9], X[9], Y[9]);
  GPGenerator U10 (G0[10], P0[10], X[10], Y[10]);
  GPGenerator U11 (G0[11], P0[11], X[11], Y[11]);
  GPGenerator U12 (G0[12], P0[12], X[12], Y[12]);
  GPGenerator U13 (G0[13], P0[13], X[13], Y[13]);
  GPGenerator U14 (G0[14], P0[14], X[14], Y[14]);
  GPGenerator U15 (G0[15], P0[15], X[15], Y[15]);
  CarryOperator U16 (G1[1], P1[1], G0[1], P0[1], G0[0], P0[0]);
  CarryOperator U17 (G1[2], P1[2], G0[2], P0[2], G0[1], P0[1]);
  CarryOperator U18 (G1[3], P1[3], G0[3], P0[3], G0[2], P0[2]);
  CarryOperator U19 (G1[4], P1[4], G0[4], P0[4], G0[3], P0[3]);
  CarryOperator U20 (G1[5], P1[5], G0[5], P0[5], G0[4], P0[4]);
  CarryOperator U21 (G1[6], P1[6], G0[6], P0[6], G0[5], P0[5]);
  CarryOperator U22 (G1[7], P1[7], G0[7], P0[7], G0[6], P0[6]);
  CarryOperator U23 (G1[8], P1[8], G0[8], P0[8], G0[7], P0[7]);
  CarryOperator U24 (G1[9], P1[9], G0[9], P0[9], G0[8], P0[8]);
  CarryOperator U25 (G1[10], P1[10], G0[10], P0[10], G0[9], P0[9]);
  CarryOperator U26 (G1[11], P1[11], G0[11], P0[11], G0[10], P0[10]);
  CarryOperator U27 (G1[12], P1[12], G0[12], P0[12], G0[11], P0[11]);
  CarryOperator U28 (G1[13], P1[13], G0[13], P0[13], G0[12], P0[12]);
  CarryOperator U29 (G1[14], P1[14], G0[14], P0[14], G0[13], P0[13]);
  CarryOperator U30 (G1[15], P1[15], G0[15], P0[15], G0[14], P0[14]);
  CarryOperator U31 (G2[2], P2[2], G1[2], P1[2], G1[0], P1[0]);
  CarryOperator U32 (G2[3], P2[3], G1[3], P1[3], G1[1], P1[1]);
  CarryOperator U33 (G2[4], P2[4], G1[4], P1[4], G1[2], P1[2]);
  CarryOperator U34 (G2[5], P2[5], G1[5], P1[5], G1[3], P1[3]);
  CarryOperator U35 (G2[6], P2[6], G1[6], P1[6], G1[4], P1[4]);
  CarryOperator U36 (G2[7], P2[7], G1[7], P1[7], G1[5], P1[5]);
  CarryOperator U37 (G2[8], P2[8], G1[8], P1[8], G1[6], P1[6]);
  CarryOperator U38 (G2[9], P2[9], G1[9], P1[9], G1[7], P1[7]);
  CarryOperator U39 (G2[10], P2[10], G1[10], P1[10], G1[8], P1[8]);
  CarryOperator U40 (G2[11], P2[11], G1[11], P1[11], G1[9], P1[9]);
  CarryOperator U41 (G2[12], P2[12], G1[12], P1[12], G1[10], P1[10]);
  CarryOperator U42 (G2[13], P2[13], G1[13], P1[13], G1[11], P1[11]);
  CarryOperator U43 (G2[14], P2[14], G1[14], P1[14], G1[12], P1[12]);
  CarryOperator U44 (G2[15], P2[15], G1[15], P1[15], G1[13], P1[13]);
  CarryOperator U45 (G3[4], P3[4], G2[4], P2[4], G2[0], P2[0]);
  CarryOperator U46 (G3[5], P3[5], G2[5], P2[5], G2[1], P2[1]);
  CarryOperator U47 (G3[6], P3[6], G2[6], P2[6], G2[2], P2[2]);
  CarryOperator U48 (G3[7], P3[7], G2[7], P2[7], G2[3], P2[3]);
  CarryOperator U49 (G3[8], P3[8], G2[8], P2[8], G2[4], P2[4]);
  CarryOperator U50 (G3[9], P3[9], G2[9], P2[9], G2[5], P2[5]);
  CarryOperator U51 (G3[10], P3[10], G2[10], P2[10], G2[6], P2[6]);
  CarryOperator U52 (G3[11], P3[11], G2[11], P2[11], G2[7], P2[7]);
  CarryOperator U53 (G3[12], P3[12], G2[12], P2[12], G2[8], P2[8]);
  CarryOperator U54 (G3[13], P3[13], G2[13], P2[13], G2[9], P2[9]);
  CarryOperator U55 (G3[14], P3[14], G2[14], P2[14], G2[10], P2[10]);
  CarryOperator U56 (G3[15], P3[15], G2[15], P2[15], G2[11], P2[11]);
  CarryOperator U57 (G4[8], P4[8], G3[8], P3[8], G3[0], P3[0]);
  CarryOperator U58 (G4[9], P4[9], G3[9], P3[9], G3[1], P3[1]);
  CarryOperator U59 (G4[10], P4[10], G3[10], P3[10], G3[2], P3[2]);
  CarryOperator U60 (G4[11], P4[11], G3[11], P3[11], G3[3], P3[3]);
  CarryOperator U61 (G4[12], P4[12], G3[12], P3[12], G3[4], P3[4]);
  CarryOperator U62 (G4[13], P4[13], G3[13], P3[13], G3[5], P3[5]);
  CarryOperator U63 (G4[14], P4[14], G3[14], P3[14], G3[6], P3[6]);
  CarryOperator U64 (G4[15], P4[15], G3[15], P3[15], G3[7], P3[7]);
endmodule

module UBZero_0_0(O);
  output [0:0] O;
  assign O[0] = 0;
endmodule

module UBKSA_15_0_15_0 (S, X, Y);
  output [16:0] S;
  input [15:0] X;
  input [15:0] Y;
  UBPureKSA_15_0 U0 (S[16:0], X[15:0], Y[15:0]);
endmodule

module UBPureKSA_15_0 (S, X, Y);
  output [16:0] S;
  input [15:0] X;
  input [15:0] Y;
  wire C;
  UBPriKSA_15_0 U0 (S, X, Y, 1'b0);
  //UBZero_0_0 U1 (C);
endmodule

