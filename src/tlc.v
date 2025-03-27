/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_tlc(   
  input wire [7:0] ui_in,
  output wire [7:0] uo_out,
  input wire [7:0] uio_in,
  output wire [7:0] uio_out,
  output wire [7:0] uio_oe
  input clk,
  input ena,
  input rst_n
);
  
  wire C = ui_in[0];
  reg light_farm = uo_out[0];
  reg light_highway = uo_out[1];

    // State encoding
    parameter HGRE_FRED = 2'b00,  // Highway Green/Farm Red
              HYEL_FRED = 2'b01,  // Highway Yellow/Farm Red
              HRED_FGRE = 2'b10,  // Highway Red/Farm Green
              HRED_FYEL = 2'b11;  // Highway Red/Farm Yellow

    reg [1:0] state, next_state;
  reg [3:0] counter;
    reg delay_10s, delay_3s;

    // State transition logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= HGRE_FRED;
            counter <= 0;
        end else begin
            state <= next_state;
          counter <= (counter >= 4'd13) ? 0 : counter + 1;
        end
    end

   // Timing control
    always @(posedge clk) begin
      delay_10s <= (counter == 4'd13);  
      delay_3s  <= (counter == 4'd3);  
    end

    // FSM combinational logic
    always @(*) begin
        case(state)
            HGRE_FRED: begin
                light_highway = 3'b001;
                light_farm = 3'b100;
                next_state = C ? HYEL_FRED : HGRE_FRED;
            end
            HYEL_FRED: begin
                light_highway = 3'b010;
                light_farm = 3'b100;
                next_state = (delay_3s) ? HRED_FGRE : HYEL_FRED;
            end
            HRED_FGRE: begin
                light_highway = 3'b100;
                light_farm = 3'b001;
                next_state = (delay_10s) ? HRED_FYEL : HRED_FGRE;
            end
            HRED_FYEL: begin
                light_highway = 3'b100;
                light_farm = 3'b010;
                next_state = (delay_3s) ? HGRE_FRED : HRED_FYEL;
            end
        endcase
    end
     
endmodule
