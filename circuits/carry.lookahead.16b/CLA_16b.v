
module LCU(
  input [3:0] BP,
  input [3:0] BG,
  input Cin,
  output [3:0] C
);

  assign C[0] = BG[0] |  (BP[0] & Cin);
  assign C[1] = BG[1] |  (BP[1] & C[0]);
  assign C[2] = BG[2] |  (BP[2] & C[1]);
  assign C[3] = BG[3] |  (BP[3] & C[2]);

endmodule


module CLA_4b(
  output [3:0] S,
  output Cout, PG, GG,
  input [3:0] A, B,
  input Cin
);

  wire [3:0] G,P,C;
  
  assign G = A & B; //Generate
  assign P = A ^ B; //Propagate

  assign C[0] = Cin;
  assign C[1] = G[0] | (P[0] & C[0]);
  assign C[2] = G[1] | (P[1] & G[0]) | (P[1] & P[0] & C[0]);
  assign C[3] = G[2] | (P[2] & G[1]) | (P[2] & P[1] & G[0]) | (P[2] & P[1] & P[0] & C[0]);

  assign Cout = G[3] | (P[3] & G[2]) | (P[3] & P[2] & G[1]) | (P[3] & P[2] & P[1] & G[0]) |(P[3] & P[2] & P[1] & P[0] & C[0]);
  assign S = P ^ C;

  assign PG = P[3] & P[2] & P[1] & P[0]; // block generate
  assign GG = G[3] | (P[3] & G[2]) | (P[3] & P[2] & G[1]) | (P[3] & P[2] & P[1] & G[0]); // block propagate

endmodule

module CLA_16b(
  output [15:0] S,
  output Cout,
  input [15:0] A, B,
  input Cin
);

  wire [3:0] BP, BG;
  wire [3:0] C;

  LCU inCarries (BP, BG, Cin, C);

  CLA_4b cla0(S[3:0], C[0], BP[0], BG[0], A[3:0], B[3:0], Cin);
  CLA_4b cla1(S[7:4], C[1], BP[1], BG[1], A[7:4], B[7:4], C[0]);
  CLA_4b cla2(S[11:8], C[2], BP[2], BG[2], A[11:8], B[11:8], C[1]);
  CLA_4b cla3(S[15:12], C[3], BP[3], BG[3], A[15:12], B[15:12], C[2]);

  assign Cout = C[3];

endmodule
