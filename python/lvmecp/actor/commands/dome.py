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
def dome():
    """tasks for Dome"""

    pass

@dome.command()
async def move(
    command: Command, controllers: dict[str, PlcController],
    ):
    """on or off the enclosure Dome"""

    command.info(text="move the Dome")

    try:
        await controllers["simulator"].send_command("Dome", "move")
        current_status = await controllers["simulator"].get_status("Dome")
    except LvmecpError as err:
            return command.fail(str(err))

    return command.finish(text=current_status)

@dome.command()
async def status(
    command: Command, controllers: dict[str, PlcController],
    ):
    """return the status of the Dome"""

    command.info(text="checking the Dome")

    try:
        current_status = await controllers["simulator"].get_status("Dome")
    except LvmecpError as err:
            return command.fail(str(err))
            
    return command.finish(text=current_status)

