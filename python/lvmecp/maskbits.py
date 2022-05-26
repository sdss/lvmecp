#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-24
# @Filename: maskbits.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from enum import Flag


__all__ = ["DomeStatus", "LightStatus"]


class DomeStatus(Flag):
    """Position and status of the dome."""

    OPEN = 0x1
    CLOSED = 0x2
    MOVING = 0x4
    DRIVE_ENABLED = 0x10
    MOTOR_CLOSING = 0x20
    MOTOR_OPENING = 0x40
    BRAKE_ENABLED = 0x80
    NE_LIMIT = 0x100
    NW_LIMIT = 0x200
    SE_LIMIT = 0x400
    SW_LIMIT = 0x800
    OVERCURRENT = 0x10000
    E_STOP = 0x20000
    ERROR = 0x40000
    UNKNOWN = 0x100000


class LightStatus(Flag):
    """Lights status. Active bits indicate on lamps."""

    CONTROL_ROOM = 0x1
    UTILITY_ROOM = 0x2
    SPECTROGRAPH_ROOM = 0x4
    UMA_ROOM = 0x8
    TELESCOPE_BRIGHT = 0x10
    TELESCOPE_RED = 0x20
