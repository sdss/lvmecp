# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-05
# @Filename: light.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


from __future__ import absolute_import, annotations, division, print_function

import asyncio
import datetime
from os import name

from clu.command import Command

#from lvmecp.controller.testcontroller import TestController
from lvmecp.controller.controller import PlcController
from lvmecp.controller.pcs import PCS
from lvmecp.exceptions import LvmecpError

from . import parser


__all__ = ["light"]

plc = PCS()

async def plc_control(command, controllers: dict[str, PlcController]):
    plcs = []
    for controller in controllers:
        plcs.append(PCS(name=controller[name], host=controller["host"], port=controller["port"]))

    return plcs

@parser.group()
def light(*args):
    """control enclosure lights."""

    pass

@light.command()
async def on(command: Command, controllers: dict[str, PlcController]):
    """on or off the enclosure light"""
    command.info(text="move the light")
    
    for controller in controllers:
        #plc = PCS(name=controller[0], host=controller[1], port=controller[2])
        #assume one plc host in the enclosure
        try:
            await plc.open()
            await plc.HL_ON()
            await plc.close()
        except LvmecpError as err:
            return command.error(str(err))
    return command.finish()

@light.command()
async def off(command: Command, controllers: dict[str, PlcController]):
    """on or off the enclosure light"""
    command.info(text="move the light")
    
    for controller in controllers:
        #plc = PCS(name=controller[0], host=controller[1], port=controller[2])
        #assume one plc host in the enclosure
        try:
            await plc.open()
            await plc.HL_OFF()
            await plc.close()
        except LvmecpError as err:
            return command.error(str(err))
    return command.finish()

@light.command()
def status(command: Command, controllers: dict[str, PlcController]):
    """return the status of light"""
   # plc = PCS(name=controllers[name], host=controllers["host"], port=controllers["port"])

    #command.info(text="what status the light is")
    #status = {}
    #status['STATUS'] = plc.HL_stat()
    #command.info(text = status)

    #return command.finish()