#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-24
# @Filename: dome.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import TYPE_CHECKING

from lvmecp.maskbits import DomeStatus
from lvmecp.tools import loop_coro


if TYPE_CHECKING:
    from .plc import PLC


class DomeController:
    """Controller for the rolling dome."""

    def __init__(self, plc: PLC):

        self.plc = plc
        self.client = plc.client

        self.status = DomeStatus.UNKNOWN

        self.__update_loop_task = loop_coro(self.update, 10)

    def __del__(self):

        self.__update_loop_task.cancel()

    async def update(self):
        """Refreshes the dome status."""

        return self.status
