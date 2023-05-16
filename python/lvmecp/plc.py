#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-24
# @Filename: plc.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from drift import Drift

from .dome import DomeController


if TYPE_CHECKING:
    from clu.command import Command

    from .actor import ECPActor


def create_actor_notifier(
    actor: ECPActor | None,
    keyword: str,
    use_hex: bool = True,
    labels_suffix="_labels",
    level="d",
):
    """Generate a notifier function for a keyword."""

    async def notifier(value: int, labels: str, command: Command | None = None):
        message = {
            keyword: value if use_hex is False else hex(value),
            f"{keyword}{labels_suffix}": labels,
        }
        if command is None and actor:
            # Allow for 3 seconds for broadcast. This is needed because the PLC
            # starts before the actor and for the first message the exchange is
            # not yet available.
            n_tries = 0
            while actor.connection.connection is None:
                n_tries += 1
                if n_tries >= 3:
                    return None
                await asyncio.sleep(1)
            actor.write(level, message)
        elif command is not None:
            command.write(level, message)

    return notifier if actor else None


class PLC(Drift):
    """Class for the enclosure programmable logic controller."""

    def __init__(self, address: str, port: int = 502, actor: ECPActor | None = None):
        super().__init__(address, port)

        self.dome = DomeController(
            "dome",
            self,
            notifier=create_actor_notifier(actor, "dome_status"),
        )

    async def read_all_registers(self):
        """Reads all the connected devices/registers and returns a dictionary."""

        devices = []
        for module in self.modules:
            for device in self[module].devices:
                devices.append(f"{module}.{device}")

        values = await self.read_devices(devices, adapt=False)

        registers = {}
        for ii in range(len(devices)):
            registers[devices[ii].lower()] = values[ii]

        return registers
