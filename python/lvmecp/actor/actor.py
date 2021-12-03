#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-09-30
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
import os
import click

from typing import ClassVar, Dict
from clu.actor import AMQPActor
from lvmecp import __version__
from lvmecp.controller.controller import PlcController

from .commands import parser as lvmecp_command_parser

__all__ = ["LvmecpActor"]


class LvmecpActor(AMQPActor):
    """Lvmecp controller actor.

    Parametersa
    ----------
    controllers
        The list of `.PlcController` instances to manage.
    """

    parser: ClassVar[click.Group] = lvmecp_command_parser
    BASE_CONFIG: ClassVar[str | Dict | None] = None

    def __init__(self, *args, **kwargs):
        #: dict[str, PlcController]: A mapping of controller name to controller.

        if "schema" not in kwargs:
            kwargs["schema"] = os.path.join(
                os.path.dirname(__file__),
                "../etc/schema.json",
            )
        super().__init__(*args, **kwargs)

        self.version = __version__

    async def start(self):
        """Start the actor and connect the controllers."""
        await super().start()

        connect_timeout = self.config["timeouts"]["controller_connect"]

        assert len(self.parser_args) == 1
        for plc in self.parser_args[0]:
            try:
                self.log.debug(f"Start {plc.name} ...")
                await asyncio.wait_for(plc.start(), timeout=connect_timeout)

            except Exception as ex:
                self.log.error(f"Unexpected exception {type(ex)}: {ex}")

        self.log.debug("Start done")

    async def stop(self):
        """Stop the actor and disconnect the controllers."""
        return await super().stop()

    @classmethod
    def from_config(cls, config, *args, **kwargs):
        """Creates an actor from a configuration file."""

        if config is None:
            if cls.BASE_CONFIG is None:
                raise RuntimeError("The class does not have a base configuration.")
            config = cls.BASE_CONFIG

        instance = super(LvmecpActor, cls).from_config(config, *args, **kwargs)

        assert isinstance(instance, LvmecpActor)
        assert isinstance(instance.config, dict)

        if "plcs" in instance.config:
            plcs = []
            for (name, config) in instance.config["plcs"].items():
                instance.log.info(f"Instance {name}: {config}")
                try:
                    plcs.append(PlcController(name, config, instance.log))

                except Exception as ex:
                    instance.log.error(f"Error in {type(ex)}: {ex}")
            instance.parser_args = [plcs]

        return instance
