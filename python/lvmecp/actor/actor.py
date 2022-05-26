#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-24
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import pathlib
from copy import deepcopy

from clu.actor import AMQPActor
from sdsstools import read_yaml_file

from lvmecp import config as lvmecp_config
from lvmecp.actor.commands import parser
from lvmecp.plc import PLC


__all__ = ["ECPActor"]


class ECPActor(AMQPActor):
    """Enclosure actor."""

    parser = parser

    def __init__(self, plc: PLC, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.plc = plc

    @classmethod
    def from_config(
        cls,
        config: dict | pathlib.Path | str | None = None,
        *args,
        **kwargs,
    ):

        if config is None:
            config = deepcopy(lvmecp_config)
        elif isinstance(config, (pathlib.Path, str)):
            config = read_yaml_file(config)

        plc = PLC.from_config(config["plc"])

        return super().from_config(config, plc, *args, **kwargs)
