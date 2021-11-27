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
@click.argument("ROOM", type=str, required=True)
async def move(
    command: Command, controllers: dict[str, PlcController], room: str
    ):
    """on or off the enclosure light

    Parameters
    -----------
    cr: Control room
    ur: Utilities room
    sr: Spectrograph room
    uma: UMA lights
    tb: Telescope room - bright light
    tr: Telescope room - red light
    """

    current_status = {}
    status = {}
    room_point = {}
    room_point["cr"] = "Control room"
    room_point["ur"] = "Utilities room"
    room_point["sr"] = "Spectrograph room"
    room_point["uma"] = "UMA lights"
    room_point["tb"] = "Telescope room - bright"
    room_point["tr"] = "Telescope room - red"
    room_list = list(room_point.keys())

    try:
        command.info(text=f"move the {room_point[room]}")
        if room in room_list:
            current_status = await controllers[0].send_command("lights", f"{room}_det", "status")
            val = current_status[f"{room}_det"]
            if val == 0:
                await controllers[0].send_command(
                    "lights",
                    f"{room}_relay",
                    "on"
                )
            elif val == 1:
                await controllers[0].send_command(
                    "lights",
                    f"{room}_relay",
                    "off"
                )
            else:
                raise LvmecpError(
                    f"{current_status} is wrong value."
                )

        else:
            raise LvmecpError(
                f"{room} is wrong argument."
            )

        current_status = await controllers[0].send_command(
            "lights",
            f"{room}_det",
            "status"
        )
        status[room_point[f"{room}"]] = current_status[f"{room}_det"]

    except LvmecpError as err:
            return command.fail(str(err))

    command.info(status=status)
    return command.finish()


@light.command()
@click.argument("ROOM", type=str, required=False)
async def status(
    command: Command, controllers: dict[str, PlcController], room: str
    ):
    """return the status of the light
    
    Parameters
    -----------
    cr: Control room
    ur: Utilities room
    sr: Spectrograph room
    uma: UMA lights
    tb: Telescope room - bright light
    tr: Telescope room - red light
    all: return the status of all room
    """

    command.info(text="checking the light")
    current_status = {}
    status = {}
    room_point = {}
    room_point["cr"] = "Control room"
    room_point["ur"] = "Utilities room"
    room_point["sr"] = "Spectrograph room"
    room_point["uma"] = "UMA lights"
    room_point["tb"] = "Telescope room - bright"
    room_point["tr"] = "Telescope room - red"
    room_list = list(room_point.keys())

    try:
        if room:
            if room in room_list:
                current_status = await controllers[0].send_command(
                    "lights",
                    f"{room}_det",
                    "status"
                )
                status[room_point[f"{room}"]] = current_status[f"{room}_det"]
            else:
                raise LvmecpError(
                    f"{room} is wrong argument."
                )
        else:
            current_status = await controllers[0].send_command(
                "lights",
                "all",
                "status"
            )
            for room_ins in room_list:
                status[room_point[f"{room_ins}"]] = current_status[f"{room_ins}_det"]


    except LvmecpError as err:
            return command.fail(str(err))

    command.info(status=status)
    return command.finish()
