`timescale 1ns / 1ps

module [[TOPMODULE]]_tb();

  wire [16:0] s;
  reg [15:0] a;
  reg [15:0] b;

  integer i;

  [[TOPMODULE]] U0(s,a,b);

  initial begin

    $display("-- Begining Simulation --");
    $dumpfile("prune.vcd");
    $dumpvars(2,[[TOPMODULE]]_tb);

    a = 0;
    b = 0;
    #10

    for (i = 0; i < 17; i = i + 1) begin
      a = (a << 1) + 1;
      b = (b << 1) + 1;
      #10;
    end

    $display("-- Ending simulation --");
    $finish;
  end
endmodule
