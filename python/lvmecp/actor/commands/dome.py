# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-05
# @Filename: dm.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import absolute_import, annotations, division, print_function

import datetime

import click
from clu.command import Command

from lvmecp.controller.controller import PlcController
from lvmecp.exceptions import LvmecpError

from . import parser


__all__ = ["dome"]


@parser.group()
def dome():
    """tasks for Dome"""
    pass


@dome.command()
async def move(command: Command, controllers: dict[str, PlcController]):
    """Turn on or off the roll-off dome of the enclosure."""

    estatus = await controllers[0].send_command(
        "interlocks", "E_status", "status"
    )
    print(estatus)
    if estatus["E_status"] == 0:
        pass
    elif estatus["E_status"] == 1:
        command.info(text="[Emergency status] We can't send the command to the enclosure.")
        return command.finish()
    else:
        raise LvmecpError(f"e-stop status is wrong value.")

    command.info(text="move the Dome")
    current_status = {}
    status = {}

    try:
        # we should check the dome state(open/close) by drive_state
        current_status["drive_state"] = await controllers[0].send_command(
            "shutter1", "drive_state", "status"
        )

        if current_status["drive_state"]["drive_state"] == 0:
            await controllers[0].send_command("shutter1", "motor_direction", "on")       # Direction would be set to 1
            await controllers[0].send_command("shutter1", "drive_enable", "on")          # Dome enable would be set to 1
            # This would trigger a stage to start the motor
            # and then, the dome would disable automatically
        elif current_status["drive_state"]["drive_state"] == 1:
            await controllers[0].send_command("shutter1", "motor_direction", "off")
            await controllers[0].send_command("shutter1", "drive_enable", "on")
        else:
            raise LvmecpError(f"Drive status returns wrong value.")

        current_status["drive_state"] = await controllers[0].send_command(
            "shutter1", "drive_state", "status"
        )
        status["Dome"] = current_status

    except LvmecpError as err:
        return command.fail(str(err))

    command.info(status=status)
    return command.finish()


@dome.command()
async def status(command: Command, controllers: dict[str, PlcController]):
    """return the current status of the dome"""

    command.info(text="checking the Dome")
    current_status = {}
    status = {}

    try:
        current_status["drive_state"] = await controllers[0].send_command(
            "shutter1", "drive_state", "status"
        )
        #current_status["dome"] = await controllers[0].send_command(
        #    "shutter1", "all", "status"
        #)
        status["Dome"] = current_status

    except LvmecpError as err:
        return command.fail(str(err))

    command.info(status=status)
    return command.finish()
