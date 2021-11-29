# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-05
# @Filename: lock.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


from __future__ import absolute_import, annotations, division, print_function

import asyncio
import datetime
from os import name
from typing import Text
import click
import json

from clu.command import Command
from lvmecp.controller.controller import PlcController
from lvmecp.exceptions import LvmecpError

from . import parser


__all__ = ["monitor"]

@parser.command()
async def monitor(command: Command, controllers: dict[str, PlcController]):
    """return the status of HVAC system, air purge system and emergency stop.
    
    ECP should monitor the pressure in air purge system and the 
    temperature in each room. Also, ECP should start the emergency stop
    if the pressure changed outside normal range. 
    
    """

    command.info(text="monitoring ... ")
    current_status = {}

    try:
        #current_status["interlocks"] = await controllers[0].send_command("interlocks","0","status")
        current_status["emergengy"] = await controllers[0].send_command(
            "emergengy",
            "0", 
            "status"
        )
        current_status["hvac"] = await controllers[1].send_command(
            "hvac",
            "0", 
            "status"
        )

    except LvmecpError as err:
            return command.fail(str(err))

    command.info(status=current_status)
    return command.finish()

