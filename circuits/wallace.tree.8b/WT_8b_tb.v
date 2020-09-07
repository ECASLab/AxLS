`timescale 1ns / 1ps

module WT_8b_tb();
  
  reg [7:0] A;
  reg [7:0] B;
  wire [15:0] S;

  reg [7:0] memA [0:999999];
  reg [7:0] memB [0:999999];

  reg [16:0] res;
  
  integer i;
  integer file;

  WT_8b U0(S,A,B);

  initial begin
    $readmemb("memA.dat", memA);
    $readmemb("memB.dat", memB);
    file = $fopen("output.txt", "w");
    
    A = 0;
    B = 0;
    res = 0;
    #10
    
    for (i = 0; i < 500000; i = i + 1) begin
      A = memA[i];
      B = memB[i];
      res = memA[i] * memB[i];
      #20
      $fwrite(file, "%d\n",S);
      /*
      if (res != S)
	 $display("ERROR");
      */
    end

    $fclose(file);
    //$display("-- Ending simulation --");
    $finish;
  end
endmodule
