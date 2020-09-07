/*
 * \file RCA_3_0_tb.v 
 * \author Jorge Castro-Godinez <jorge.castro-godinez@kit.edu>
 * Chair for Embedded Systems (CES)
 * Karlsruhe Institute of Technology (KIT), Germany
 * Prof. Dr. Joerg Henkel
 *
 */

`timescale 1ns / 1ps

module RCA_3_0_tb();
  
  wire [4:0] s;
  reg [3:0] a;
  reg [3:0] b;
  reg cin;
  
  reg [3:0] memA [0:999999];
  reg [3:0] memB [0:999999];
  
  integer i,file;

  RCA_3_0 U0(a,b,cin,s);

  initial begin

    $display("-- Begining Simulation --");
    $readmemb("memA.dat", memA);
    $readmemb("memB.dat", memB);
    file = $fopen("output.txt","w");
    
    a = 0;
    b = 0;
    cin = 0;
    #10
    
    for (i = 0; i < 500000; i = i + 1) begin
      a = memA[i];
      b = memB[i];
      #10
      $fwrite(file,"%d\n",s);
    end

    $fclose(file);
    $display("-- Ending simulation --");
    $finish;
  end
endmodule
