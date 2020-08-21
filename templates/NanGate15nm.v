// 
// ******************************************************************************
// *                                                                            *
// *                   Copyright (C) 2004-2014, Nangate Inc.                    *
// *                           All rights reserved.                             *
// *                                                                            *
// * Nangate and the Nangate logo are trademarks of Nangate Inc.                *
// *                                                                            *
// * All trademarks, logos, software marks, and trade names (collectively the   *
// * "Marks") in this program are proprietary to Nangate or other respective    *
// * owners that have granted Nangate the right and license to use such Marks.  *
// * You are not permitted to use the Marks without the prior written consent   *
// * of Nangate or such third party that may own the Marks.                     *
// *                                                                            *
// * This file has been provided pursuant to a License Agreement containing     *
// * restrictions on its use. This file contains valuable trade secrets and     *
// * proprietary information of Nangate Inc., and is protected by U.S. and      *
// * international laws and/or treaties.                                        *
// *                                                                            *
// * The copyright notice(s) in this file does not indicate actual or intended  *
// * publication of this file.                                                  *
// *                                                                            *
// *    NGLibraryCharacterizer, Development_version_64 - build 201405281900     *
// *                                                                            *
// ******************************************************************************
// 
// * Default delays
//   * comb. path delay        : 0.1
//   * seq. path delay         : 0.1
//   * delay cells             : 0.1
//   * timing checks           : 0.1
// 
// * NTC Setup
//   * Export NTC sections     : true
//   * Combine setup / hold    : true
//   * Combine recovery/removal: true
// 
// * Extras
//   * Export `celldefine      : false
//   * Export `timescale       : -
// 
`timescale 1ns/10ps
module AND2_X1 (A1, A2, Z);
  input A1;
  input A2;
  output Z;

  and(Z, A1, A2);
endmodule

module AND2_X2 (A1, A2, Z);
  input A1;
  input A2;
  output Z;

  and(Z, A1, A2);
endmodule

module AND3_X1 (A1, A2, A3, Z);
  input A1;
  input A2;
  input A3;
  output Z;

  and(Z, i_12, A3);
  and(i_12, A1, A2);
endmodule

module AND3_X2 (A1, A2, A3, Z);
  input A1;
  input A2;
  input A3;
  output Z;

  and(Z, i_18, A3);
  and(i_18, A1, A2);
endmodule

module AND4_X1 (A1, A2, A3, A4, Z);
  input A1;
  input A2;
  input A3;
  input A4;
  output Z;

  and(Z, i_0, A4);
  and(i_0, i_1, A3);
  and(i_1, A1, A2);
endmodule

module AND4_X2 (A1, A2, A3, A4, Z);
  input A1;
  input A2;
  input A3;
  input A4;
  output Z;

  and(Z, i_0, A4);
  and(i_0, i_1, A3);
  and(i_1, A1, A2);
endmodule

module ANTENNA (I);
  input I;

endmodule

module AOI21_X1 (A1, A2, B, ZN);
  input A1;
  input A2;
  input B;
  output ZN;

  not(ZN, i_18);
  or(i_18, i_19, B);
  and(i_19, A1, A2);
endmodule

module AOI21_X2 (A1, A2, B, ZN);
  input A1;
  input A2;
  input B;
  output ZN;

  not(ZN, i_12);
  or(i_12, i_13, B);
  and(i_13, A1, A2);
endmodule

module AOI22_X1 (A1, A2, B1, B2, ZN);
  input A1;
  input A2;
  input B1;
  input B2;
  output ZN;

  not(ZN, i_0);
  or(i_0, i_1, i_2);
  and(i_1, A1, A2);
  and(i_2, B1, B2);
endmodule

module AOI22_X2 (A1, A2, B1, B2, ZN);
  input A1;
  input A2;
  input B1;
  input B2;
  output ZN;

  not(ZN, i_0);
  or(i_0, i_1, i_2);
  and(i_1, A1, A2);
  and(i_2, B1, B2);
endmodule

module BUF_X1 (I, Z);
  input I;
  output Z;

  buf(Z, I);
endmodule

module BUF_X2 (I, Z);
  input I;
  output Z;

  buf(Z, I);
endmodule

module BUF_X4 (I, Z);
  input I;
  output Z;

  buf(Z, I);
endmodule

module BUF_X8 (I, Z);
  input I;
  output Z;

  buf(Z, I);
endmodule

module BUF_X12 (I, Z);
  input I;
  output Z;

  buf(Z, I);
endmodule

module BUF_X16 (I, Z);
  input I;
  output Z;

  buf(Z, I);
endmodule

module CLKBUF_X1 (I, Z);
  input I;
  output Z;

  buf(Z, I);
endmodule

module CLKBUF_X2 (I, Z);
  input I;
  output Z;

  buf(Z, I);
endmodule

module CLKBUF_X4 (I, Z);
  input I;
  output Z;

  buf(Z, I);
endmodule

module CLKBUF_X8 (I, Z);
  input I;
  output Z;

  buf(Z, I);
endmodule

module CLKBUF_X12 (I, Z);
  input I;
  output Z;

  buf(Z, I);
endmodule

module CLKBUF_X16 (I, Z);
  input I;
  output Z;

  buf(Z, I);
endmodule

primitive \seq_CLKGATETST_X1  (QD, CLK, nextstate, NOTIFIER);
  output QD;
  input CLK;
  input nextstate;
  input NOTIFIER;
  reg QD;

  table
      // CLK   nextstate    NOTIFIER     : @QD :          QD
           0           0           ?       : ? :           0;
           0           1           ?       : ? :           1;
           1           ?           ?       : ? :           -; // Ignore non-triggering clock edge
           ?           *           ?       : ? :           -; // Ignore all edges on nextstate
           ?           ?           *       : ? :           x; // Any NOTIFIER change
  endtable
endprimitive

module CLKGATETST_X1 (CLK, E, TE, Q);
  input CLK;
  input E;
  input TE;
  output Q;
  reg NOTIFIER;

    and(Q, CLK, QD);
    \seq_CLKGATETST_X1 (QD, CLK, nextstate, NOTIFIER);
    not(QDn, QD);
    or(nextstate, E, TE);
endmodule

primitive \seq_DFFRNQ_X1  (IQ, RN, nextstate, CLK, NOTIFIER);
  output IQ;
  input RN;
  input nextstate;
  input CLK;
  input NOTIFIER;
  reg IQ;

  table
       // RN   nextstate         CLK    NOTIFIER     : @IQ :          IQ
           ?           0           r           ?       : ? :           0;
           1           1           r           ?       : ? :           1;
           ?           0           *           ?       : 0 :           0; // reduce pessimism
           1           1           *           ?       : 1 :           1; // reduce pessimism
           1           *           ?           ?       : ? :           -; // Ignore all edges on nextstate
           1           ?           n           ?       : ? :           -; // Ignore non-triggering clock edge
           0           ?           ?           ?       : ? :           0; // RN activated
           *           ?           ?           ?       : 0 :           0; // Cover all transitions on RN
           ?           ?           ?           *       : ? :           x; // Any NOTIFIER change
  endtable
endprimitive

module DFFRNQ_X1 (D, RN, CLK, Q);
  input D;
  input RN;
  input CLK;
  output Q;
  reg NOTIFIER;

    \seq_DFFRNQ_X1 (IQ, RN, nextstate, CLK, NOTIFIER);
    not(IQN, IQ);
    buf(Q, IQ);
    buf(nextstate, D);
endmodule

primitive \seq_DFFSNQ_X1  (IQ, SN, nextstate, CLK, NOTIFIER);
  output IQ;
  input SN;
  input nextstate;
  input CLK;
  input NOTIFIER;
  reg IQ;

  table
       // SN   nextstate         CLK    NOTIFIER     : @IQ :          IQ
           1           0           r           ?       : ? :           0;
           ?           1           r           ?       : ? :           1;
           1           0           *           ?       : 0 :           0; // reduce pessimism
           ?           1           *           ?       : 1 :           1; // reduce pessimism
           1           *           ?           ?       : ? :           -; // Ignore all edges on nextstate
           1           ?           n           ?       : ? :           -; // Ignore non-triggering clock edge
           0           ?           ?           ?       : ? :           1; // SN activated
           *           ?           ?           ?       : 1 :           1; // Cover all transitions on SN
           ?           ?           ?           *       : ? :           x; // Any NOTIFIER change
  endtable
endprimitive

module DFFSNQ_X1 (D, SN, CLK, Q);
  input D;
  input SN;
  input CLK;
  output Q;
  reg NOTIFIER;

    \seq_DFFSNQ_X1 (IQ, SN, nextstate, CLK, NOTIFIER);
    not(IQN, IQ);
    buf(Q, IQ);
    buf(nextstate, D);
endmodule

module FA_X1 (A, B, CI, CO, S);
  input A;
  input B;
  input CI;
  output CO;
  output S;

  or(CO, i_12, i_15);
  or(i_12, i_13, i_14);
  and(i_13, B, CI);
  and(i_14, B, A);
  and(i_15, CI, A);
  not(S, i_20);
  or(i_20, i_21, i_27);
  and(i_21, i_22, A);
  not(i_22, i_23);
  or(i_23, i_24, i_25);
  and(i_24, B, CI);
  not(i_25, i_26);
  or(i_26, B, CI);
  not(i_27, i_28);
  or(i_28, i_29, A);
  not(i_29, i_30);
  or(i_30, i_31, i_32);
  and(i_31, B, CI);
  not(i_32, i_33);
  or(i_33, B, CI);
endmodule

module FILLTIE ();

endmodule

module FILL_X1 ();

endmodule

module FILL_X2 ();

endmodule

module FILL_X4 ();

endmodule

module FILL_X8 ();

endmodule

module FILL_X16 ();

endmodule

module HA_X1 (A, B, CO, S);
  input A;
  input B;
  output CO;
  output S;

  and(CO, A, B);
  not(S, i_42);
  or(i_42, i_43, i_44);
  and(i_43, A, B);
  not(i_44, i_45);
  or(i_45, A, B);
endmodule

module INV_X1 (I, ZN);
  input I;
  output ZN;

  not(ZN, I);
endmodule

module INV_X2 (I, ZN);
  input I;
  output ZN;

  not(ZN, I);
endmodule

module INV_X4 (I, ZN);
  input I;
  output ZN;

  not(ZN, I);
endmodule

module INV_X8 (I, ZN);
  input I;
  output ZN;

  not(ZN, I);
endmodule

module INV_X12 (I, ZN);
  input I;
  output ZN;

  not(ZN, I);
endmodule

module INV_X16 (I, ZN);
  input I;
  output ZN;

  not(ZN, I);
endmodule

primitive \seq_LHQ_X1  (IQ, nextstate, E, NOTIFIER);
  output IQ;
  input nextstate;
  input E;
  input NOTIFIER;
  reg IQ;

  table
// nextstate           E    NOTIFIER     : @IQ :          IQ
           0           1           ?       : ? :           0;
           1           1           ?       : ? :           1;
           *           ?           ?       : ? :           -; // Ignore all edges on nextstate
           ?           0           ?       : ? :           -; // Ignore non-triggering clock edge
           ?           ?           *       : ? :           x; // Any NOTIFIER change
  endtable
endprimitive

module LHQ_X1 (D, E, Q);
  input D;
  input E;
  output Q;
  reg NOTIFIER;

    \seq_LHQ_X1 (IQ, nextstate, E, NOTIFIER);
    not(IQN, IQ);
    buf(Q, IQ);
    buf(nextstate, D);
endmodule

module MUX2_X1 (I0, I1, S, Z);
  input I0;
  input I1;
  input S;
  output Z;

  or(Z, i_12, i_13);
  and(i_12, S, I1);
  and(i_13, i_14, I0);
  not(i_14, S);
endmodule

module NAND2_X1 (A1, A2, ZN);
  input A1;
  input A2;
  output ZN;

  not(ZN, i_24);
  and(i_24, A1, A2);
endmodule

module NAND2_X2 (A1, A2, ZN);
  input A1;
  input A2;
  output ZN;

  not(ZN, i_18);
  and(i_18, A1, A2);
endmodule

module NAND3_X1 (A1, A2, A3, ZN);
  input A1;
  input A2;
  input A3;
  output ZN;

  not(ZN, i_6);
  and(i_6, i_7, A3);
  and(i_7, A1, A2);
endmodule

module NAND3_X2 (A1, A2, A3, ZN);
  input A1;
  input A2;
  input A3;
  output ZN;

  not(ZN, i_6);
  and(i_6, i_7, A3);
  and(i_7, A1, A2);
endmodule

module NAND4_X1 (A1, A2, A3, A4, ZN);
  input A1;
  input A2;
  input A3;
  input A4;
  output ZN;

  not(ZN, i_0);
  and(i_0, i_1, A4);
  and(i_1, i_2, A3);
  and(i_2, A1, A2);
endmodule

module NAND4_X2 (A1, A2, A3, A4, ZN);
  input A1;
  input A2;
  input A3;
  input A4;
  output ZN;

  not(ZN, i_0);
  and(i_0, i_1, A4);
  and(i_1, i_2, A3);
  and(i_2, A1, A2);
endmodule

module NOR2_X1 (A1, A2, ZN);
  input A1;
  input A2;
  output ZN;

  not(ZN, i_12);
  or(i_12, A1, A2);
endmodule

module NOR2_X2 (A1, A2, ZN);
  input A1;
  input A2;
  output ZN;

  not(ZN, i_12);
  or(i_12, A1, A2);
endmodule

module NOR3_X1 (A1, A2, A3, ZN);
  input A1;
  input A2;
  input A3;
  output ZN;

  not(ZN, i_0);
  or(i_0, i_1, A3);
  or(i_1, A1, A2);
endmodule

module NOR3_X2 (A1, A2, A3, ZN);
  input A1;
  input A2;
  input A3;
  output ZN;

  not(ZN, i_0);
  or(i_0, i_1, A3);
  or(i_1, A1, A2);
endmodule

module NOR4_X1 (A1, A2, A3, A4, ZN);
  input A1;
  input A2;
  input A3;
  input A4;
  output ZN;

  not(ZN, i_0);
  or(i_0, i_1, A4);
  or(i_1, i_2, A3);
  or(i_2, A1, A2);
endmodule

module NOR4_X2 (A1, A2, A3, A4, ZN);
  input A1;
  input A2;
  input A3;
  input A4;
  output ZN;

  not(ZN, i_0);
  or(i_0, i_1, A4);
  or(i_1, i_2, A3);
  or(i_2, A1, A2);
endmodule

module OAI21_X1 (A1, A2, B, ZN);
  input A1;
  input A2;
  input B;
  output ZN;

  not(ZN, i_0);
  and(i_0, i_1, B);
  or(i_1, A1, A2);
endmodule

module OAI21_X2 (A1, A2, B, ZN);
  input A1;
  input A2;
  input B;
  output ZN;

  not(ZN, i_0);
  and(i_0, i_1, B);
  or(i_1, A1, A2);
endmodule

module OAI22_X1 (A1, A2, B1, B2, ZN);
  input A1;
  input A2;
  input B1;
  input B2;
  output ZN;

  not(ZN, i_0);
  and(i_0, i_1, i_2);
  or(i_1, A1, A2);
  or(i_2, B1, B2);
endmodule

module OAI22_X2 (A1, A2, B1, B2, ZN);
  input A1;
  input A2;
  input B1;
  input B2;
  output ZN;

  not(ZN, i_0);
  and(i_0, i_1, i_2);
  or(i_1, A1, A2);
  or(i_2, B1, B2);
endmodule

module OR2_X1 (A1, A2, Z);
  input A1;
  input A2;
  output Z;

  or(Z, A1, A2);
endmodule

module OR2_X2 (A1, A2, Z);
  input A1;
  input A2;
  output Z;

  or(Z, A1, A2);
endmodule

module OR3_X1 (A1, A2, A3, Z);
  input A1;
  input A2;
  input A3;
  output Z;

  or(Z, i_0, A3);
  or(i_0, A1, A2);
endmodule

module OR3_X2 (A1, A2, A3, Z);
  input A1;
  input A2;
  input A3;
  output Z;

  or(Z, i_0, A3);
  or(i_0, A1, A2);
endmodule

module OR4_X1 (A1, A2, A3, A4, Z);
  input A1;
  input A2;
  input A3;
  input A4;
  output Z;

  or(Z, i_0, A4);
  or(i_0, i_1, A3);
  or(i_1, A1, A2);
endmodule

module OR4_X2 (A1, A2, A3, A4, Z);
  input A1;
  input A2;
  input A3;
  input A4;
  output Z;

  or(Z, i_0, A4);
  or(i_0, i_1, A3);
  or(i_1, A1, A2);
endmodule

primitive \seq_SDFFRNQ_X1  (IQ, RN, nextstate, CLK, NOTIFIER);
  output IQ;
  input RN;
  input nextstate;
  input CLK;
  input NOTIFIER;
  reg IQ;

  table
       // RN   nextstate         CLK    NOTIFIER     : @IQ :          IQ
           ?           0           r           ?       : ? :           0;
           1           1           r           ?       : ? :           1;
           ?           0           *           ?       : 0 :           0; // reduce pessimism
           1           1           *           ?       : 1 :           1; // reduce pessimism
           1           *           ?           ?       : ? :           -; // Ignore all edges on nextstate
           1           ?           n           ?       : ? :           -; // Ignore non-triggering clock edge
           0           ?           ?           ?       : ? :           0; // RN activated
           *           ?           ?           ?       : 0 :           0; // Cover all transitions on RN
           ?           ?           ?           *       : ? :           x; // Any NOTIFIER change
  endtable
endprimitive

module SDFFRNQ_X1 (D, RN, SE, SI, CLK, Q);
  input D;
  input RN;
  input SE;
  input SI;
  input CLK;
  output Q;
  reg NOTIFIER;

    \seq_SDFFRNQ_X1 (IQ, RN, nextstate, CLK, NOTIFIER);
    not(IQN, IQ);
    buf(Q, IQ);
    or(nextstate, i_0, i_1);
    and(i_0, SE, SI);
    and(i_1, i_2, D);
    not(i_2, SE);
endmodule

primitive \seq_SDFFSNQ_X1  (IQ, SN, nextstate, CLK, NOTIFIER);
  output IQ;
  input SN;
  input nextstate;
  input CLK;
  input NOTIFIER;
  reg IQ;

  table
       // SN   nextstate         CLK    NOTIFIER     : @IQ :          IQ
           1           0           r           ?       : ? :           0;
           ?           1           r           ?       : ? :           1;
           1           0           *           ?       : 0 :           0; // reduce pessimism
           ?           1           *           ?       : 1 :           1; // reduce pessimism
           1           *           ?           ?       : ? :           -; // Ignore all edges on nextstate
           1           ?           n           ?       : ? :           -; // Ignore non-triggering clock edge
           0           ?           ?           ?       : ? :           1; // SN activated
           *           ?           ?           ?       : 1 :           1; // Cover all transitions on SN
           ?           ?           ?           *       : ? :           x; // Any NOTIFIER change
  endtable
endprimitive

module SDFFSNQ_X1 (D, SE, SI, SN, CLK, Q);
  input D;
  input SE;
  input SI;
  input SN;
  input CLK;
  output Q;
  reg NOTIFIER;

    \seq_SDFFSNQ_X1 (IQ, SN, nextstate, CLK, NOTIFIER);
    not(IQN, IQ);
    buf(Q, IQ);
    or(nextstate, i_0, i_1);
    and(i_0, SE, SI);
    and(i_1, i_2, D);
    not(i_2, SE);
endmodule

module TBUF_X1 (EN, I, Z);
  input EN;
  input I;
  output Z;

  bufif0(Z, Z_in, Z_enable);
  not(Z_enable, EN);
  buf(Z_in, I);
endmodule

module TBUF_X2 (EN, I, Z);
  input EN;
  input I;
  output Z;

  bufif0(Z, Z_in, Z_enable);
  not(Z_enable, EN);
  buf(Z_in, I);
endmodule

module TBUF_X4 (EN, I, Z);
  input EN;
  input I;
  output Z;

  bufif0(Z, Z_in, Z_enable);
  not(Z_enable, EN);
  buf(Z_in, I);
endmodule

module TBUF_X8 (EN, I, Z);
  input EN;
  input I;
  output Z;

  bufif0(Z, Z_in, Z_enable);
  not(Z_enable, EN);
  buf(Z_in, I);
endmodule

module TBUF_X12 (EN, I, Z);
  input EN;
  input I;
  output Z;

  bufif0(Z, Z_in, Z_enable);
  not(Z_enable, EN);
  buf(Z_in, I);
endmodule

module TBUF_X16 (EN, I, Z);
  input EN;
  input I;
  output Z;

  bufif0(Z, Z_in, Z_enable);
  not(Z_enable, EN);
  buf(Z_in, I);
endmodule

module TIEH (Z);
  output Z;

  buf(Z, 1);
endmodule

module TIEL (ZN);
  output ZN;

  buf(ZN, 0);
endmodule

module XNOR2_X1 (A1, A2, ZN);
  input A1;
  input A2;
  output ZN;

  not(ZN, i_18);
  not(i_18, i_19);
  or(i_19, i_20, i_21);
  and(i_20, A1, A2);
  not(i_21, i_22);
  or(i_22, A1, A2);
endmodule

module XOR2_X1 (A1, A2, Z);
  input A1;
  input A2;
  output Z;

  not(Z, i_18);
  or(i_18, i_19, i_20);
  and(i_19, A1, A2);
  not(i_20, i_21);
  or(i_21, A1, A2);
endmodule

`ifdef TETRAMAX
`else
  primitive ng_xbuf (o, i, d);
	output o;
	input i, d;
	table
	// i   d   : o
	   0   1   : 0 ;
	   1   1   : 1 ;
	   x   1   : 1 ;
	endtable
  endprimitive
`endif
//
// End of file
//
