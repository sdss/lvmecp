#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-25
# @Filename: status.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import TYPE_CHECKING

from lvmecp.safety import SafetyController

from . import parser


if TYPE_CHECKING:
    from lvmecp.actor import ECPCommand
    from lvmecp.module import PLCModule


@parser.command()
async def status(command: ECPCommand):
    """Returns the enclosure status."""

    plc = command.actor.plc

    command.info(registers=(await plc.read_all_registers()))

    modules: list[PLCModule] = [plc.dome, plc.safety, plc.lights]
    for module in modules:
        await module.notify_status(wait=True, command=command)

        if module.name == "safety":
            assert isinstance(module, SafetyController)
            command.info(
                o2_percent_utilities=module.o2_level_utilities,
                o2_percent_spectrograph=module.o2_level_spectrograph,
            )

    return command.finish()
