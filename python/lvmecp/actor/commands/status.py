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

    plc = command.actor.plc

    command.info(registers=(await plc.read_all_registers()))

    modules = [plc.dome, plc.safety]
    for module in modules:
        await module.notify_status(wait=True, command=command)

    return command.finish()
