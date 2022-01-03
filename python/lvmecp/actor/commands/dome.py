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
        current_time = datetime.datetime.now()
        print(
            f"start the command and get initial status of device              : {current_time}"
        )
        current_status["enable"] = await controllers[0].send_command(
            "shutter1", "drive_enable", "status"
        )
        if current_status["enable"] == 0:
            # dome state == close
            current_time = datetime.datetime.now()
            print(f"start the send_command(ON)           : {current_time}")
            await controllers[0].send_command("shutter1", "drive_enable", "on")
            await controllers[0].send_command("shutter1", "motor_direction", "on")
        elif current_status["enable"] == 1:
            # dome state == open
            current_time = datetime.datetime.now()
            print(f"start the send_command(OFF)           : {current_time}")
            await controllers[0].send_command("shutter1", "drive_enable", "off")
            await controllers[0].send_command("shutter1", "motor_direction", "off")
        else:
            raise LvmecpError(f"{current_status} is wrong value.")

        current_time = datetime.datetime.now()
        print(f"get final status of device              : {current_time}")

        current_status["enable"] = await controllers[0].send_command(
            "shutter1", "drive_enable", "status"
        )
        current_status["drive"] = await controllers[0].send_command(
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
        current_status["enable"] = await controllers[0].send_command(
            "shutter1", "drive_enable", "status"
        )
        current_status["drive"] = await controllers[0].send_command(
            "shutter1", "drive_state", "status"
        )
        status["Dome"] = current_status

    except LvmecpError as err:
        return command.fail(str(err))

    command.info(status=status)
    return command.finish()


@dome.command()
@click.argument("shutters", type=int, required=True)
@click.argument("acts", type=str, required=True)
async def test(command: Command, controllers: dict[str, PlcController], shutters: int, acts: str):
    """test for moving the dome parameters"""

    command.info(text="testing the dome")
    current_status={}
    status={}

    if shutters == 1:
        if acts == "status":
            current_status["coil"] = await controllers[0].send_command(
                "shutter1", "all", "status"
                )
            status["Dome"] = current_status
        elif acts == "move":
            current_status["coil"] = await controllers[0].send_command(
                "shutter1", "all", "status"
                )
            if current_status["coil"]["drive_enable"] == 0:
                    current_status["coil"] = await controllers[0].send_command(
                        "shutter1", "all", "on"
                        )
            elif current_status["coil"]["drive_enable"] == 1:
                    current_status["coil"] = await controllers[0].send_command(
                        "shutter1", "all", "off"
                        )
            else:
                raise LvmecpError(f"{current_status} is wrong value.")
            
            current_status["coil"] = await controllers[0].send_command(
                "shutter1", "all", "status"
                )
            status["Dome"] = current_status
        else:
            raise LvmecpError(f"{acts} is wrong value.")

    elif shutters == 2:
        if acts == "status":
            current_status["register"] = await controllers[0].send_command(
                "shutter2", "all", "status"
                )
            status["Dome"] = current_status
        elif acts == "move":
            current_status["register"] = await controllers[0].send_command(
                "shutter2", "all", "status"
                )
            if current_status["register"]["drive_velcity2"] == 0:
                    current_status["register"] = await controllers[0].send_command(
                        "shutter2", "all", "on"
                        )
            elif current_status["register"]["drive_velcity2"] != 0:
                    current_status["register"] = await controllers[0].send_command(
                        "shutter2", "all", "off"
                        )
            else:
                raise LvmecpError(f"{current_status} is wrong value.")
            
            current_status["register"] = await controllers[0].send_command(
                "shutter2", "all", "status"
                )
            status["Dome"] = current_status
        else:
            raise LvmecpError(f"{acts} is wrong value.")
    else:
        raise LvmecpError(f"{shutters} is wrong value.")

    command.info(status=status)
    return command.finish()
