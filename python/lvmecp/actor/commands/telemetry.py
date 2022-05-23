# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-05
# @Filename: telemetry.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


from __future__ import absolute_import, annotations, division, print_function

from clu.command import Command

from lvmecp.controller.controller import PlcController
from lvmecp.exceptions import LvmecpError

from . import parser


__all__ = ["telemetry"]


@parser.command()
async def telemetry(command: Command, controllers: dict[str, PlcController]):
    """Returns the status of the enclosure"""

    enclosure_status = {}
    final = {}
    lights_status = {}
    room_point = {}
    room_point["cr"] = "control room"
    room_point["ur"] = "utilities room"
    room_point["sr"] = "spectrograph room"
    room_point["uma"] = "uma lights"
    room_point["tb"] = "telescope room - bright"
    room_point["tr"] = "telescope room - red"
    room_list = list(room_point.keys())

    command.info(text="monitoring ... ")

    try:
        estatus = await controllers[0].send_command("interlocks", "E_status", "status")
        enclosure_status["emergency"] = estatus["E_status"]

        domestatus = await controllers[0].send_command("shutter1", "ne_limit", "status")
        drivestatus = await controllers[0].send_command(
            "shutter1", "drive_state", "status"
        )
        if drivestatus["drive_state"] == 0:
            if domestatus["ne_limit"] == 1:
                enclosure_status["Dome"] = "OPEN"
            elif domestatus["ne_limit"] == 0:
                enclosure_status["Dome"] = "CLOSE"
        elif drivestatus["drive_state"] == 1:
            enclosure_status["Dome"] = "moving"
        else:
            enclosure_status["Dome"] = "Error"

        lights_status = await controllers[0].send_command("lights", "all", "status")
        roomlights = {}
        for room_ins in room_list:
            roomlights[room_point[f"{room_ins}"]] = lights_status[f"{room_ins}_status"]
        enclosure_status["lights"] = roomlights

        enclosure_status["hvac"] = await controllers[1].send_command(
            "hvac", "all", "status"
        )

    except LvmecpError as err:
        return command.fail(str(err))

    final["status"] = enclosure_status
    return command.finish(final)
