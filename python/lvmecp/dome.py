#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-24
# @Filename: dome.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
import warnings
from types import SimpleNamespace

from lvmecp import log
from lvmecp.exceptions import DomeError, ECPWarning
from lvmecp.maskbits import DomeStatus
from lvmecp.module import PLCModule


class DomeController(PLCModule[DomeStatus]):
    """Controller for the rolling dome."""

    flag = DomeStatus
    interval = 15.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def _update_internal(self, use_cache: bool = True):
        dome_registers = await self.plc.modbus.read_group("dome", use_cache=use_cache)

        dome_status = SimpleNamespace(**dome_registers)

        assert self.flag
        new_status = self.flag(0)

        if dome_status.drive_state:
            new_status |= self.flag.DRIVE_AVAILABLE
        else:
            new_status |= self.flag.NODRIVE

        if dome_status.drive_enabled:
            new_status |= self.flag.DRIVE_ENABLED

        if dome_status.drive_enabled:
            new_status |= self.flag.MOVING
            if dome_status.motor_direction:
                new_status |= self.flag.MOTOR_OPENING
            else:
                new_status |= self.flag.MOTOR_CLOSING

        if dome_status.drive_brake:
            new_status |= self.flag.BRAKE_ENABLED

        # if dome_status.overcurrent:
        #     new_status |= self.flag.OVERCURRENT

        if dome_status.dome_open is True:
            new_status |= self.flag.OPEN
        elif dome_status.dome_closed is True:
            new_status |= self.flag.CLOSED
        else:
            new_status |= self.flag.POSITION_UNKNOWN

        if new_status.value == 0:
            new_status = self.flag.__unknown__

        return new_status

    async def set_direction(self, open: bool):
        """Sets the motor direction (`True` means open, `False` close)."""

        await self.modbus["drive_direction"].set(open)
        await self.update(use_cache=False)

    async def _move(self, open: bool, force: bool = False):
        """Moves the dome to open/close position."""

        if not (await self.plc.safety.is_remote()):
            raise DomeError("Cannot move dome while in local mode.")

        await self.update(use_cache=False)

        assert self.status is not None and self.flag is not None

        if self.status & self.flag.UNKNOWN:
            raise DomeError("Dome is in unknown state.")

        if self.status & self.flag.NODRIVE:
            raise DomeError("Dome drive is not available.")

        # TODO: in the future this may not be an error and we may
        # want to override the direction of the move.
        if self.status & self.flag.MOVING:
            raise DomeError("Dome is moving.")

        already_at_position = False
        if (self.status & self.flag.OPEN) and open:
            already_at_position = True
        elif (self.status & self.flag.CLOSED) and not open:
            already_at_position = True
        else:
            warnings.warn("Dome in unknown or intermediate position.", ECPWarning)

        if already_at_position:
            if force is False:
                return
            else:
                warnings.warn("Dome already at position, but forcing.", ECPWarning)

        log.debug("Setting motor_direction.")
        await self.modbus["motor_direction"].set(open)

        await asyncio.sleep(0.5)

        log.debug("Setting drive_enabled.")
        await self.modbus["drive_enabled"].set(True)

        await asyncio.sleep(0.5)
        while True:
            # Still moving.
            await asyncio.sleep(2)

            drive_enabled = await self.modbus["drive_enabled"].get()
            move_done = await self.modbus["dome_open" if open else "dome_closed"].get()

            if not drive_enabled and move_done:
                break

        await self.update(use_cache=False)

    async def open(self, force: bool = False):
        """Open the dome."""

        await self._move(True, force=force)

    async def close(self, force: bool = False):
        """Close the dome."""

        await self._move(False, force=force)

    async def stop(self):
        """Stops the dome."""

        status = await self.update(use_cache=False)
        if status is None or self.flag is None:
            raise RuntimeError("Failed retrieving dome status.")

        drive_enabled = bool(status & self.flag.DRIVE_ENABLED)
        if not drive_enabled:
            return

        await self.plc.modbus["drive_enabled"].set(False)

        await self.update(use_cache=False)
