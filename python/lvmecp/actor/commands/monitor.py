# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-05
# @Filename: monitor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


from __future__ import absolute_import, annotations, division, print_function

import datetime
import click

from clu.command import Command
from lvmecp.controller.controller import PlcController
from lvmecp.exceptions import LvmecpError

from . import parser

__all__ = ["monitor"]

@parser.command()
@click.argument("ROOM", type=str, required=False)
async def monitor(command: Command, controllers: dict[str, PlcController], room: str):
    """return the status of HVAC system and air purge system.
    
    ECP should monitor the pressure in air purge system and the 
    temperature in each room.
    """

    command.info(text="monitoring ... ")
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
                current_status["hvac"] = await controllers[1].send_command(
                    "hvac",
                    f"{room}_sensor",
                    "status"
                )
                status[room_point[f"{room}"]] = current_status[f"{room}_sensor"]
            else:
                raise LvmecpError(
                    f"{room} is wrong argument."
                )
        else:
            current_status["hvac"] = await controllers[1].send_command(
                "hvac",
                "all",
                "status"
            )

    except LvmecpError as err:
        return command.fail(str(err))

    command.info(status=current_status)
    return command.finish()
