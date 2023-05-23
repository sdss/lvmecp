#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-24
# @Filename: dome.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from types import SimpleNamespace

from lvmecp.maskbits import DomeStatus
from lvmecp.module import PLCModule


class DomeController(PLCModule[DomeStatus]):
    """Controller for the rolling dome."""

    flag = DomeStatus

    async def _update_internal(self):
        dome_registers = await self.plc.modbus.read_group("dome")

        dome_status = SimpleNamespace(**dome_registers)

        new_status = self.flag(0)

        if dome_status.drive_enabled:
            new_status |= self.flag.DRIVE_ENABLED
            if dome_status.motor_direction:
                new_status |= self.flag.MOTOR_OPENING
            else:
                new_status |= self.flag.MOTOR_CLOSING

        if dome_status.drive_state:
            new_status |= self.flag.DRIVE_CONNECTED

        if dome_status.drive_brake:
            new_status |= self.flag.BRAKE_ENABLED

        if dome_status.overcurrent:
            new_status |= self.flag.OVERCURRENT

        return new_status
