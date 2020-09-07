`timescale 1ns / 1ps

module UBKSA_15_0_15_0_tb();

  wire [16:0] s;
  reg [15:0] a;
  reg [15:0] b;

  reg [15:0] memA [0:999999];
  reg [15:0] memB [0:999999];

  integer i,file;

  UBKSA_15_0_15_0 U0(s,a,b);

  initial begin

    //$display("-- Begining Simulation --");
    /*
    $dumpfile("./test.vcd");
    $dumpvars(0,UBKSA_15_0_15_0_tb);
    */
    $readmemb("memA.dat", memA);
    $readmemb("memB.dat", memB);
    file = $fopen("output.txt","w");

    a = 0;
    b = 0;
    #10

    for (i = 0; i < 500000; i = i + 1) begin
      a = memA[i];
      b = memB[i];
      #10
      $fwrite(file,"%d\n",s);
    end

    $fclose(file);
    //$display("-- Ending simulation --");
    $finish;
  end
endmodule
