#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-03
# @Filename: ControllerBase.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

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


__all__ = ["PlcController", "Module"]

class PlcController():
    """Talks to an Plc controller over TCP/IP.

    Parameters
    ----------
    name
        A name identifying this controller.
    host
        The hostname of the Plc.
    port
        The port on which the Plc listens to incoming connections.
    """
    def __init__(self, name: str, host: str, port: int, module: dict[str, Module]):
        self.name = name
        self.host = host
        self.port = port
        self.module = module

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

        module = self.module
        devices = module.devices
        elements = module.elements
        addr = module.get_address()

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
    async def parse(value):
        """Parse the input data for ON/OFF."""
        if value in ["off", "OFF", "0", 0, False]:
            return "OFF"
        if value in ["on", "ON", "1", 1, True]:
            return "ON"
        return -1


class Module():
    """get the information of the LVM Enclosure Elements from config."""
    
    def __init__(
        self, 
        name: str, 
        mode: str, 
        channels: int, 
        description: str,
        devices: dict, 
        *args, 
        **kwargs):
        
        self.name = name
        self.mode = mode
        self.channels = channels
        self.description = description
        self.devices = devices
        self.elements = self.devices.keys()

    async def get_address(self):
        self.addr = {}

        for element in self.elements:
            self.addr[element] = self.device[element]["address"]

        return self.addr
