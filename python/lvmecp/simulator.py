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
from pymodbus.server.async_io import ModbusTcpServer

from lvmecp import config


__all__ = ["Simulator", "plc_simulator"]


class Simulator:
    """A modbus simulator for a PLC controller."""

    OVERRIDES: ClassVar[dict[str, int]] = {}

    def __init__(
        self,
        modules: dict,
        address: str = "",
        port: int = 5020,
        overrides={},
    ):

        self.address = address
        self.port = port

        self.modules = deepcopy(modules)

        self.overrides = Simulator.OVERRIDES.copy()
        self.overrides.update(overrides)

        self.current_values: dict[str, list[int]] = {}

        self.context: ModbusServerContext | None = None

        self.reset()
        self.context = ModbusServerContext(self.slave_context, single=True)

        self.server: ModbusTcpServer | None = None
        self.__task: asyncio.Task | None = None

    def reset(self):

        di = {}
        co = {}
        hr = {}
        ir = {}

        for module in self.modules:
            mode = self.modules[module]["mode"]
            for device in self.modules[module]["devices"]:
                register = self.modules[module]["devices"][device]["address"]

                value = self.overrides.get(device, 0)

                if mode == "coil":
                    co[register] = value
                elif mode == "holding_register":
                    hr[register] = value
                elif mode == "discrete_input":
                    di[register] = value
                elif mode == "input_register":
                    ir[register] = value
                else:
                    raise ValueError(f"Invalid mode {mode!r} for device {device!r}.")

                code = 1 if mode == "coil" else 3
                self.current_values[f"{module}.{device}".lower()] = [
                    register,
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

    async def start(self, serve_forever: bool = True, monitor_interval: float = 0.01):
        """Starts the server and the process that monitors changes."""

        self.__task = asyncio.create_task(self._monitor_context(monitor_interval))

        self.server = ModbusTcpServer(
            self.context,
            address=(self.address, self.port),
            allow_reuse_address=True,
        )

        if serve_forever:
            await self.server.serve_forever()
        else:
            if self.server.server is None:
                self.server.server = await self.server.server_factory
                self.server.serving.set_result(True)

    async def stop(self):
        """Stops the simulator."""

        if self.__task:
            self.__task.cancel()
            with suppress(asyncio.CancelledError):
                await self.__task

        self.__task = None

        if self.server and self.server.server:
            self.server.server.close()
            await self.server.server.wait_closed()

    def __del__(self):
        if self.__task:
            self.__task.cancel()

    async def _monitor_context(self, interval: float):
        """Monitor the context."""

        async def set_value(device: str, new_value: int, delay: float = 0):
            if delay > 0:
                await asyncio.sleep(delay)

            status_address, *_ = self.current_values[device]

            context.setValues(code, status_address, [new_value])
            self.current_values[device][2] = new_value

        assert self.context
        context = cast(ModbusSlaveContext, self.context[0])

        while True:
            for device in self.current_values:

                address, code, current_value = self.current_values[device]
                new_value = int(context.getValues(code, address, count=1)[0])

                if new_value == current_value:
                    continue

                self.current_values[device][2] = new_value

                if device.endswith("_new"):
                    # For lights. When we change the value of the XX_new
                    # register the light is switched and XX_status changes value.
                    status_name = device.replace("_new", "_status")
                    asyncio.create_task(set_value(status_name, new_value, 0.0))

                elif device == "emergency.e_stop":
                    if new_value == 1:
                        asyncio.create_task(set_value("emergency.e_status", 1, 0.0))
                        asyncio.create_task(set_value("emergency.e_reset", 0, 0.0))

                elif device == "emergency.e_reset":
                    if new_value == 1:
                        asyncio.create_task(set_value("emergency.e_status", 0, 0.0))
                        asyncio.create_task(set_value("emergency.e_stop", 0, 0.0))

            await asyncio.sleep(interval)


plc_simulator = Simulator(config["plc"]["modules"])
