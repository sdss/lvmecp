# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-05
# @Filename: telemetry.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


from __future__ import absolute_import, annotations, division, print_function

import datetime

import click
from clu.command import Command

from lvmecp.controller.controller import PlcController
from lvmecp.exceptions import LvmecpError

from . import parser


__all__ = ["telemetry"]


@parser.command()
async def telemetry(command: Command, controllers: dict[str, PlcController]):
    """Returns the status of the enclosure"""

    status = {}
    lights_status = {}
    room_point = {}
    room_point["cr"] = "Control room"
    room_point["ur"] = "Utilities room"
    room_point["sr"] = "Spectrograph room"
    room_point["uma"] = "UMA lights"
    room_point["tb"] = "Telescope room - bright"
    room_point["tr"] = "Telescope room - red"
    room_list = list(room_point.keys())

    command.info(text="monitoring ... ")

    try:
        estatus = await controllers[0].send_command("interlocks", "E_status", "status")
        status["emergency"] = estatus["E_status"]

        domestatus = await controllers[0].send_command("shutter1", "ne_limit", "status")
        drivestatus = await controllers[0].send_command(
            "shutter1", "drive_state", "status"
        )
        if drivestatus["drive_state"] == 0:
            status["Dome"] = domestatus["ne_limit"]
        elif drivestatus["drive_state"] == 1:
            status["Dome"] = "moving"
        else:
            status["Dome"] = "Error"

        lights_status = await controllers[0].send_command("lights", "all", "status")
        roomlights = {}
        for room_ins in room_list:
            roomlights[room_point[f"{room_ins}"]] = lights_status[f"{room_ins}_status"]
        status["lights"] = roomlights

        status["HVAC"] = await controllers[1].send_command("hvac", "all", "status")

    except LvmecpError as err:
        return command.fail(str(err))

    command.info(status=status)
    return command.finish()
