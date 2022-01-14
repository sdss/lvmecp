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

    command.info(text="move the Dome")
    current_status = {}
    status = {}

    try:
        current_status["drive_enable"] = await controllers[0].send_command(
            "shutter1", "drive_enable", "status"
        )
        current_status["motor_direction"] = await controllers[0].send_command(
            "shutter1", "motor_direction", "status"
        )
        if current_status["drive_enable"]["drive_enable"] == 0:
            if current_status["motor_direction"]["motor_direction"] == 0:
                await controllers[0].send_command("shutter1", "drive_enable", "on")
                await controllers[0].send_command("shutter1", "motor_direction", "on")
            elif current_status["motor_direction"]["motor_direction"] == 1:
                raise LvmecpError(f"Dome motor has a wrong value.")
            else:
                raise LvmecpError(f"Dome motor has a wrong value.")

        elif current_status["drive_enable"]["drive_enable"] == 1:
            if current_status["motor_direction"]["motor_direction"] == 1:
                await controllers[0].send_command("shutter1", "motor_direction", "off")
                await controllers[0].send_command("shutter1", "drive_enable", "off")
            elif current_status["motor_direction"]["motor_direction"] == 0:
                await controllers[0].send_command("shutter1", "drive_enable", "off")
        else:
            raise LvmecpError(f"drive_enable is wrong value.")

        current_status["drive_enable"] = await controllers[0].send_command(
            "shutter1", "drive_enable", "status"
        )
        current_status["motor_direction"] = await controllers[0].send_command(
            "shutter1", "motor_direction", "status"
        )
        #current_status["drive_state"] = await controllers[0].send_command(
        #    "shutter1", "drive_state", "status"
        #)
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
        #current_status["drive_enable"] = await controllers[0].send_command(
        #    "shutter1", "drive_enable", "status"
        #)
        #current_status["motor_direction"] = await controllers[0].send_command(
        #    "shutter1", "motor_direction", "status"
        #)
        current_status["dome"] = await controllers[0].send_command(
            "shutter1", "all", "status"
        )
        status["Dome"] = current_status

    except LvmecpError as err:
        return command.fail(str(err))

    command.info(status=status)
    return command.finish()
