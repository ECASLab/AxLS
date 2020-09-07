`timescale 1ns / 1ps

module CSkipA_16b_tb();
  
  reg [15:0] A;
  reg [15:0] B;
  wire [15:0] S;
  wire Cout;

  reg [15:0] memA [0:999999];
  reg [15:0] memB [0:999999];

  reg [16:0] res;
  
  integer i;
  integer file;

  CSkipA_16b U0(S,Cout,A,B);

  initial begin
    $readmemb("memA.dat", memA);
    $readmemb("memB.dat", memB);
    file = $fopen("output.txt", "w");
    
    A = 0;
    B = 0;
    res = 0;
    #10
    
    for (i = 0; i < 1000000; i = i + 1) begin
      A = memA[i];
      B = memB[i];
      res = memA[i] + memB[i];
      #10
      $fwrite(file, "%d\n",{Cout,S});
/*
      if (res != {Cout,S})
	 $display("ERROR");
*/
    end

    $fclose(file);
    $display("-- Ending simulation --");
    $finish;
  end
endmodule
