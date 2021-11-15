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
from typing import Text
import click
import json

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
async def move(
    command: Command, controllers: dict[str, PlcController], room: str
    ):
    """on or off the enclosure light"""

    command.info(text="move the light")

    try:
        await controllers["simulator"].send_command("light", "move")
        current_status = await controllers["simulator"].get_status("light")

    except LvmecpError as err:
            return command.fail(str(err))

    command.info(current_status)
    return command.finish()


@light.command()
@click.argument("ROOM", type=str, required=False)
async def status(
    command: Command, controllers: dict[str, PlcController], room: str
    ):
    """return the status of the light"""

    command.info(text="checking the light")
    current_status = {}

    try:
        current_status = await controllers["simulator"].get_status("light")

    except LvmecpError as err:
            return command.fail(str(err))

    command.info(current_status)
    return command.finish()
