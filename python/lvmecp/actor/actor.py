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
import time

from lvmopstools.actor import ErrorCodesBase, LVMActor
from lvmopstools.notifications import send_notification

from clu.tools import ActorHandler
from sdsstools.utils import cancel_task

from lvmecp import __version__, log
from lvmecp.actor.commands import parser
from lvmecp.exceptions import ECPWarning
from lvmecp.plc import PLC


__all__ = ["ECPActor"]


class ECPActor(LVMActor):
    """Enclosure actor."""

    _engineering_mode_hearbeat_interval: float = 5
    _engineering_mode_timeout: float = 30

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
        self._monitor_dome_task: asyncio.Task | None = None

        self._engineering_mode: bool = False
        self._engineering_mode_task: asyncio.Task | None = None

        self.running: bool = False

    async def start(self, **kwargs):
        """Starts the actor."""

        await super().start(**kwargs)
        self.running = True

        # Start PLC modules now that the actor is running. This prevents the modules
        # trying to broadcast messages before the actor is ready.
        await self.plc.start_modules()

        self._emit_status_task = asyncio.create_task(self.emit_status())
        self._monitor_dome_task = asyncio.create_task(self.monitor_dome())

        return self

    async def stop(self, **kwargs):
        """Stops the actor."""

        self._emit_status_task = await cancel_task(self._emit_status_task)
        self._monitor_dome_task = await cancel_task(self._monitor_dome_task)

        self._engineering_mode_task = await cancel_task(self._engineering_mode_task)

        await super().stop(**kwargs)
        self.running = False

        return

    async def emit_status(self, delay: float = 30.0):
        """Emits the status on a timer."""

        while True:
            await self.send_command(self.name, "status", internal=True)
            await asyncio.sleep(delay)

    async def monitor_dome(self, delay: float = 30.0):
        """Monitors the dome and closes during daytime."""

        while True:
            await asyncio.sleep(delay)

            if self._engineering_mode:
                pass
            elif self.plc.dome.is_daytime():
                self.write("w", text="Dome found open during daytime. Closing.")
                await send_notification(
                    "Dome found open during daytime. Closing.",
                    level="warning",
                )
                await self.plc.dome.close()

    async def engineering_mode(
        self,
        enable: bool,
        timeout: float | None = None,
    ):
        """Sets or returns the engineering mode."""

        # Kill current task if it exists.
        self._engineering_mode_task = await cancel_task(self._engineering_mode_task)

        if enable:
            self._engineering_mode_task = asyncio.create_task(
                self._run_eng_mode(timeout)
            )

        self._engineering_mode = enable

    def is_engineering_mode_enabled(self):
        """Returns whether engineering mode is enabled."""

        return self._engineering_mode

    async def _run_eng_mode(self, timeout: float | None = None):
        """Runs the engineering mode.

        Emits a heartbeat every N seconds even if we are not receiving heartbeat
        commands from ``lvmbeat``. Monitors how long we have been in engineering
        mode and disables it after a timeout.

        """

        started_at: float = time.time()
        timeout = timeout or self._engineering_mode_timeout

        while True:
            await self.emit_heartbeat()

            if time.time() - started_at > timeout:
                self.write("w", text="Engineering mode timed out and was disabled.")
                await self.engineering_mode(False)
                return

            await asyncio.sleep(self._engineering_mode_hearbeat_interval)

    async def emit_heartbeat(self):
        """Emits a heartbeat to the PLC."""

        await self.plc.modbus["hb_set"].set(True)

    async def _check_internal(self):
        return await super()._check_internal()

    async def _troubleshoot_internal(
        self,
        error_code: ErrorCodesBase,
        exception: Exception | None = None,
    ):
        return await super()._troubleshoot_internal(error_code, exception)
