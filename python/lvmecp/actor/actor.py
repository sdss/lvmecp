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
from lvmecp.controller.testcontroller import TestController
from lvmecp.exceptions import LvmecpUserWarning

from .commands import parser as lvmecp_command_parser


__all__ = ["LvmecpBaseActor","LvmecpActor"]

class LvmecpBaseActor(BaseActor):
    """Lvmecp controller base actor.
    
    This class is intended to be subclassed with a specific actor class (normally
    ``AMQPActor`` or ``LegacyActor``).
    Parameters
    ----------
    controllers
        The list of `.PlcController` instances to manage.
    """
    
    #parser: ClassVar[click.Group] = lvmecp_command_parser

    def __init__(
        self,
        *args,
        controllers: tuple[TestController, ...] = (),
        **kwargs,
    ):

    #: dict[str, PlcController]: A mapping of controller name to controller.
        self.controllers = {c.name: c for c in controllers}
        self.parser_args = [self.controllers]

        super().__init__(*args, **kwargs)

        self.version = __version__

        self._fetch_log_jobs = []
        self._status_jobs = []

    async def start(self):
        """Start the actor and connect the controllers."""

        connect_timeout = self.config["timeouts"]["controller_connect"]

        for controller in self.controllers.values():
            try:
                await asyncio.wait_for(controller.start(), timeout=connect_timeout)
            except asyncio.TimeoutError:
                warnings.warn(
                    f"Timeout out connecting to {controller.name!r}.",
                    LvmecpUserWarning,
                )

        await super().start()

        self._fetch_log_jobs = [
            asyncio.create_task(self._fetch_log(controller))
            for controller in self.controllers.values()
        ]

        self._status_jobs = [
            asyncio.create_task(self._report_status(controller))
            for controller in self.controllers.values()
        ]

    async def stop(self):
        with suppress(asyncio.CancelledError):
            for task in self._fetch_log_jobs:
                task.cancel()
                await task

        for controller in self.controllers.values():
            await controller.stop()

        return await super().stop()

    @classmethod
    def from_config(cls, config, *args, **kwargs):
        """Creates an actor from a configuration file."""

        if config is None:
            if cls.BASE_CONFIG is None:
                raise RuntimeError("The class does not have a base configuration.")
            config = cls.BASE_CONFIG

        instance = super(LvmecpBaseActor, cls).from_config(config, *args, **kwargs)

        assert isinstance(instance, LvmecpBaseActor)
        assert isinstance(instance.config, dict)

        if "controllers" in instance.config:
            controllers = (
                TestController(
                    ctrname,
                    ctr["host"],
                    ctr["port"],
                )
                for (ctrname, ctr) in instance.config["controllers"].items()
            )
            instance.controllers = {c.name: c for c in controllers}
            instance.parser_args = [instance.controllers]  # Need to refresh this

        return instance
        
class LvmecpActor(LvmecpBaseActor, AMQPActor):
    """Lvmecp actor based on the AMQP protocol"""

    pass