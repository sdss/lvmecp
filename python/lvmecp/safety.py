#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-06-20
# @Filename: safety.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from types import SimpleNamespace

from lvmecp.maskbits import SafetyStatus
from lvmecp.module import PLCModule


class SafetyController(PLCModule[SafetyStatus]):
    """Handles the enclosure safety features."""

    flag = SafetyStatus

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def _update_internal(self):
        safety_registers = await self.plc.modbus.read_group("safety")

        safety_status = SimpleNamespace(**safety_registers)

        new_status = self.flag(0)

        if safety_status.door_closed:
            new_status |= self.flag.DOOR_CLOSED

        if safety_status.door_locked:
            new_status |= self.flag.DOOR_LOCKED

        if safety_status.local:
            new_status |= self.flag.LOCAL

        return new_status

    async def is_remote(self):
        """Returns `True` if NOT in local mode (i.e., safe to operate remotely)."""

        safety_config = self.plc.config.get("safety", {})
        override_local = safety_config.get("override_local_mode", False)
        if override_local:
            return True

        await self.update()
        return not (self.status & self.flag.LOCAL)
