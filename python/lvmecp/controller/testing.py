#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2022-04-02
# @Filename: testing.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

"""
isort:skip_file
"""

from __future__ import annotations

import sys
import pytest

from unittest.mock import Mock
from pymodbus.client.asynchronous.async_io import AsyncioModbusTcpClient as ModbusClient
from sdsstools.logger import SDSSLogger

from lvmecp.controller.controller import PlcController
from lvmecp.exceptions import LvmecpTestControllerError

if sys.version_info.major < 3:
    raise ValueError("Python 2 is not supported.")
if sys.version_info.minor <= 7:
    from asyncmock import AsyncMock
else:
    from unittest.mock import AsyncMock

__all__ = ["TestPlcController"]


class TestPlcController(PlcController):
    """an Test Plc Controller. Mock PlcController for unit test.

    Parameters
    ----------
    name
        A name identifying this controller.
    config
        The configuration defined on the .yaml file under /etc/lvmecp.yml
    log
        The logger for logging
    """

    def __init___(self, name: str, config: [], log: SDSSLogger):

        super().__init__(name, config, log)

        self.host = "localhost"
        # self.port = unused_tcp_port_factory()
        self.Client = ModbusClient(self.host, self.port)

    async def start(self):
        """Make a mock connection"""

        self.Client.connect = AsyncMock()
        self.call = 0
        self.estop_call = 0

    async def stop(self):
        """Close a mock connection"""

        self.Client.close = AsyncMock()

    async def read(self, estop=None):
        """Set mock replies from PLC"""

        if estop:
            return self.estop_call
        else:
            return self.call

    async def write(self, estop=None):
        """Set mock replies from PLC"""

        # call = self.call

        if estop:
            if self.estop_call == 1:
                self.estop_call = 0
            elif self.estop_call == 0:
                self.estop_call = 1
            return self.estop_call
        else:
            if self.call == 1:
                self.call = 0
            elif self.call == 0:
                self.call = 1
            return self.call

    async def send_command(self, module: str, element: str, command: str):
        """send command to PLC

        Parameters
        -----------
        module
            The devices controlled by lvmecp
            which are "interlocks", "light", "shutter" and "emergengy".

        element
            The elements contained by the module

        command
            on/off/status/trigger
        """

        self.result = {}

        # module "interlocks" -> 0
        if module == "interlocks":
            elements = self.modules[0].get_element()
            if element in elements:
                if command == "status":
                    self.result[element] = await self.read(estop=True)
                elif command == "trigger":
                    self.result[element] = await self.write(estop=True)

        # module "lights" -> 1
        # 0x0000  off
        # 0xff00  on

        if module == "lights":
            elements = self.modules[1].get_element()
            if command == "status":
                if element in elements:
                    self.result[element] = await self.read()
                elif element == "all":
                    for element in elements:
                        self.result[element] = await self.read()
            elif command == "on":
                if element in elements:
                    self.result[element] = await self.write()
            elif command == "off":
                if element in elements:
                    self.result[element] = await self.write()

        # module "dome" -> 2, 3
        if module == "shutter1":
            elements = self.modules[2].get_element()
            if command == "status":
                if element in elements:
                    self.result[element] = await self.read()
                elif element == "all":
                    for element in elements:
                        self.result[element] = await self.read()
            elif command == "on":
                for element in elements:
                    self.result[element] = await self.write()
            elif command == "off":
                for element in elements:
                    self.result[element] = await self.write()

        # module "hvac" -> 0
        if module == "hvac":
            if command == "status":
                elements = self.modules[0].get_element()
                if element in elements:
                    self.result[element] = await self.read()
                    self.result["unit"] = self.unit[module][element]
                elif element == "all":
                    for element in elements:
                        see = {}
                        see["value"] = await self.read()
                        see["unit"] = self.unit[module][element]
                        self.result[element] = see

        print(f"----------------{self.result}--------------------------")
        return self.result
