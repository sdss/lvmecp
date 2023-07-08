#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-24
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import logging

from clu.actor import AMQPActor
from clu.tools import ActorHandler

from lvmecp import __version__, log
from lvmecp.actor.commands import parser
from lvmecp.exceptions import ECPWarning
from lvmecp.plc import PLC


__all__ = ["ECPActor"]


class ECPActor(AMQPActor):
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
