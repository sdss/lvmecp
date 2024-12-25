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
from sdsstools.utils import cancel_task

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
            self.plc = PLC(config=plc_config, actor=self, start_modules=False)
        else:
            self.plc = plc

        self.semaphore = asyncio.Semaphore(5)

        self._emit_status_task: asyncio.Task | None = None


    async def start(self, **kwargs):
        """Starts the actor."""

        self.running: bool = False

    async def start(self, **kwargs):
        """Starts the actor."""

        await super().start(**kwargs)
        self.running = True

        # Start PLC modules now that the actor is running. This prevents the modules
        # trying to broadcast messages before the actor is ready.
        await self.plc.start_modules()

        self._emit_status_task = asyncio.create_task(self.emit_status())

        return self

    async def stop(self, **kwargs):
        """Stops the actor."""

        self._emit_status_task = await cancel_task(self._emit_status_task)
        await super().stop(**kwargs)
        self.running = False

        return

    async def emit_status(self, delay: float = 30.0):
        """Emits the status on a timer."""

        while True:
            await self.send_command(self.name, "status", internal=True)
            await asyncio.sleep(delay)

    async def _check_internal(self):
        return await super()._check_internal()

    async def _troubleshoot_internal(
        self,
        error_code: ErrorCodesBase,
        exception: Exception | None = None,
    ):
        return await super()._troubleshoot_internal(error_code, exception)
