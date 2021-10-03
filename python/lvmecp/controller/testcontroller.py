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

    def __init__(self) -> None:
        self.DMsocket = None
        self.Tcpaddr = None     # PLC modbus tcp ip and port
        self.TcpSock = None     # PLC TCP socket

    def close(self):
        self.DMsocket.close()

    #Define DMLogger (Do-more logging feature UDP based)
    def DMLogger(self):
        #Create DMSocket
        self.DMsocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #Create UDP socket
        self.DMsocket.bind(('', 0x7272)) #define listening port
        return 'DMLogger ready for listening'
    
    #Define float read method for DMLogger
    def read_DMLogger(self):
        data = self.DMsocket.recvfrom(512)
        data = struct.unpack(''.join('f' for i in range(int(len(data[0])/4))), data[0]) #unpack the byte array as n float numbers
        return data

    def DMLogger_close(self):
        self.DMsocket.close()

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

        #def send tcp packet
    def TCP_send(self, *argv):
        message = None
        if len(argv) == 3:
            # Build message
            message = struct.pack('12B', 0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x00, argv[0], argv[1] >> 8, argv[1] & 0xff, argv[2] >> 8, argv[2] & 0xff)
        elif len(argv) == 1:
            message = argv[0]
        
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