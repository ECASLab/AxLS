/*
 * cells.v
 *
 * Support cell library for adder circuits
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

