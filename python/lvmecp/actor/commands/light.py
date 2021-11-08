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
import click

from clu.command import Command
from lvmecp.controller.controller import PlcController
from lvmecp.exceptions import LvmecpError

from . import parser


__all__ = ["light"]

@parser.group()
def light():
    """tasks for lights"""

    pass

@light.command()
@click.argument("ROOM", type=str, required=False)
async def on(
    command: Command, controllers: dict[str, PlcController], room: str
    ):
    """on or off the enclosure light"""

    tasks = []
    #current_status = await controllers["simulator"].HL_status()
    command.info(text="on the light")

    try:
        await controllers["simulator"].send_command("light", "on")
        #if current_status['Low_lights'] == False or current_status['High_lights'] == False:
        #    await controllers["simulator"].send_command("light", "on")
        #elif current_status['Low_lights'] == True or current_status['High_lights'] == True:
        #    await controllers["simulator"].send_command("light", "off")

    except LvmecpError as err:
            return command.fail(str(err))

    return command.finish(text="done")

@light.command()
@click.argument("ROOM", type=str, required=False)
async def off(
    command: Command, controllers: dict[str, PlcController], room: str
    ):
    """on or off the enclosure light"""

    tasks = []
    #current_status = await controllers["simulator"].HL_status()
    command.info(text="off the light")

    try:
        await controllers["simulator"].send_command("light", "off")
        #if current_status['Low_lights'] == False or current_status['High_lights'] == False:
        #    await controllers["simulator"].send_command("light", "on")
        #elif current_status['Low_lights'] == True or current_status['High_lights'] == True:
        #    await controllers["simulator"].send_command("light", "off")

    except LvmecpError as err:
            return command.fail(str(err))

    return command.finish(text="done")

@light.command()
@click.argument("ROOM", type=str, required=False)
async def status(
    command: Command, controllers: dict[str, PlcController], room: str
    ):
    """return the status of the light"""

    tasks = []
    command.info(text="checking the light")

    try:
        tasks.append(controllers["simulator"].HL_status())
    except LvmecpError as err:
            return command.fail(str(err))

    result = await asyncio.gather(*tasks)
    return command.finish(light=result)

