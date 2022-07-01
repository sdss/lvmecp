#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-25
# @Filename: status.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import TYPE_CHECKING

from . import parser


if TYPE_CHECKING:
    from lvmecp.actor import ECPCommand


@parser.command()
async def status(command: ECPCommand):
    """Returns the enclosure status."""

    command.info(registers=(await command.actor.plc.read_all_registers()))

    return command.finish()
