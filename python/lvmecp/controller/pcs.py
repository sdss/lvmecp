#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-03
# @Filename: pcs.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from .controller import PlcController, TestController
from plc_var_test import *   # Import plc variables

class pcs():
    """PLC Control Software"""
    def __init__(self):
        self.controller = TestController
        self.controller.TCP_add('127.0.0.1',502)
        self.controller.TCP_sock()
        
        #Define all plc variables from ./var/plc_var.py
        for element in plc_var_list:            # Append to dictionary every plc readable variable in plc_var
            self.PLC[element] = None            # Initialize variable with none
        
        #Define DCS var
        self.DCS = dict()
        self.DCS['Dome_is_mov'] = False         # Dome is moving