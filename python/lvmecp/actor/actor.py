#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-24
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
import logging

from lvmopstools.actor import ErrorCodesBase, LVMActor

from clu.tools import ActorHandler

from lvmecp import __version__, log
from lvmecp.actor.commands import parser
from lvmecp.exceptions import ECPWarning
from lvmecp.plc import PLC


__all__ = ["ECPActor"]


class ECPActor(LVMActor):
    """Enclosure actor."""

    parser = parser

    def __init__(
        self,
        plc: PLC | None = None,
        *args,
        plc_config: dict | None = None,
        **kwargs,
    ):
        if "version" not in kwargs:
            kwargs["version"] = __version__

        super().__init__(*args, **kwargs)

        self.actor_handler = ActorHandler(
            self,
            level=logging.WARNING,
            filter_warnings=[ECPWarning],
        )
        log.addHandler(self.actor_handler)
        if log.warnings_logger:
            log.warnings_logger.addHandler(self.actor_handler)

        if plc is None:
            plc_config = plc_config or self.config
            self.plc = PLC(config=plc_config, actor=self)
        else:
            self.plc = plc

    async def start(self, **kwargs):
        """Starts the actor."""

        await super().start(**kwargs)

        asyncio.create_task(self.emit_status())
        asyncio.create_task(self.emit_heartbeat())

        return self

    async def emit_status(self, delay: float = 30.0):
        """Emits the status on a timer."""

        while True:
            await self.send_command(self.name, "status", internal=True)
            await asyncio.sleep(delay)

    async def emit_heartbeat(self, delay: float = 5.0):
        """Updates the heartbeat Modbus variable to indicate the system is alive."""

        while True:
            try:
                await self.plc.modbus["hb_set"].set(True)
            except Exception:
                self.write("w", "Failed to set heartbeat variable.")
            finally:
                await asyncio.sleep(delay)

    async def _check_internal(self):
        return await super()._check_internal()

    async def _troubleshoot_internal(
        self,
        error_code: ErrorCodesBase,
        exception: Exception | None = None,
    ):
        return await super()._troubleshoot_internal(error_code, exception)
