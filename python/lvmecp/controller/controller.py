#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-03
# @Filename: Controller.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations
from sdsstools.logger import SDSSLogger

import asyncio
import configparser
import os
import socket
import struct
import datetime
import time
import warnings
import json

from pymodbus.client.asynchronous.async_io import (
    AsyncioModbusTcpClient as ModbusClient,
)

from lvmecp.exceptions import LvmecpError, LvmecpWarning


__all__ = ["PlcController", "Module", "Elements"]

class PlcController():
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
        print(modules)
        modules_list = list(modules.keys())
        print(modules_list)
        self.modules = [
            Module(
                name,
                config,
                self.config_get(f"modules.{module}.name"),
                self.config_get(f"modules.{module}.mode"),
                self.config_get(f"modules.{module}.channels"),
                self.config_get(f"modules.{module}.description"),            
            )for module in modules_list
        ]
        print(self.modules)

        self.host = self.config_get("host")
        self.port = self.config_get("port")
        self.addr = {}
        for module in self.modules:
            self.addr[module.name] = module.get_address() 
        print(self.addr)
        self.Client = None          #Modbusclient or client 


    async def start(self, *argv):
        """open the ModbusTCP connection with PLC"""
        # connection
        try:
            self.Client = ModbusClient(self.host, self.port)
            await self.Client.connect()
        except:
            raise LvmecpError(
            f"fail to open connection with {self.host}"
        )

    async def stop(self):
        """close the ModbusTCP connection with PLC"""
        try:
            self.Client.protocol.close()

        except:
            raise LvmecpError(
            f"fail to close connection with {self.host}"
        )

    async def write(self, mode: str, addr: int, data):
        """write the data to devices
        
        parameters
        ------------
        mode
            coil or input_register
        addr
            modbus address
        data
            ON 0xff00
            OFF 0x0000
        """

        try:
            if mode == "coil":
                await self.Client.protocol.write_coil(addr, data)
            elif mode == "input_register":
                await self.Client.protocol.write_register(addr, data)
            else:
                raise LvmecpError(
                    f"{mode} is a wrong value"
                )

        except:
            raise LvmecpError(
                f"fail to write coil to {addr}"
            )

    async def read(self, mode:str, addr:int):
        """read the data from devices
        
        parameters
        ------------
        mode
            coil or input_register
        addr
            modbus address       
        """
        try:
            if mode == "coil":
                reply = await self.Client.protocol.read_coils(addr, 1)
                reply_str = str(reply.bits[0])
                return reply.bits[0]
            elif mode == "input_register":
                reply = await self.Client.protocol.read_holding_registers(addr, 1)
                reply_str = str(reply.registers)                  
                return reply.registers
            else:
                raise LvmecpError(
                    f"{mode} is a wrong value"
                )

        except:
            raise LvmecpError(
                f"fail to read coils to {addr}"
            )

    
    async def send_command(self, device:str, command:str):
        """send command to PLC
        
        Parameters
        -----------
        device
            The devices controlled by lvmecp which are "Dome" and "light"

        command
            move/status
        """
        
        addr_tggl = 236
        addr_light = 336
        addr_enb = 200
        addr_act = 1000
        addr_new = 2000

        await self.start()

        # get the status from the hardware
        try:
            if device == "light":
                reply = await self.read("light", addr_light)
                if command == "move":
                    if reply:
                        await self.write("light", addr_tggl, 0x0000)         #off
                    else:
                        await self.write("light", addr_tggl, 0xff00)         #on
                else:
                    raise LvmecpError(
                        f"{command} is not correct"
                    )

            elif device == "Dome" :
                if command == "move":
                    reply = await self.read("Dome_enb", addr_enb)
                    if reply:
                        dome_position = True
                    else:
                        dome_position = False
                # Dome status is default: False
                    if dome_position:#true
                            #await self.write('Dome_new', addr_new, 0)        # close
                            await self.write("Dome_enb", addr_enb, 0x0000)# disable dome
                    else:#false
                            await self.write("Dome_enb", addr_enb, 0xff00)# Enable dome
                            #await self.write('Dome_new', addr_new, 359)        # open
                else:
                    raise LvmecpError(
                        f"{command} is not correct"
                    )

            else:
                raise LvmecpError(
                    f"{device} is not connected."
                )
         
        except LvmecpError as err:
            warnings.warn(str(err), LvmecpWarning)

        # close the connection
        await self.stop() 

    async def get_status(self, mode:str, addr:int):
        """get the status of the device

                Parameters
        -----------
        device
            The devices controlled by lvmecp which are "Dome" and "light"
        
        """
        
        await self.start()
        status = {}

        addr_light = 336
        addr_enb = 200
        addr_act = 1000

        if mode == "coil":
            #print(device)
            reply = await self.read("coil", addr)
            status = await self.parse(reply) 
        
        elif mode == "input_register":
            reply = await self.read("input_register", addr)
            status = await self.parse(reply)
        
        else:
            raise LvmecpError(
                f"{mode} is not correct"
            )

        # close the connection
        await self.stop()

        return status


    @staticmethod
    def parse(value):
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


class Module():

    def __init__(
        self,
        plcname: str,
        config: [],
        name: str, 
        mode: str, 
        channels: int, 
        description: str,
        *args, 
        **kwargs):

        self.plc = plcname
        self.config = config

        self.name = name
        self.mode = mode
        self.description = description
        self.channels= channels

        self.elements = self.config_get(f"modules.{name}.elements")
        print(self.elements)
        self.elements_list = list(self.elements.keys())
        print(self.elements_list)

    def get_address(self):
        self.addr = {}

        for element in self.elements_list:
            self.addr[element] = self.elements[element]["address"]

        return self.addr

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

