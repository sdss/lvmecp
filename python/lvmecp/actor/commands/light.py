# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-05
# @Filename: light.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


from __future__ import absolute_import, annotations, division, print_function

import asyncio
import datetime

from clu.command import Command

from lvmecp.controller.testcontroller import TestController
from lvmecp.controller.pcs import pcs
from lvmecp.exceptions import LvmecpError

from . import parser


__all__ = ["light"]


@parser.group()
def light(*args):
    """control enclosure lights."""

    pass

@light.command()
def move(command: Command, controllers: dict[str, TestController]):
    """on or off the enclosure light"""
    pcs.DCS_update()

    command.info(text="move the light")
    pcs.HL()

    return

@light.command()
def status(command: Command, controllers: dict[str, TestController]):
    """return the status of light"""
    pcs.DCS_update()

    command.info(text="what status the light is")
    pcs.HL_stat()

    return 