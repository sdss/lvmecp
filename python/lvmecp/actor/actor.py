#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-24
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from clu.actor import AMQPActor

from lvmecp import __version__
from lvmecp.actor.commands import parser
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

        if plc is None:
            if plc_config is None and self.config.get("plc", None) is None:
                raise ValueError("PLC configuraton must be defined at initialisation.")
            plc_config = plc_config or self.config["plc"]

            self.plc = PLC(config=self.config["plc"], actor=self)
        else:
            self.plc = plc
