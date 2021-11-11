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
import warnings
from contextlib import suppress

from typing import ClassVar, Dict, Type

import click
from clu.actor import AMQPActor, BaseActor

from lvmecp import __version__
from lvmecp.controller.controller import PlcController
#from lvmecp.controller.testcontroller import TestController
from lvmecp.exceptions import LvmecpUserWarning

from .commands import parser as lvmecp_command_parser


__all__ = ["LvmecpActor"]

class LvmecpActor(AMQPActor):
    """Lvmecp controller actor.

    Parameters
    ----------
    controllers
        The list of `.PlcController` instances to manage.
    """
    
    parser: ClassVar[click.Group] = lvmecp_command_parser
    BASE_CONFIG: ClassVar[str | Dict | None] = None


    def __init__(
        self,
        *args,
        controllers: tuple[PlcController, ...] = (),
        **kwargs,
    ):
    #: dict[str, PlcController]: A mapping of controller name to controller.
        self.controllers = {c.name: c for c in controllers}
        self.parser_args = [self.controllers]


        #if "schema" not in kwargs:
        #    kwargs["schema"] = os.path.join(
        #        os.path.dirname(__file__),
        #        "../etc/schema.json",
        #    )        
        super().__init__(*args, **kwargs)

        self.version = __version__


    async def start(self):
        """Start the actor and connect the controllers."""
        await super().start()


    async def stop(self):
        """Stop the actor and disconnect the controllers."""
        return await super().stop()

    @classmethod
    def from_config(cls, config, *args, **kwargs):
        """Creates an actor from a configuration file."""

        instance = super(LvmecpActor, cls).from_config(config, *args, **kwargs)

        assert isinstance(instance, LvmecpActor)
        assert isinstance(instance.config, dict)

        if "simulator" in instance.config["devices"]["plcs"]:
            controllers = (
                PlcController(
                    name=ctrname,
                    host=ctr["host"],
                    port=ctr["port"],
                )
                for (ctrname, ctr) in instance.config["devices"]["plcs"].items()
            )
            instance.controllers = {c.name: c for c in controllers}
            instance.parser_args = [instance.controllers]  # Need to refresh this

        return instance
