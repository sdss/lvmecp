# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-05
# @Filename: light.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


from __future__ import absolute_import, annotations, division, print_function

import datetime

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
@click.argument("ROOM", type=str, required=True)
async def move(command: Command, controllers: dict[str, PlcController], room: str):
    """Turn on or off the enclosure light. This command
    required the argument essentially. You should put the
    proper argument according to the room you want to control.

    A message is printed by the final status of the light.
    If message return "0", it means "OFF".
    If message return "1", it means "ON".

    Parameters
    -----------
    cr
        Control room.
    ur
        Utilities room.
    sr
        Spectrograph room.
    uma
        UMA lights.
    tb
        Telescope room - bright light.
    tr
        Telescope room - red light.
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
            current_status = await controllers[0].send_command(
                "lights", f"{room}_status", "status"
            )
            val = current_status[f"{room}_status"]
            if val == 0:
                await controllers[0].send_command("lights", f"{room}_new", "on")
            elif val == 1:
                await controllers[0].send_command("lights", f"{room}_new", "off")
            else:
                raise LvmecpError(f"{current_status} is wrong value.")
        else:
            raise LvmecpError(f"{room} is wrong argument.")

        current_status = await controllers[0].send_command(
            "lights", f"{room}_status", "status"
        )
        status[room_point[f"{room}"]] = current_status[f"{room}_status"]

    except LvmecpError as err:
        return command.fail(str(err))

    command.info(status=status)
    return command.finish()


@light.command()
@click.argument("ROOM", type=str, required=False)
async def status(command: Command, controllers: dict[str, PlcController], room: str):
    """return the current status of the light. This command don't
    require the argument essentially. You should put the
    proper argument according to the room you want to control. If you don't
    put any argument, this returns the status of all room in the enclosure.

    A message is printed by the status of the light.
    If message return "0", it means "OFF".
    If message return "1", it means "ON".

    Parameters
    -----------
    cr
        Control room.
    ur
        Utilities room.
    sr
        Spectrograph room.
    uma
        UMA lights.
    tb
        Telescope room - bright light.
    tr
        Telescope room - red light.
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
                    "lights", f"{room}_status", "status"
                )
                status[room_point[f"{room}"]] = current_status[f"{room}_status"]
            else:
                raise LvmecpError(f"{room} is wrong argument.")
        else:
            current_status = await controllers[0].send_command(
                "lights", "all", "status"
            )
            for room_ins in room_list:
                status[room_point[f"{room_ins}"]] = current_status[f"{room_ins}_status"]

    except LvmecpError as err:
        return command.fail(str(err))

    command.info(status=status)
    return command.finish()
