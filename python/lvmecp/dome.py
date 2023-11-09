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
    interval = 10.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Temporary, until we have proximity sensors that tell
        # us whether we are open or closed.
        self.dome_is_open: bool | None = None

    async def _update_internal(self):
        dome_registers = await self.plc.modbus.read_group("dome")

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

        if dome_status.overcurrent:
            new_status |= self.flag.OVERCURRENT

        if self.dome_is_open is True:
            new_status |= self.flag.OPEN
        elif self.dome_is_open is False:
            new_status |= self.flag.CLOSED
        else:
            new_status |= self.flag.POSITION_UNKNOWN

        if new_status.value == 0:
            new_status = self.flag.__unknown__

        return new_status

    async def set_direction(self, open: bool):
        """Sets the motor direction (`True` means open, `False` close)."""

        await self.modbus["drive_direction"].set(open)
        await self.update()

    async def _move(self, open: bool, force: bool = False):
        """Moves the dome to open/close position."""

        if not (await self.plc.safety.is_remote()):
            raise DomeError("Cannot move dome while in local mode.")

        await self.update()

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

        self.dome_is_open = None

        await asyncio.sleep(0.5)
        while await self.modbus["drive_enabled"].get():
            # Still moving.
            await asyncio.sleep(2)

        self.dome_is_open = open

        await self.update()

    async def open(self, force: bool = False):
        """Open the dome."""

        await self._move(True, force=force)

    async def close(self, force: bool = False):
        """Close the dome."""

        await self._move(False, force=force)

    async def stop(self):
        """Stops the dome."""

        drive_enabled = await self.plc.modbus["drive_enabled"].get()
        status = await self.update()

        if status is None or self.flag is None:
            raise RuntimeError("Failed retrieving dome status.")

        if not drive_enabled:
            return

        is_moving = status & self.flag.MOVING
        await self.plc.modbus["drive_enabled"].set(False)

        if is_moving:
            self.dome_is_open = None

        await self.update()
