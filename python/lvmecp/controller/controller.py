#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-03
# @Filename: Controller.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

"""
isort:skip_file
"""

from __future__ import annotations

import datetime
import warnings

from pymodbus.client.asynchronous.async_io import AsyncioModbusTcpClient as ModbusClient

from sdsstools.logger import SDSSLogger

from lvmecp.exceptions import LvmecpControllerError, LvmecpControllerWarning


__all__ = ["PlcController", "Module"]


class PlcController:
    """Talks to an Plc controller over TCP/IP.

    Parameters
    ----------
    name
        A name identifying this controller.
    config
        The configuration defined on the .yaml file under /etc/lvmecp.yml
    log
        The logger for logging
    """

    def __init__(self, name: str, config: [], log: SDSSLogger):
        self.name = name
        self.log = log
        self.config = config

        modules = self.config_get("modules")
        modules_list = list(modules.keys())
        self.modules = [
            Module(
                name,
                config,
                self.config_get(f"modules.{module}.name"),
                self.config_get(f"modules.{module}.mode"),
                self.config_get(f"modules.{module}.channels"),
                self.config_get(f"modules.{module}.description"),
            )
            for module in modules_list
        ]

        self.host = self.config_get("host")
        self.port = self.config_get("port")
        self.addr = {}
        self.unit = {}
        for module in self.modules:
            self.addr[module.name] = module.get_address()
            if module.name == "hvac":
                self.unit[module.name] = module.get_unit()
        #print(self.addr)
        #self.Client = None

    async def start(self, *argv):
        """open the ModbusTCP connection with PLC"""
        # connection
        self.Client = None
        try:
            self.Client = ModbusClient(self.host, self.port)
            await self.Client.connect()
        except LvmecpControllerError:
            print(f"fail to open connection with {self.host}")

    async def stop(self):
        """close the ModbusTCP connection with PLC"""
        try:
            assert self.Client
            self.Client.protocol.close()

        except LvmecpControllerError:
            print(f"fail to close connection with {self.host}")

    async def write(self, mode: str, addr: int, data):
        """write the data to devices

        parameters
        ------------
        mode
            coil or holding_registers
        addr
            modbus address
        data
            ON 0xFF00
            OFF 0x0000
        """

        try:
            if mode == "coil":
                assert self.Client
                await self.Client.protocol.write_coil(addr, data)
            elif mode == "holding_registers":
                await self.Client.protocol.write_register(addr, data)
            else:
                raise LvmecpControllerError(f"{mode} is a wrong value")

        except LvmecpControllerError:
            print(f"fail to write coil to {addr}")

    async def read(self, mode: str, addr: int):
        """read the data from devices

        parameters
        ------------
        mode
            coil or holding_registers
        addr
            modbus address
        """

        try:
            if mode == "coil":
                assert self.Client
                assert self.Client.protocol
                reply = await self.Client.protocol.read_coils(addr, 1)
                if reply:
                    return reply.bits[0]
                else:
                    raise LvmecpControllerError("read_coils returns a wrong value")
            elif mode == "holding_registers":
                assert self.Client
                assert self.Client.protocol
                reply = await self.Client.protocol.read_holding_registers(addr, 1)
                if reply:
                    return reply.registers[0]
                else:
                    raise LvmecpControllerError("read_holding_registers returns a wrong value")
            else:
                raise LvmecpControllerError(f"{mode} is a wrong value")

        except LvmecpControllerError:
            print(f"fail to read coils to {addr}")

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
            move/status
        """

        self.result = {}

        try:
            # module "interlocks" -> 0
            if module == "interlocks":
                elements = self.modules[0].get_element()
                if element in elements:
                    if command == "status":
                        self.result[element] = await self.get_status(
                            self.modules[0].mode, self.addr[module][element]
                        )
                    elif command == "trigger":
                        await self.write(
                            self.modules[0].mode, self.addr[module][element], 0xFF00
                        )
                    else:
                        raise LvmecpControllerError(f"{command} is not correct")
                else:
                    raise LvmecpControllerError(f"{element} is not correct")

            # module "lights" -> 1
            # 0x0000  off
            # 0xff00  on

            if module == "lights":
                elements = self.modules[1].get_element()
                if command == "status":
                    if element in elements:
                        self.result[element] = await self.get_status(
                            self.modules[1].mode, self.addr[module][element]
                        )
                    elif element == "all":
                        for element in elements:
                            self.result[element] = await self.get_status(
                                self.modules[1].mode, self.addr[module][element]
                            )
                    else:
                        raise LvmecpControllerError(f"{element} is not correct")
                elif command == "on":
                    if element in elements:
                        await self.write(
                            self.modules[1].mode, self.addr[module][element], 0xFF00
                        )
                    else:
                        raise LvmecpControllerError(f"{element} is not correct")
                elif command == "off":
                    if element in elements:
                        await self.write(
                            self.modules[1].mode, self.addr[module][element], 0x0000
                        )
                    else:
                        raise LvmecpControllerError(f"{element} is not correct")
                else:
                    raise LvmecpControllerError(f"{command} is not correct")

            # module "dome" -> 2, 3
            if module == "shutter1":
                elements = self.modules[2].get_element()
                if command == "status":
                    if element in elements:
                        self.result[element] = await self.get_status(
                            self.modules[2].mode, self.addr[module][element]
                        )
                    elif element == "all":
                        for element in elements:
                            self.result[element] = await self.get_status(
                                self.modules[2].mode, self.addr[module][element]
                            )
                    else:
                        raise LvmecpControllerError(f"{element} is not correct")
                elif command == "on":
                    if element in elements:
                        await self.write(
                            self.modules[2].mode, self.addr[module][element], 0xFF00
                        )
                    elif element == "all":
                        for element in elements:
                            await self.write(
                                self.modules[2].mode, self.addr[module][element], 0xFF00
                            )
                    else:
                        raise LvmecpControllerError(f"{element} is not correct")
                elif command == "off":
                    if element in elements:
                        await self.write(
                            self.modules[2].mode, self.addr[module][element], 0x0000
                        )
                    elif element == "all":
                        for element in elements:
                            await self.write(
                                self.modules[2].mode, self.addr[module][element], 0x0000
                            )
                    else:
                        raise LvmecpControllerError(f"{element} is not correct")
                else:
                    raise LvmecpControllerError(f"{command} is not correct")

            if module == "shutter2":
                elements = self.modules[3].get_element()
                if command == "status":
                    if element in elements:
                        self.result[element] = await self.get_status(
                            self.modules[3].mode, self.addr[module][element]
                        )
                    elif element == "all":
                        for element in elements:
                            self.result[element] = await self.get_status(
                                self.modules[3].mode, self.addr[module][element]
                            )
                    else:
                        raise LvmecpControllerError(f"{element} is not correct")
                elif command == "on":
                    if element in elements:
                        await self.write(
                            self.modules[3].mode, self.addr[module][element], 0xFF00
                        )
                    elif element == "all":
                        for element in elements:
                            await self.write(
                                self.modules[3].mode, self.addr[module][element], 0xFF00
                            )
                    else:
                        raise LvmecpControllerError(f"{element} is not correct")
                elif command == "off":
                    if element in elements:
                        await self.write(
                            self.modules[3].mode, self.addr[module][element], 0x0000
                        )
                    elif element == "all":
                        for element in elements:
                            await self.write(
                                self.modules[3].mode, self.addr[module][element], 0x0000
                            )
                    else:
                        raise LvmecpControllerError(f"{element} is not correct")
                else:
                    raise LvmecpControllerError(f"{command} is not correct")

            # module "emergengy_stop" -> 4
            if module == "emergency":
                if element == "0":
                    if command == "status":
                        elements = self.modules[4].get_element()
                        for element in elements:
                            self.result[element] = await self.get_status(
                                self.modules[3].mode, self.addr[module][element]
                            )
                    else:
                        raise LvmecpControllerError(f"{command} is not correct")
                else:
                    raise LvmecpControllerError(f"{element} is not correct")

            # module "hvac" -> 0
            if module == "hvac":
                if command == "status":
                    elements = self.modules[0].get_element()
                    if element in elements:
                        self.result[element] = await self.get_status(
                            self.modules[0].mode, self.addr[module][element]
                        )
                        self.result["unit"] = self.unit[module][element]
                    elif element == "all":
                        for element in elements:
                            see = {}
                            see["value"] = await self.get_status(
                                self.modules[0].mode, self.addr[module][element]
                            )
                            see["unit"] = self.unit[module][element]
                            self.result[element] = see
                    else:
                        raise LvmecpControllerError(f"{element} is not correct")
                else:
                    raise LvmecpControllerError(f"{command} is not correct")

            return self.result

        except LvmecpControllerError as err:
            warnings.warn(str(err), LvmecpControllerWarning)

    async def get_status(self, mode: str, addr: int):
        """get the status of the device

        parameters
        ------------
        mode
            coil or holding_registers
        addr
            modbus address
        """

        if mode == "coil":
            reply = await self.read("coil", addr)
            status = await self.parse(reply)

        elif mode == "holding_registers":
            reply = await self.read("holding_registers", addr)
            status = reply

        else:
            raise LvmecpControllerError(f"{mode} is not correct")

        return status

    @staticmethod
    async def parse(value):
        """Parse the input data for ON/OFF."""
        if value in ["off", "OFF", "0", 0, False]:
            return 0
        if value in ["on", "ON", "1", 1, True]:
            return 1
        return -1

    def config_get(self, key, default=None):
        """Read the configuration and extract the data as a structure that we want.
        Notice: DOESNT work for keys with dots !!!

        Parameters
        ----------
        key
            The tree structure as a string to extract the data.
            For example, if the configuration structure is

            ports;
                1;
                    desc; "Hg-Ar spectral callibration lamp"

            You can input the key as
            "ports.1.desc" to take the information "Hg-Ar spectral callibration lamp"
        """

        def g(config, key, d=None):
            """Internal function for parsing the key from the configuration.

            Parameters
            ----------
            config
                config from the class member, which is saved from the class instance
            key
                The tree structure as a string to extract the data.
                For example, if the configuration structure is

                ports:
                    num:1
                    1:
                        desc: "Hg-Ar spectral callibration lamp"

                You can input the key as
                "ports.1.desc" to take the information "Hg-Ar spectral callibration lamp"
            """
            k = key.split(".", maxsplit=1)
            c = config.get(
                k[0] if not k[0].isnumeric() else int(k[0])
            )  # keys can be numeric
            return (
                d
                if c is None
                else c
                if len(k) < 2
                else g(c, k[1], d)
                if type(c) is dict
                else d
            )

        return g(self.config, key, default)


class Module:
    def __init__(
        self,
        plcname: str,
        config: [],
        name: str,
        mode: str,
        channels: int,
        description: str,
        *args,
        **kwargs,
    ):

        self.plc = plcname
        self.config = config

        self.name = name
        self.mode = mode
        self.description = description
        self.channels = channels

    def get_address(self):
        """return a dictionary about modbus address of each element in module."""

        addr = {}

        elements = self.config_get(f"modules.{self.name}.elements")
        elements_list = list(elements.keys())

        try:
            for element in elements_list:
                addr[element] = elements[element]["address"]
        except LvmecpControllerError:
            print("You cannot get addresses.")

        return addr

    def get_unit(self):
        """return a dictionary about units of each element in module."""

        unit = {}

        elements = self.config_get(f"modules.{self.name}.elements")
        elements_list = list(elements.keys())

        try:
            for element in elements_list:
                unit[element] = elements[element]["units"]
        except LvmecpControllerError:
            print("You cannot get units.")

        return unit

    def get_element(self):
        """return a list of elements in module."""

        elements = self.config_get(f"modules.{self.name}.elements")
        elements_list = list(elements.keys())

        return elements_list

    def config_get(self, key, default=None):
        """Read the configuration and extract the data as a structure that we want.
        Notice: DOESNT work for keys with dots !!!

        Parameters
        ----------
        key
            The tree structure as a string to extract the data.
            For example, if the configuration structure is

            ports;
                1;
                    desc; "Hg-Ar spectral callibration lamp"

            You can input the key as
            "ports.1.desc" to take the information "Hg-Ar spectral callibration lamp"
        """

        def g(config, key, d=None):
            """Internal function for parsing the key from the configuration.

            Parameters
            ----------
            config
                config from the class member, which is saved from the class instance
            key
                The tree structure as a string to extract the data.
                For example, if the configuration structure is

                ports:
                    num:1
                    1:
                        desc: "Hg-Ar spectral callibration lamp"

                You can input the key as
                "ports.1.desc" to take the information "Hg-Ar spectral callibration lamp"
            """
            k = key.split(".", maxsplit=1)
            c = config.get(
                k[0] if not k[0].isnumeric() else int(k[0])
            )  # keys can be numeric
            return (
                d
                if c is None
                else c
                if len(k) < 2
                else g(c, k[1], d)
                if type(c) is dict
                else d
            )

        return g(self.config, key, default)
