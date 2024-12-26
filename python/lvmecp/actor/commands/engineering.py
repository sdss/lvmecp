#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2024-12-24
# @Filename: engineering.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import TYPE_CHECKING

import click

from lvmecp.tools import timestamp_to_iso

from . import parser


if TYPE_CHECKING:
    from lvmecp.actor import ECPCommand


@parser.group(name="engineering-mode")
def engineering_mode():
    """Enable/disable the engineering mode."""

    pass


@engineering_mode.command()
@click.option(
    "--timeout",
    "-t",
    type=click.FloatRange(min=0.1, max=86400),
    help="Timeout for the engineering mode. "
    "If not passed, the default timeout is used.",
)
async def enable(command: ECPCommand, timeout: float | None = None):
    """Enables the engineering mode."""

    await command.actor.engineering_mode(True, timeout=timeout)

    return command.finish(engineering_mode=True)


@engineering_mode.command()
async def disable(command: ECPCommand):
    """Disables the engineering mode."""

    await command.actor.engineering_mode(False)

    return command.finish(engineering_mode=False)


@engineering_mode.command()
async def status(command: ECPCommand):
    """Returns the status of the engineering mode."""

    enabled = command.actor.is_engineering_mode_enabled()
    started_at = command.actor._engineering_mode_started_at
    duration = command.actor._engineering_mode_duration

    if duration is None or started_at is None:
        ends_at = None
    else:
        ends_at = started_at + duration

    return command.finish(
        engineering_mode={
            "enabled": enabled,
            "started_at": timestamp_to_iso(started_at),
            "ends_at": timestamp_to_iso(ends_at),
        }
    )
