# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-05
# @Filename: estop.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


from __future__ import absolute_import, annotations, division, print_function

import datetime

import click
from clu.command import Command

from lvmecp.controller.controller import PlcController
from lvmecp.exceptions import LvmecpError

from . import parser


__all__ = ["estop"]


@parser.group()
def estop():
    """tasks for emergency stop."""
    pass

@estop.command()
async def status(command: Command, controllers: dict[str, PlcController]):
    """return the status of emergency stop.

    ECP should start the emergency stop
    if the pressure changed outside normal range.
    """

    command.info(text="monitoring ... ")
    current_status = {}

    try:
        current_status["emergency"] = await controllers[0].send_command(
            "interlocks", "E_status", "status"
        )

    except LvmecpError as err:
        return command.fail(str(err))

    command.info(status=current_status)
    return command.finish()

@estop.command()
async def trigger(command: Command, controllers: dict[str, PlcController]):
    """E-stop indicator code, 
    uses the modbus + input variables to determine
    if the E-stop has been triggered.
    """

    command.info(text="start emergency stop of the enclosure ... ")
    current_status = {}
    status={}

    try:
        current_status["E_stop"] = await controllers[0].send_command(
            "interlocks","E_stop","trigger"
        )
        status["emergency"] = await controllers[0].send_command(
            "interlocks", "E_status", "status"
        )

    except LvmecpError as err:
        return command.fail(str(err))

    command.info(status=status)
    return command.finish()

@estop.command()
async def stop(command: Command, controllers: dict[str, PlcController]):
    """stop the emergency status"""

    command.info(text="stop the emergency status ... ")
    current_status = {}
    status={}

    try:
        current_status["E_stop"] = await controllers[0].send_command(
            "interlocks","E_stop","stop"
        )
        status["emergency"] = await controllers[0].send_command(
            "interlocks", "E_status", "status"
        )

    except LvmecpError as err:
        return command.fail(str(err))

    command.info(status=status)
    return command.finish()