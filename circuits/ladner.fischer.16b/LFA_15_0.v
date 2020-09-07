/*
 * 16-bit Ladner-Fischer Adder
 *
 * Steve Barrus
 */

 module gray (pg, pg0, pgo);
     input [1:0] pg;
     input pg0;
     output pgo;

     assign pgo = (pg0 & pg[1]) | pg[0];

 endmodule

 module black (pg, pg0, pgo);
     input [1:0] pg, pg0;
     output [1:0] pgo;

     assign pgo[1] = pg[1] & pg0[1];
     assign pgo[0] = (pg0[0] & pg[1]) | pg[0];

 endmodule

 module xor16 (A, B, S);
     input [15:0] A, B;
     output [15:0] S;

     assign S = A ^ B;

 endmodule

 module xor32 (A, B, S);
     input [31:0] A, B;
     output [31:0] S;

     assign S = A ^ B;

 endmodule

 module pg16 (A, B, pg15, pg14, pg13, pg12, pg11, pg10, pg9, pg8, pg7, pg6, pg5, pg4, pg3, pg2, pg1, pg0);
     input [15:0] A, B;
     output [1:0] pg15, pg14, pg13, pg12, pg11, pg10, pg9, pg8, pg7, pg6, pg5, pg4, pg3, pg2, pg1, pg0;

     assign pg15 = {(A[15] ^ B[15]), (A[15] & B[15])};
     assign pg14 = {(A[14] ^ B[14]), (A[14] & B[14])};
     assign pg13 = {(A[13] ^ B[13]), (A[13] & B[13])};
     assign pg12 = {(A[12] ^ B[12]), (A[12] & B[12])};
     assign pg11 = {(A[11] ^ B[11]), (A[11] & B[11])};
     assign pg10 = {(A[10] ^ B[10]), (A[10] & B[10])};
     assign pg9 = {(A[9] ^ B[9]), (A[9] & B[9])};
     assign pg8 = {(A[8] ^ B[8]), (A[8] & B[8])};
     assign pg7 = {(A[7] ^ B[7]), (A[7] & B[7])};
     assign pg6 = {(A[6] ^ B[6]), (A[6] & B[6])};
     assign pg5 = {(A[5] ^ B[5]), (A[5] & B[5])};
     assign pg4 = {(A[4] ^ B[4]), (A[4] & B[4])};
     assign pg3 = {(A[3] ^ B[3]), (A[3] & B[3])};
     assign pg2 = {(A[2] ^ B[2]), (A[2] & B[2])};
     assign pg1 = {(A[1] ^ B[1]), (A[1] & B[1])};
     assign pg0 = {(A[0] ^ B[0]), (A[0] & B[0])};

 endmodule

 module pg32 (A, B, pg31, pg30, pg29, pg28, pg27, pg26, pg25, pg24, pg23, pg22, pg21, pg20, pg19, pg18, pg17, pg16, pg15, pg14, pg13, pg12, pg11, pg10, pg9, pg8, pg7, pg6, pg5, pg4, pg3, pg2, pg1, pg0);
     input [31:0] A, B;
     output [1:0] pg31, pg30, pg29, pg28, pg27, pg26, pg25, pg24, pg23, pg22, pg21, pg20, pg19, pg18, pg17, pg16, pg15, pg14, pg13, pg12, pg11, pg10, pg9, pg8, pg7, pg6, pg5, pg4, pg3, pg2, pg1, pg0;

     assign pg31 = {(A[31] ^ B[31]), (A[31] & B[31])};
     assign pg30 = {(A[30] ^ B[30]), (A[30] & B[30])};
     assign pg29 = {(A[29] ^ B[29]), (A[29] & B[29])};
     assign pg28 = {(A[28] ^ B[28]), (A[28] & B[28])};
     assign pg27 = {(A[27] ^ B[27]), (A[27] & B[27])};
     assign pg26 = {(A[26] ^ B[26]), (A[26] & B[26])};
     assign pg25 = {(A[25] ^ B[25]), (A[25] & B[25])};
     assign pg24 = {(A[24] ^ B[24]), (A[24] & B[24])};
     assign pg23 = {(A[23] ^ B[23]), (A[23] & B[23])};
     assign pg22 = {(A[22] ^ B[22]), (A[22] & B[22])};
     assign pg21 = {(A[21] ^ B[21]), (A[21] & B[21])};
     assign pg20 = {(A[20] ^ B[20]), (A[20] & B[20])};
     assign pg19 = {(A[19] ^ B[19]), (A[19] & B[19])};
     assign pg18 = {(A[18] ^ B[18]), (A[18] & B[18])};
     assign pg17 = {(A[17] ^ B[17]), (A[17] & B[17])};
     assign pg16 = {(A[16] ^ B[16]), (A[16] & B[16])};
     assign pg15 = {(A[15] ^ B[15]), (A[15] & B[15])};
     assign pg14 = {(A[14] ^ B[14]), (A[14] & B[14])};
     assign pg13 = {(A[13] ^ B[13]), (A[13] & B[13])};
     assign pg12 = {(A[12] ^ B[12]), (A[12] & B[12])};
     assign pg11 = {(A[11] ^ B[11]), (A[11] & B[11])};
     assign pg10 = {(A[10] ^ B[10]), (A[10] & B[10])};
     assign pg9 = {(A[9] ^ B[9]), (A[9] & B[9])};
     assign pg8 = {(A[8] ^ B[8]), (A[8] & B[8])};
     assign pg7 = {(A[7] ^ B[7]), (A[7] & B[7])};
     assign pg6 = {(A[6] ^ B[6]), (A[6] & B[6])};
     assign pg5 = {(A[5] ^ B[5]), (A[5] & B[5])};
     assign pg4 = {(A[4] ^ B[4]), (A[4] & B[4])};
     assign pg3 = {(A[3] ^ B[3]), (A[3] & B[3])};
     assign pg2 = {(A[2] ^ B[2]), (A[2] & B[2])};
     assign pg1 = {(A[1] ^ B[1]), (A[1] & B[1])};
     assign pg0 = {(A[0] ^ B[0]), (A[0] & B[0])};

 endmodule

 module inv(A, Y);
     input A;
     output Y;
     assign Y = ~A;
 endmodule

 module and2(A, B, Y);
     input A, B;
     output Y;
     assign Y = (A & B);
 endmodule

 module nand2(A, B, Y);
     input A, B;
     output Y;
     assign Y = ~(A & B);
 endmodule

 module or2(A, B, Y);
     input A, B;
     output Y;
     assign Y = (A | B);
 endmodule

 module nor2(A, B, Y);
     input A, B;
     output Y;
     assign Y = ~(A | B);
 endmodule

 module tiehi(Y);
     output Y;
     assign Y = 1'b1;
 endmodule

 module tielo(Y);
     output Y;
     assign Y = 1'b0;
 endmodule

 module xor2(A, B, Y);
     input A, B;
     output Y;
     assign Y = A ^ B;
 endmodule

module LadnerFischer16 (A, B, Cin, S, Cout);
    input [15:0] A, B;
    input Cin;
    output [15:0] S;
    output Cout;

    /* First generate the propigate and generate signals for each bit */
    wire [1:0] r1c16, r1c15, r1c14, r1c13, r1c12, r1c11, r1c10, r1c9;
    wire [1:0] r1c8, r1c7, r1c6, r1c5, r1c4, r1c3, r1c2, r1c1;

    pg16 ipg16(.A(A), .B(B), .pg15(r1c16),.pg14(r1c15),.pg13(r1c14),
        .pg12(r1c13),.pg11(r1c12),.pg10(r1c11),.pg9(r1c10),.pg8(r1c9),
        .pg7(r1c8),.pg6(r1c7),.pg5(r1c6),.pg4(r1c5),.pg3(r1c4),.pg2(r1c3),
        .pg1(r1c2),.pg0(r1c1));

    /* First row */
    wire [1:0] r2c15, r2c13, r2c11, r2c9, r2c7, r2c5, r2c3;
    wire r2c1;

    black ir1c15(.pg(r1c15), .pg0(r1c14), .pgo(r2c15));
    black ir1c13(.pg(r1c13), .pg0(r1c12), .pgo(r2c13));
    black ir1c11(.pg(r1c11), .pg0(r1c10), .pgo(r2c11));
    black ir1c9(.pg(r1c9), .pg0(r1c8), .pgo(r2c9));
    black ir1c7(.pg(r1c7), .pg0(r1c6), .pgo(r2c7));
    black ir1c5(.pg(r1c5), .pg0(r1c4), .pgo(r2c5));
    black ir1c3(.pg(r1c3), .pg0(r1c2), .pgo(r2c3));
    gray ir1c1(.pg(r1c1), .pg0(Cin), .pgo(r2c1));

    /* Second row */
    wire [1:0] r3c15, r3c11, r3c7;
    wire r3c3;

    black ir2c15(.pg(r2c15), .pg0(r2c13), .pgo(r3c15));
    black ir2c11(.pg(r2c11), .pg0(r2c9), .pgo(r3c11));
    black ir2c7(.pg(r2c7), .pg0(r2c5), .pgo(r3c7));
    gray ir2c3(.pg(r2c3), .pg0(r2c1), .pgo(r3c3));

    /* Third row */
    wire [1:0] r4c15, r4c13;
    wire r4c7, r4c5;

    black ir3c15(.pg(r3c15), .pg0(r3c11), .pgo(r4c15));
    black ir3c13(.pg(r2c13), .pg0(r3c11), .pgo(r4c13));
    gray ir3c7(.pg(r3c7), .pg0(r3c3), .pgo(r4c7));
    gray ir3c5(.pg(r2c5), .pg0(r3c3), .pgo(r4c5));

    /* Fourth row */
    wire r5c15, r5c13, r5c11, r5c9;

    gray ir4c15(.pg(r4c15), .pg0(r4c7), .pgo(r5c15));
    gray ir4c13(.pg(r4c13), .pg0(r4c7), .pgo(r5c13));
    gray ir4c11(.pg(r3c11), .pg0(r4c7), .pgo(r5c11));
    gray ir4c9(.pg(r2c9), .pg0(r4c7), .pgo(r5c9));

    /* Fifth row */
    wire r6c14, r6c12, r6c10, r6c8, r6c6, r6c4, r6c2;

    gray ir6c14(.pg(r1c14), .pg0(r5c13), .pgo(r6c14));
    gray ir6c12(.pg(r1c12), .pg0(r5c11), .pgo(r6c12));
    gray ir6c10(.pg(r1c10), .pg0(r5c9), .pgo(r6c10));
    gray ir6c8(.pg(r1c8), .pg0(r4c7), .pgo(r6c8));
    gray ir6c6(.pg(r1c6), .pg0(r4c5), .pgo(r6c6));
    gray ir6c4(.pg(r1c4), .pg0(r3c3), .pgo(r6c4));
    gray ir6c2(.pg(r1c2), .pg0(r2c1), .pgo(r6c2));

    /* Finaly produce the sum */
    xor16 ixor16(.A({r5c15,r6c14,r5c13,r6c12,r5c11,r6c10,r5c9,
        r6c8,r4c7,r6c6,r4c5,r6c4,r3c3,r6c2,r2c1,Cin}), .B({r1c16[1],
        r1c15[1],r1c14[1],r1c13[1],r1c12[1],r1c11[1],r1c10[1],r1c9[1],
        r1c8[1],r1c7[1],r1c6[1],r1c5[1],r1c4[1],r1c3[1],r1c2[1],
        r1c1[1]}), .S(S));

    /* Generate Cout */
    gray gcout(.pg(r1c16), .pg0(r5c15), .pgo(Cout));

endmodule

module LFA_15_0 (S, X, Y);
  output [16:0] S;
  input [15:0] X;
  input [15:0] Y;
  wire Cout;
  LadnerFischer16 U0 (X, Y, 1'b0, S[15:0], Cout);
  assign S[16] = Cout;
endmodule
