#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-25
# @Filename: lights.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import click

from lvmecp.lights import CODE_TO_LIGHT

from . import parser


if TYPE_CHECKING:
    from lvmecp.actor import ECPCommand


@parser.command()
@click.argument("LIGHT", type=str, required=False)
@click.argument(
    "ACTION",
    type=click.Choice(["on", "off", "switch"], case_sensitive=False),
    required=False,
)
async def lights(
    command: ECPCommand,
    light: str | None = None,
    action: str | None = None,
):
    """Manages the enclosure lights."""

    plc = command.actor.plc

    if light is None:
        return command.finish(lights=(await plc.lights.get_all()))

    try:
        code = plc.lights.get_code(light)
        full = CODE_TO_LIGHT[code]
    except ValueError:
        return command.fail(f"Unknown light {light}.")

    if action == "on":
        await plc.lights.set(light, action=True)
    elif action == "off":
        await plc.lights.set(light, action=False)
    elif action == "switch":
        await plc.lights.set(light, action=None)

    await asyncio.sleep(0.1)

    status = await plc.lights.get_light_status(code)
    return command.finish(lights={full: status})
