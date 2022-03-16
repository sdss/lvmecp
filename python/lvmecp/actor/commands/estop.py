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
    """Activates the emergency status.

    if the E-stop has been triggered, a contactor and power electronic
    will shut down.
    """

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

    command.info(text="start emergency stop of the enclosure ... ")
    current_status = {}
    status = {}

    try:
        current_status["E_stop"] = await controllers[0].send_command(
            "interlocks", "E_stop", "trigger"
        )
        current_status["E_status"] = await controllers[0].send_command(
            "interlocks", "E_status", "status"
        )
        status["emergency"] = current_status["E_status"]["E_status"]

    except LvmecpError as err:
        return command.fail(str(err))

    print(status)
    return command.finish(status)
