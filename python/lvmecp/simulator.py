#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-24
# @Filename: simulator.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
from contextlib import suppress
from copy import deepcopy

from typing import ClassVar, cast

from pymodbus.datastore import (
    ModbusServerContext,
    ModbusSlaveContext,
    ModbusSparseDataBlock,
)
from pymodbus.server import ServerAsyncStop, StartAsyncTcpServer

from lvmecp import config


__all__ = ["Simulator", "plc_simulator"]


class Simulator:
    """A modbus simulator for a PLC controller."""

    OVERRIDES: ClassVar[dict[str, int]] = {}

    def __init__(
        self,
        registers: dict,
        address: str = "127.0.0.1",
        port: int = 5020,
        overrides={},
    ):
        self.address = address
        self.port = port

        self.registers = deepcopy(registers)

        self.overrides = Simulator.OVERRIDES.copy()
        self.overrides.update(overrides)

        self.current_values: dict[str, list[int]] = {}

        self.context: ModbusServerContext | None = None
        self.slave_context: ModbusSlaveContext

        self.reset()
        self.context = ModbusServerContext(self.slave_context, single=True)

        self.__task: asyncio.Task | None = None

    def reset(self):
        di = {}
        co = {}
        hr = {}
        ir = {}

        for register in self.registers:
            mode = self.registers[register].get("mode", "coil")
            address = self.registers[register]["address"]
            value = self.overrides.get(register, 0)

            if mode == "coil":
                co[address] = value
            elif mode == "holding_register":
                hr[address] = value
            elif mode == "discrete_input":
                di[address] = value
            elif mode == "input_register":
                ir[address] = value
            else:
                raise ValueError(f"Invalid mode {mode!r} for register {register!r}.")

            code = 1 if mode == "coil" else 3
            self.current_values[register.lower()] = [
                address,
                code,
                value,
            ]

        self.slave_context = ModbusSlaveContext(
            di=ModbusSparseDataBlock(di),
            co=ModbusSparseDataBlock(co),
            hr=ModbusSparseDataBlock(hr),
            ir=ModbusSparseDataBlock(ir),
            zero_mode=True,
        )

        if self.context is not None:
            self.context[0] = self.slave_context

    async def start(self, monitor_interval: float = 0.01):
        """Starts the process that monitors changes and serves forever."""

        self.__task = asyncio.create_task(self._monitor_context(monitor_interval))

        await StartAsyncTcpServer(
            self.context,
            address=(self.address, self.port),
        )

    async def stop(self):
        """Stops the simulator."""

        await ServerAsyncStop()

        if self.__task:
            self.__task.cancel()
            with suppress(asyncio.CancelledError):
                await self.__task

        self.__task = None

    def __del__(self):
        if self.__task:
            self.__task.cancel()

    async def _monitor_context(self, interval: float):
        """Monitor the context."""

        async def set_value(register: str, new_value: int, delay: float = 0):
            if delay > 0:
                await asyncio.sleep(delay)

            address, code, current_value = self.current_values[register]

            context.setValues(code, address, [new_value])
            self.current_values[register][2] = new_value

        assert self.context
        context = cast(ModbusSlaveContext, self.context[0])

        while True:
            for register in self.current_values:
                address, code, current_value = self.current_values[register]
                new_value = int(context.getValues(code, address, count=1)[0])

                if new_value == current_value:
                    continue

                self.current_values[register][2] = new_value

                if register.endswith("_new"):
                    # For lights. When we change the value of the XX_new
                    # register the light is switched and XX_status changes value.
                    status_name = register.replace("_new", "_status")
                    asyncio.create_task(set_value(status_name, new_value, 0.0))

                elif register == "e_stop":
                    if new_value == 1:
                        asyncio.create_task(set_value("e_status", 1, 0.0))
                        asyncio.create_task(set_value("e_reset", 0, 0.0))

                elif register == "e_reset":
                    if new_value == 1:
                        asyncio.create_task(set_value("e_status", 0, 0.0))
                        asyncio.create_task(set_value("e_stop", 0, 0.0))

            await asyncio.sleep(interval)


plc_simulator = Simulator(config["modbus"]["registers"])
