#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-06-20
# @Filename: safety.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import math
from types import SimpleNamespace

from lvmecp.maskbits import SafetyStatus
from lvmecp.module import PLCModule


class SafetyController(PLCModule[SafetyStatus]):
    """Handles the enclosure safety features."""

    flag = SafetyStatus
    interval = 10.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.o2_level_utilities: float = math.nan
        self.o2_level_spectrograph: float = math.nan

    async def _update_internal(self):
        assert self.flag is not None

        safety_registers = await self.plc.modbus.read_group("safety")

        safety_status = SimpleNamespace(**safety_registers)

        new_status = self.flag(0)

        # Door and lock
        if safety_status.door_closed:
            new_status |= self.flag.DOOR_CLOSED
        if safety_status.door_locked:
            new_status |= self.flag.DOOR_LOCKED
        if safety_status.local:
            new_status |= self.flag.LOCAL

        # Utilities room O2 sensor
        self.o2_level_utilities = safety_status.oxygen_read_utilities_room / 10.0
        if self.o2_level_utilities < self.plc.config["safety"]["o2_threshold"]:
            new_status |= self.flag.O2_SENSOR_UR_ALARM
        if safety_status.oxygen_mode_utilities_room == 8:
            new_status |= self.flag.O2_SENSOR_UR_FAULT

        # Spectrograph room O2 sensor
        self.o2_level_spectrograph = safety_status.oxygen_read_spectrograph_room / 10.0
        if self.o2_level_spectrograph < self.plc.config["safety"]["o2_threshold"]:
            new_status |= self.flag.O2_SENSOR_SR_ALARM
        if safety_status.oxygen_mode_spectrograph_room == 8:
            new_status |= self.flag.O2_SENSOR_SR_FAULT

        if new_status.value == 0:
            new_status = self.flag.__unknown__

        return new_status

    async def is_remote(self):
        """Returns `True` if NOT in local mode (i.e., safe to operate remotely)."""

        safety_config = self.plc.config.get("safety", {})
        override_local = safety_config.get("override_local_mode", False)
        if override_local:
            return True

        await self.update()
        assert self.status is not None and self.flag is not None

        return not (self.status & self.flag.LOCAL)
