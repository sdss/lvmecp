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

@parser.command()
async def estop(command: Command, controllers: dict[str, PlcController]):
    """return the status of emergency stop.
    
    ECP should start the emergency stop
    if the pressure changed outside normal range. 
    """

    command.info(text="monitoring ... ")
    current_status = {}

    try:
        #current_status["interlocks"] = await controllers[0].send_command("interlocks","0","status")
        current_status["emergengy"] = await controllers[0].send_command(
            "emergengy",
            "0",
            "status"
        )

    except LvmecpError as err:
        return command.fail(str(err))

    command.info(status=current_status)
    return command.finish()
