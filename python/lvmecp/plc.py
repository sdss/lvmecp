#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-24
# @Filename: plc.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from drift import Drift

from .dome import DomeController
from .lights import LightsController


class PLC(Drift):
    """Class for the enclosure programmable logic controller."""

    def __init__(self, address: str, port: int = 502):

        super().__init__(address, port)

        self.lights = LightsController(self)
        self.dome = DomeController(self)

    async def read_all_registers(self):
        """Reads all the connected devices/registers and returns a dictionary."""

        devices = []
        for module in self.modules:
            for device in self[module].devices:
                devices.append(f"{module}.{device}")

        values = await self.read_devices(devices, adapt=False)

        registers = {}
        for ii in range(len(devices)):
            registers[devices[ii].lower()] = values[ii]

        return registers
