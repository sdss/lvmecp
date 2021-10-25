#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-03
# @Filename: pcs.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import sys
import asyncio
from .controller import PlcController
from .plc_var_test import *                    # Import plc variables

class PCS():
    """PLC Control Software"""
    def __init__(self):
        #self.name = name
        #self.host = host
        #self.port = port

        self.PLC = dict()                           # PLC dictionary
        #self.PLC['PLC'] = PlcController(name=self.name, host=self.host,port=self.port)
        self.PLC['PLC'] = PlcController(name="simulator", host="163.180.145.123",port=502)

        #Define all plc variables from ./var/plc_var.py
        for element in plc_var_list:            # Append to dictionary every plc readable variable in plc_var
            self.PLC[element] = None            # Initialize variable with none
        
        #Define DCS var
        self.DCS = dict()
        self.DCS['Dome_is_mov'] = False         # Dome is moving

    async def open(self):
        """open TCP socket connection with PLCs"""
        await self.PLC['PLC'].TCP_sock()

    async def close(self):
        """close TCP socket connection with PLCs"""
        await self.PLC['PLC'].close()              # Close plc socket


#Define PCS commands                                                                                                    # Issue exit status to python
    #High lights
    async def HL_ON(self):
        """Turn on/off the light"""
        await self.PLC['PLC'].TCP_send(plc_var_talk['Tggl_lights'][0], plc_var_talk['Tggl_lights'][1], 0xff00)

    async def HL_OFF(self):
        """Turn on/off the light"""
        await self.PLC['PLC'].TCP_send(plc_var_talk['Tggl_lights'][0], plc_var_talk['Tggl_lights'][1], 0x0000)
    
    #High light status
    async def HL_stat(self):
        """return the status of lights"""
        out = dict()
        for element in self.PLC:
            if 'LIGHTS' in element.upper():                                                                             # If lights is in key
                out[element]=self.PLC[element]                                                                           # Print lights status elements 
        return out

    #Define dome enable
    async def Dome_enb(self):
        await self.PLC['PLC'].TCP_send(plc_var_talk['Dome_enb_mov'][0], plc_var_talk['Dome_enb_mov'][1], 0xff00)              # Enable dome
    #Define dome disable
    async def Dome_dis(self):
        await self.PLC['PLC'].TCP_send(plc_var_talk['Dome_enb_mov'][0], plc_var_talk['Dome_enb_mov'][1], 0x0000)              # Disable move
    #Define dome status
    async def Dome_stat(self):
        out = dict()
        for element in self.PLC:
            if 'DOME' in element.upper():                                                                               # If Dome is in key
                out[element] = self.PLC[element]                                                                        # Print dome status elements 
        for element in self.DCS:
            if 'DOME' in element.upper():                                                                               # If Dome is in key
                 out[element] = self.DCS[element]                                                                       # Print dome status elements
        return out

    #Define move dome to specific bar code location
    def Dome_move(self,new_pos):
        self.Dome_enb()                                                                                                 # Enable move
        self.PLC['PLC'].TCP_send(plc_var_talk['Dome_new_pos'][0], plc_var_talk['Dome_new_pos'][1], new_pos)             # Send new position to PLC
        self.DCS['Dome_is_mov'] = True                                                                                  # Set dom is moving bit to true 

    #Define platform position
    def Platform_stat(self):                                                                                            # Shows if platform is down
        return f"Platform not down: {not self.PLC['plat_not_dwn']}"

    #Define Windscreen enable
    def Screen_enb(self):
        self.PLC['PLC'].TCP_send(plc_var_talk['WS_enable'][0],plc_var_talk['WS_enable'][1],0xff00)                      # Send WS enable bit (1) to PLC

    #Define Windscreen disable
    def Screen_dis(self):
        self.PLC['PLC'].TCP_send(plc_var_talk['WS_enable'][0],plc_var_talk['WS_enable'][1],0x0000)                     # Send WS disable bit (0) to PLC
        self.PLC['PLC'].TCP_send(plc_var_talk['WS_to_top'][0],plc_var_talk['WS_to_top'][1],0x0000)
        self.PLC['PLC'].TCP_send(plc_var_talk['WS_to_btm'][0],plc_var_talk['WS_to_btm'][1],0x0000)

    #Define Windscreen to upper position
    def Screen_up(self):
        self.Screen_enb()                                                                                               # Send WS enable to PLC
        self.PLC['PLC'].TCP_send(plc_var_talk['WS_to_top'][0],plc_var_talk['WS_to_top'][1],0xff00)                      # Send WS to upper position

    #Define Windscreen to lower position
    def Screen_down(self):
        self.Screen_enb()                                                                                               # Send WS enable to PLC
        self.PLC['PLC'].TCP_send(plc_var_talk['WS_to_btm'][0],plc_var_talk['WS_to_btm'][1],0xff00)                      # Send WS to lower position
    
    #Define Screen status
    def Screen_stat(self):
        out = dict()
        for element in self.PLC:
            if 'WS' in element.upper():                                                                                 # If Dome is in var key
                out[element] = self.PLC[element]                                                                        # Add element to key
        return out

    #Define Shutter enable
    def Shutter_enb(self):
        self.PLC['PLC'].TCP_send(plc_var_talk['Shut_enable'][0],plc_var_talk['Shut_enable'][1],0xff00)                  # Send 1 to shutter enable bit

    #Define Shutter disable
    def Shutter_dis(self):
        self.PLC['PLC'].TCP_send(plc_var_talk['Shut_enable'][0],plc_var_talk['Shut_enable'][1],0x0000)                  # Send 0 to shutter enable bit
    
    #Define Shutter open
    def Shutter_open(self):
        self.Shutter_enb()                                                                                              # Send shutter enable
        self.PLC['PLC'].TCP_send(plc_var_talk['Shut_open'][0],plc_var_talk['Shut_open'][1],0xff00)                      # Send shutter open

    #Define Shutter open
    def Shutter_close(self):
        self.Shutter_enb()                                                                                              # Send shutter enable
        self.PLC['PLC'].TCP_send(plc_var_talk['Shut_close'][0],plc_var_talk['Shut_close'][1],0xff00)                    # Send shutter close

    #Define Shutter status
    def Shutter_status(self):
        out = dict()
        for element in self.PLC:
            if 'Shut' in element.upper():                                                                               # If shut is in var key
                out[element] = self.PLC[element]                                                                        # Add element to key
        return out                                                                                                      # return parameters

    #Define DCS update
    def DCS_update(self):
        # Update status variables
        for element in plc_var_list:                                                                            # Cycle through every variable in plc_var_list
            try:
                data = self.PLC['PLC'].TCP_send(plc_var_list[element][0], plc_var_list[element][1], 0x01)       # Query PLC for a value
            except:
                print ('Error Quering ' + element)
                data = ''
                continue
            if plc_var_list[element][0] == 0x01 and len(data) == 20 and data[:18] == '000000000004000101':      # Case getting a correct answer from a coil query
                try:
                    self.PLC[element] = bool(int(data[-2:]))                                                    # Last to bytes from package are the answer
                except ValueError as msg:
                    print ('Error parsing data from '+ element,msg)
            elif plc_var_list[element][0] == 0x03 and len(data) == 22 and data[:18] == '000000000005000302':    # Case getting a correct answer from a holding register
                try:
                    self.PLC[element] = int(data[-4:],16)                                                       # Last 4 bytes from package are the answer
                except ValueError as msg:
                    print ('Error parsing data from '+ element,msg)                                             # Print error if something goes wrong
            else:
                print('Error reading '+ element)                                                                # Print reading error if something goes wrong
        #Disable DCS dome control if movement finished
        if self.PLC['Dome_in_pos'] and self.DCS['Dome_is_mov']:                                                 # If Dome just reached position
            self.Dome_dis()                                                                                     # Disable move
            self.DCS['Dome_is_mov'] = False                                                                     # Dome isn't moving anymore
        #Disable DCS Screen control if movement finished
        # if (self.PLC['WS_position']>= 5370 or self.PLC['WS_position']== 512) and self.PLC['WS_enable']:         # If screen in position
        #     self.Screen_dis()                                                                                   # Disable screen
        #     self.PLC['PLC'].TCP_send(plc_var_talk['WS_to_top'][0],plc_var_talk['WS_to_top'][1],0x0000)          # Disable lower bit
        #     self.PLC['PLC'].TCP_send(plc_var_talk['WS_to_btm'][0],plc_var_talk['WS_to_btm'][1],0x0000)          # Disable upper bit
