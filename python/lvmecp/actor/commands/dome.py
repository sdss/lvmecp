#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2023-05-23
# @Filename: dome.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import TYPE_CHECKING

import click

from lvmecp.exceptions import DomeError
from lvmecp.maskbits import DomeStatus

from . import parser


if TYPE_CHECKING:
    from lvmecp.actor import ECPCommand


__all__ = ["dome"]


@parser.group()
def dome():
    """Commands the dome."""

    return


@dome.command()
@click.option("--force", is_flag=True, help="Force dome opening.")
async def open(command: ECPCommand, force=False):
    """Opens the dome."""

    command.info("Opening dome.")

    try:
        await command.actor.plc.dome.open(force=force)
    except DomeError as err:
        return command.fail(f"Dome failed to open with error: {err}")

    status = command.actor.plc.dome.status
    if status and status & DomeStatus.OPEN:
        return command.finish(text="Dome is now open.")
    else:
        return command.fail(text="Dome was left in an unknown state.")


@dome.command()
@click.option("--force", is_flag=True, help="Force dome closing.")
async def close(command: ECPCommand, force=False):
    """Closes the dome."""

    command.info("Closing dome.")

    try:
        await command.actor.plc.dome.close(force=force)
    except DomeError as err:
        return command.fail(f"Dome failed to close with error: {err}")

    status = command.actor.plc.dome.status
    if status and status & DomeStatus.CLOSED:
        return command.finish(text="Dome is now closed.")
    else:
        return command.fail(text="Dome was left in an unknown state.")


@dome.command()
async def status(command: ECPCommand):
    """Returns the status of the dome."""

    status = await command.actor.plc.dome.update(
        use_cache=False,
        force_output=True,
        command=command,
    )

    if status is None:
        return command.fail("Failed retrieving dome status.")

    if status & DomeStatus.MOVING:
        command.warning("Dome is moving!!!")

    if status & DomeStatus.POSITION_UNKNOWN:
        command.warning("Dome position is unknown!!!")

    return command.finish()


@dome.command()
async def stop(command: ECPCommand):
    """Stops the dome if it's moving."""

    command.warning("Stopping the dome.")
    await command.actor.plc.dome.stop()

    return command.finish()


@dome.command()
async def reset(command: ECPCommand, force=False):
    """Resets dome error state."""

    command.warning("Resetting dome error state.")
    await command.actor.plc.dome.reset()

    return command.finish()
