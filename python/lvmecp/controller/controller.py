#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-03
# @Filename: controller.py
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

from pymodbus.client.asynchronous.async_io import (
    AsyncioModbusTcpClient as ModbusClient,
)

from lvmecp.exceptions import LvmecpError, LvmecpWarning


__all__ = ["PlcController"]


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
    def __init__(self, name: str, host: str, port: int, ):
        self.name = name
        self.host = host
        self.port = port

        self.wagoClient = None


    async def start(self, *argv):
        """open the socket connection with PLC"""
        # connection
        try:
            self.wagoClient = ModbusClient(self.host, self.port)
            await self.wagoClient.connect()
        except:
            raise LvmecpError(
            f"fail to open connection with {self.host}"
        )

    async def stop(self):
        """close the socket connection with PLC"""
        try:
            self.wagoClient.protocol.close()

        except:
            raise LvmecpError(
            f"fail to close connection with {self.host}"
        )

    async def write(self, addr, data):
        """write the data to devices"""
        try:
            await self.wagoClient.protocol.write_coil(addr, data)
        except:
            raise LvmecpError(
                f"fail to write coil to {addr}"
            )

    async def read(self, addr):
        """read the data from devices"""
        try:
            reply = await self.wagoClient.protocol.read_coils(addr, 1)
        except:
            raise LvmecpError(
                f"fail to read coils to {addr}"
            )

        return reply.bits[0]

    
    async def send_command(self, device, command):
        """send command to PLC
        
        Parameters
        -----------
        device
            The devices controlled by lvmecp which are "Dome" and "light"

        command
            move/status
        """
        
        addr_tggl = 236
        addr_low = 336
        addr_high = 337
        addr_dome = 200

        await self.start()

        # get the status from the hardware
        try:
            if device == "light":
                reply_low = await self.read(addr_low)
                reply_high = await self.read(addr_high)
                if command == "move":
                    if reply_high == False and reply_low == False:
                        await self.write(addr_tggl, 0xff00)
                    elif reply_high == True and reply_low == True:
                        await self.write(addr_tggl, 0x0000)
                    elif reply_high == None and reply_low == None:
                        raise LvmecpError(
                            f"The lights return {reply_low} and {reply_high}"
                        )
                else:
                    raise LvmecpError(
                        f"{command} is not correct"
                    )

            elif device == "Dome" :
                reply = await self.read(addr_dome)
                if command == "move":
                    if reply == False:
                        await self.write(addr_dome, 0xff00)              # Enable dome
                    elif reply == True:
                        await self.write(addr_dome, 0x0000)              # Disable move
                    elif reply == None:
                        raise LvmecpError(
                            f"The Dome return {reply}"
                        )
                else:
                    raise LvmecpError(
                        f"{command} is not correct"
                    )
         
            else:
                raise LvmecpError(
                    f"{device} is not correct."
                )
        except LvmecpError as err:
            warnings.warn(str(err), LvmecpWarning)

        # close the connection
        await self.stop() 

    async def get_status(self, device):
        """get the status of the device"""
        
        await self.start()
        status = {}

        addr_low = 336
        addr_high = 337
        addr_dome = 200

        if device == "light":
            reply_low = await self.read(addr_low)
            reply_high = await self.read(addr_high)
            status["high_light"] = reply_high
            status["low_light"] = reply_low
            print(status) 

        elif device == "Dome":
            reply = await self.read(addr_dome)
            status["Dome"] = reply
            print(status)

        # close the connection
        await self.stop() 

        return status
