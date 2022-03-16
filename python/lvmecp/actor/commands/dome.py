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
    """Tasks for Dome which turn on or off the roll-off dome and return the current status of the dome"""
    pass


@dome.command()
async def enable(command: Command, controllers: dict[str, PlcController]):
    """Turn on or off the roll-off dome of the enclosure."""

    estatus = await controllers[0].send_command("interlocks", "E_status", "status")
    print(estatus)
    if estatus["E_status"] == 0:
        pass
    elif estatus["E_status"] == 1:
        command.info(
            text="[Emergency status] We can't send the command to the enclosure."
        )
        return command.finish()
    else:
        raise LvmecpError("e-stop status is wrong value.")

    command.info(text="moving the Dome")
    current_status = {}
    domestatus = {}

    try:
        # we should check the dome state(open/close) by drive_state
        current_status = await controllers[0].send_command("shutter1", "all", "status")

        if current_status["drive_state"] == 0:
            # motor state is 0
            if current_status["ne_limit"] == 0:
                # dome is closed
                await controllers[0].send_command(
                    "shutter1", "motor_direction", "on"
                )  # Direction would be set to 1
                domestatus["Dome"] = "OPEN"
            # This would trigger a stage to start the motor
            # and then, the dome would disable automatically
            elif current_status["ne_limit"] == 1:
                # dome is opened
                await controllers[0].send_command("shutter1", "motor_direction", "off")
                domestatus["Dome"] = "CLOSE"
            else:
                raise LvmecpError("The status of limitswitches returns wrong value.")
        elif current_status["drive_state"] == 1:
            # motor state is 1
            raise LvmecpError("the enclosure is moving.")
        else:
            raise LvmecpError("The status of motor returns wrong value.")

        await controllers[0].send_command("shutter1", "drive_enable", "on")

    except LvmecpError as err:
        return command.fail(str(err))

    return command.finish(domestatus)


@dome.command()
async def status(command: Command, controllers: dict[str, PlcController]):
    """return the current status of the dome"""

    command.info(text="checking the Dome")
    current_status = {}
    domestatus = {}

    try:
        current_status = await controllers[0].send_command("shutter1", "all", "status")
        if current_status["drive_state"] == 0:
            if current_status["ne_limit"] == 1:
                domestatus["Dome"] = "OPEN"
            elif current_status["ne_limit"] == 0:
                domestatus["Dome"] = "CLOSE"
        elif current_status["drive_state"] == 1:
            raise LvmecpError("the enclosure is moving.")
        else:
            raise LvmecpError("The status of motor returns wrong value.")

    except LvmecpError as err:
        return command.fail(str(err))

    return command.finish(domestatus)
