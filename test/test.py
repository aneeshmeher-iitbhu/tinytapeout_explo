# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

@cocotb.test()
async def test_traffic_light(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initialize signals
    dut.ena.value = 1  # REQUIRED: Enable the module
    dut.rst_n.value = 0
    dut.ui_in.value = 0  # C sensor is at ui_in[0]

    # Reset sequence
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Helper function to extract light states
    def get_light_states():
        farm_light = dut.uo_out.value & 0b00000111  # uo_out[2:0]
        highway_light = (dut.uo_out.value >> 3) & 0b00000111  # uo_out[5:3]
        return farm_light, highway_light

    # Test initial state (HGRE_FRED)
    await RisingEdge(dut.clk)
    farm_light, highway_light = get_light_states()
    assert highway_light == 0b001, f"Highway should be Green (001), but got {highway_light:03b}"
    assert farm_light == 0b100, f"Farm should be Red (100), but got {farm_light:03b}"

    # Test sensor activation after 10 cycles
    dut.ui_in.value = 0b00000001  # Set C (ui_in[0]) to 1
    # await ClockCycles(dut.clk, 10)
    await RisingEdge(dut.clk)
    # Verify transition to HYEL_FRED (Highway Yellow)
    farm_light, highway_light = get_light_states()
    assert highway_light == 0b010, f"Highway should be Yellow (010), but got {highway_light:03b}"

    # Wait 3 cycles for HYEL_FRED -> HRED_FGRE transition
    await ClockCycles(dut.clk, 3)
    farm_light, highway_light = get_light_states()
    assert highway_light == 0b100, f"Highway should be Red (100), but got {highway_light:03b}"
    assert farm_light == 0b001, f"Farm should be Green (001), but got {farm_light:03b}"

    # Wait 10 cycles for HRED_FGRE -> HRED_FYEL transition
    await ClockCycles(dut.clk, 10)
    farm_light, highway_light = get_light_states()
    assert farm_light == 0b010, f"Farm should be Yellow (010), but got {farm_light:03b}"

    # Wait 3 cycles for HRED_FYEL -> HGRE_FRED transition
    await ClockCycles(dut.clk, 3)
    farm_light, highway_light = get_light_states()
    assert highway_light == 0b001, f"Highway should return to Green (001), but got {highway_light:03b}"
    assert farm_light == 0b100, f"Farm should return to Red (100), but got {farm_light:03b}"

    dut._log.info("Test completed successfully")
