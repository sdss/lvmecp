# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-05
# @Filename: dm.py
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


__all__ = ["dm"]

@parser.group()
def dm():
    """tasks for Dome"""

    pass

@dm.command()
async def open(
    command: Command, controllers: dict[str, PlcController]
    ):
    """open the enclosure Dome"""

    tasks = []
#    current_status = await controllers["simulator"].DM_status()
    command.info(text="move the Dome")

    try:
        await controllers['simulator'].send_command("Dome", "open")
#        if current_status['Dome_enb_mov'] == None:
#            await controllers['simulator'].send_command("Dome", "open")
#        elif current_status['Dome_enb_mov'] == False:
#            await controllers["simulator"].send_command("Dome", "open")
#        elif current_status['Dome_enb_mov'] == True:
#            await controllers["simulator"].send_command("Dome", "close")

    except LvmecpError as err:
            return command.fail(str(err))

    return command.finish(text="done")

@dm.command()
async def close(
    command: Command, controllers: dict[str, PlcController]
    ):
    """close the enclosure Dome"""

    tasks = []
#    current_status = await controllers["simulator"].DM_status()
    command.info(text="move the Dome")

    try:
        await controllers['simulator'].send_command("Dome", "close")
#        if current_status['Dome_enb_mov'] == None:
#            await controllers['simulator'].send_command("Dome", "open")
#        elif current_status['Dome_enb_mov'] == False:
#            await controllers["simulator"].send_command("Dome", "open")
#        elif current_status['Dome_enb_mov'] == True:
#            await controllers["simulator"].send_command("Dome", "close")

    except LvmecpError as err:
            return command.fail(str(err))

    return command.finish(text="done")

@dm.command()
async def status(
    command: Command, controllers: dict[str, PlcController],
    ):
    """return the status of the Dome"""

    tasks = []
    command.info(text="checking the Dome")

    try:
        tasks.append(controllers["simulator"].DM_status())
    except LvmecpError as err:
            return command.fail(str(err))

    result = await asyncio.gather(*tasks)
    return command.finish(Dome=result)

