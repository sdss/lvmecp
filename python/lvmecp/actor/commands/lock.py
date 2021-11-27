# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-05
# @Filename: lock.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


from __future__ import absolute_import, annotations, division, print_function

import asyncio
import datetime
from os import name
from typing import Text
import click
import json

from clu.command import Command
from lvmecp.controller.controller import PlcController
from lvmecp.exceptions import LvmecpError

from . import parser


__all__ = ["lock"]

@parser.command()
async def lock(command: Command, controllers: dict[str, PlcController]):
    """return the status of the interlocks"""

    command.info(text="checking the interlocks")
    current_status = {}

    try:
        current_status = await controllers[0].send_command(
            "interlocks",
            "0", 
            "status"
        )

    except LvmecpError as err:
            return command.fail(str(err))

    command.info(status=current_status)
    return command.finish()

