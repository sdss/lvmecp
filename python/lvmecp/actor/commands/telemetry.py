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
    """return the status of the enclosure"""
    
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

    estatus = await controllers[0].send_command(
        "interlocks", "E_status", "status"
    )
    status["emergency"] = estatus["E_status"]
    
    domestatus = await controllers[0].send_command(
            "shutter1", "drive_state", "status"
    )
    status["Dome"] = domestatus["drive_state"]
    
    lights_status = await controllers[0].send_command(
        "lights", "all", "status"
    )
    roomlights = {}
    for room_ins in room_list:
        roomlights[room_point[f"{room_ins}"]] = lights_status[f"{room_ins}_status"]
    status["lights"] = roomlights

    status["HVAC"] = await controllers[1].send_command(
        "hvac", "all", "status"
    )

    command.info(status=status)
    return command.finish()

#@parser.command()
#async def telemetry(command: Command, controllers: dict[str, PlcController]):
#    """return the status of the enclosure"""

#    command.info(text="monitoring ... ")

#    current_time = datetime.datetime.now()
#    print(f"start to write the data to dome_status_cmd     : {current_time}")

#    dome_status_cmd = await command.actor.send_command("lvmecp", "dome status")
#    await dome_status_cmd

#    if dome_status_cmd.status.did_fail:
#        command.info(text="Failed to receive the dome status")
#    else:
#        dome_replies = dome_status_cmd.replies
#        dome_status = dome_replies[-2].body["status"]

#    current_time = datetime.datetime.now()
#    print(f"start to write the data to light_status_cmd     : {current_time}")

#    light_status_cmd = await command.actor.send_command("lvmecp", "light status")
#    await light_status_cmd

#    if light_status_cmd.status.did_fail:
#        command.info(text="Failed to receive the light status")
#    else:
#        light_replies = light_status_cmd.replies
#        light_status = light_replies[-2].body["status"]

#    current_time = datetime.datetime.now()
#    print(f"start to write the data to hvac_status_cmd     : {current_time}")

#    hvac_status_cmd = await command.actor.send_command("lvmecp", "monitor")
#    await hvac_status_cmd

#    if hvac_status_cmd.status.did_fail:
#        command.info(text="Failed to receive the hvac status")
#    else:
#        hvac_replies = hvac_status_cmd.replies
#        hvac_status = hvac_replies[-2].body["status"]

#    current_time = datetime.datetime.now()
#    print(f"start to write the data to estop_status_cmd     : {current_time}")

#    estop_status_cmd = await command.actor.send_command("lvmecp", "estop status")
#    await estop_status_cmd

#    if estop_status_cmd.status.did_fail:
#        command.info(text="Failed to receive the estop status")
#    else:
#        estop_replies = estop_status_cmd.replies
#        estop_status = estop_replies[-2].body["status"]

#    command.info(
#        DOME=dome_status, LIGHTS=light_status, HVAC=hvac_status, ESTOP=estop_status
#    )
#    return command.finish()
