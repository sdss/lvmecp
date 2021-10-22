#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-03
# @Filename: testcontroller.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import os
import socket
import struct
import datetime as dt
import time

class TestController():
    """Talks to an Plc simulator controller over TCP/IP."""

    def __init__(self, name: str, host: str, port: int) -> None:
        # Define the class variables
        self.name = name
        self.host = host
        self.port = port
        self.log_time = None    # Log timestamp
        self.file = None        # Filename
        self.DMsocket = None    # PLC UDP socket (Do more Logger)
        self.Tcpaddr = None     # PLC modbus tcp ip and port
        self.TcpSock = None     # PLC TCP socket

    # Define class close command
    def close(self):
        try:
            self.TcpSock.close()
        except:
            if not self.TcpSock == None:
                print('TCP socket already close')
        try:
            self.DMsocket.close()
        except:
            if not self.DMsocket == None:
                print('DMlogger socket already close')

    #Start logging file to a data subfolder
    def start_logging(self):
        self.log_time = dt.datetime.now(tz=dt.timezone.utc)
        if not os.path.isdir('./data'):
            os.mkdir('./data/')
        self.file = open(self.log_time.strftime('./data/C100_%Y-%m-%d_%H.%M.%S_lvdt.csv'), 'w+')
        return 'File ready for logging'

    #Define DMLogger (Do-more logging feature UDP based)
    def DMLogger(self):
        #Create DMSocket
        self.DMsocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #Create UDP socket
        self.DMsocket.bind(('', 0x7272)) #define listening port
        return 'DMLogger ready for listening'

    #Define PLC TCP/IP pair
    def TCP_add(self, ip, port):
        self.Tcpaddr = (ip, port)

    #Define TCP socket
    def TCP_sock(self):
        self.TCPSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCPSock.settimeout(7)
        try:
            self.TCPSock.connect(self.Tcpaddr)
        except socket.error as msg:
            print("Message", msg)
            R1 = ''

    #Define when to automaticaly change file
    def change_file(self, time):
        if self.log_time.hour >= 12 and (time-self.log_time).total_seconds() >= 12*60*60: #Change log file at noon UTC
        #if ((time-self.log_time).total_seconds()) > 60:
            self.file.close()
            self.file = open(time.strftime('./data/C100_%Y-%m-%d_%H.%M.%S_lvdt.csv'), 'w+')
            self.log_time = time

    #Define float read method for DMLogger
    def read_DMLogger(self):
        data = self.DMsocket.recvfrom(512)
        data = struct.unpack(''.join('f' for i in range(int(len(data[0])/4))), data[0]) #unpack the byte array as n float numbers
        return data

    #def send tcp packet
    def TCP_send(self, *argv):
        message = None
        if len(argv) == 3:
            # Build message
            message = struct.pack('12B', 0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x00, argv[0], argv[1] >> 8, argv[1] & 0xff, argv[2] >> 8, argv[2] & 0xff)
        elif len(argv) == 1:
            message = argv[0]
        
        # Build MODBUS message
        #command = struct.pack('12B', 0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x00, fc, addr >> 8, addr & 0xff, data >> 8, data & 0xff)
        # command = chr(0x00) + chr(0x00)			              	# Transaction identifier
        # command = command + chr(0x00) + chr(0x00)           	# Protocol identifier (0 = MODBUS)
        # command = command + chr(0x00) + chr(0x06)           	# Message length
        # command = command + chr(0x00)			            	# Unit identifier
        # command = command + chr(fc)				                # Function code
        # command = command + chr(addr >> 8) + chr(addr & 0xFF)  	# Address
        # command = command + chr(data >> 8) + chr(data & 0xFF)   # Data

        
        try:
            self.TCPSock.send(message)
        except socket.error as msg:
            print ("Message", msg)
        time.sleep(0.001)
        try:
            R1 = self.TCPSock.recv(128)
        except socket.error as msg:

            print ("Message", msg)
            R1 = ''
        #self.TCPSock.close()
        return R1.hex()

    def DMLogger_close(self):
        self.DMsocket.close()

    def file_close(self):
        self.file.close()
