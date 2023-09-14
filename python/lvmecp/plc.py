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

from lvmecp.hvac import HVACController
from lvmecp.modbus import Modbus
from lvmecp.safety import SafetyController

from .dome import DomeController
from .lights import LightsController


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


class PLC:
    """Class for the enclosure programmable logic controller."""

    def __init__(self, config: dict, actor: ECPActor | None = None):
        self.config = config
        self.modbus = Modbus(config=config["modbus"])

        self.dome = DomeController(
            "dome",
            self,
            notifier=create_actor_notifier(actor, "dome_status"),
        )

        self.safety = SafetyController(
            "safety",
            self,
            notifier=create_actor_notifier(actor, "safety_status"),
        )

        self.lights = LightsController(
            "lights",
            self,
            notifier=create_actor_notifier(actor, "lights"),
        )

        self.hvac_modbus = Modbus(config=config["hvac"])
        self.hvac = HVACController(
            "hvac",
            self,
            modbus=self.hvac_modbus,
            notifier=None,
        )

    async def read_all_registers(self):
        """Reads all the connected registers and returns a dictionary."""

        registers = await self.modbus.get_all()
        registers.update(await self.hvac_modbus.get_all())

        return registers
