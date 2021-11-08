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

    def __init__(self, name: str, host: str, port: int):
        self.name = name
        self.host = host
        self.port = port
        self.wagoClient = None



    async def TCP_sock(self):
        """open TCP socket connection"""
        # connection
        current_time = datetime.datetime.now()
        print(
            f"host: {self.port} before connection   : {current_time}"
            )
        #self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

        self.wagoClient = ModbusClient(self.host, self.port)
        await self.wagoClient.connect()

        current_time = datetime.datetime.now()
        print(
            f"host: {self.port} after connection   : {current_time}"
            )


    #def send tcp packet
    async def TCP_send(self, *argv):
        """Send a command to device"""
        message = None
        if len(argv) == 3:
            # Build message
            message = struct.pack('12B', 0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x00, argv[0], argv[1] >> 8, argv[1] & 0xff, argv[2] >> 8, argv[2] & 0xff)
        elif len(argv) == 1:
            message = argv[0]

        print(f'Send: {message!r}')
        
        # Build MODBUS message
        #command = struct.pack('12B', 0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x00, fc, addr >> 8, addr & 0xff, data >> 8, data & 0xff)
        # command = chr(0x00) + chr(0x00)			              	# Transaction identifier
        # command = command + chr(0x00) + chr(0x00)           	# Protocol identifier (0 = MODBUS)
        # command = command + chr(0x00) + chr(0x06)           	# Message length
        # command = command + chr(0x00)			            	# Unit identifier
        # command = command + chr(fc)				                # Function code
        # command = command + chr(addr >> 8) + chr(addr & 0xFF)  	# Address
        # command = command + chr(data >> 8) + chr(data & 0xFF)   # Data
        
        reg_addr = message + chr(argv[1] >> 8) + chr(argv[1] & 0xFF)  	# Address
        reg_value = len(argv)                                           #register value to write
        
        try:
            current_time = datetime.datetime.now()
            print(
                f"host: {self.port} before write   : {current_time}"
            )     

            await self.wagoClient.write_single_register(reg_addr, reg_value)
            
            current_time = datetime.datetime.now()
            print(
                f"host: {self.port} after write   : {current_time}"
            )                         
        except LvmecpError as msg:
            self.close()
            warnings.warn(str(msg), LvmecpWarning)            

        try:
            current_time = datetime.datetime.now()
            print(
                f"host: {self.port} before read   : {current_time}"
            )             
            reply = await self.wagoClient.read_holding_registers(reg_addr, reg_value)
            print(f"reply: {reply}")
            current_time = datetime.datetime.now()
            print(
                f"host: {self.port} after read   : {current_time}"
            )             
        except LvmecpError as msg:
            self.close()
            warnings.warn(str(msg), LvmecpWarning)   


    async def close(self):
        """close the socket connection with PLC"""
        try:
            print('Close the connection')
            await self.wagoClient.protocol.close()

        except:
            if not self.wagoClient == None:
                print('TCP socket already close')