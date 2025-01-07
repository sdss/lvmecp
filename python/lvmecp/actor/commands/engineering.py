#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2024-12-24
# @Filename: engineering.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING

import click

from lvmecp.tools import timestamp_to_iso

from . import parser


if TYPE_CHECKING:
    from lvmecp.actor import ECPActor, ECPCommand


async def get_eng_mode_status(actor: ECPActor) -> dict:
    enabled = actor.is_engineering_mode_enabled()
    started_at = actor._engineering_mode_started_at
    duration = actor._engineering_mode_duration

    registers = await actor.plc.read_all_registers(use_cache=False)

    if duration is None or started_at is None:
        ends_at = None
    else:
        ends_at = started_at + duration

    return {
        "enabled": enabled,
        "started_at": timestamp_to_iso(started_at),
        "ends_at": timestamp_to_iso(ends_at),
        "plc_software_override": registers["engineering_mode_software_status"],
        "plc_hardware_override": registers["engineering_mode_hardware_status"],
    }


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
@click.option(
    "--hardware-override",
    is_flag=True,
    help="Sets the hardware override flag.",
)
@click.option(
    "--software-override",
    is_flag=True,
    help="Sets the software override flag.",
)
async def enable(
    command: ECPCommand,
    timeout: float | None = None,
    hardware_override: bool = False,
    software_override: bool = False,
):
    """Enables the engineering mode."""

    modbus = command.actor.plc.modbus

    await command.actor.engineering_mode(True, timeout=timeout)
    await asyncio.sleep(0.5)  # Allow time for the e-mode task to run.

    if hardware_override:
        await modbus.write_register("engineering_mode_hardware_remote", True)
    if software_override:
        await modbus.write_register("engineering_mode_software_remote", True)

    return command.finish(engineering_mode=await get_eng_mode_status(command.actor))


@engineering_mode.command()
async def disable(command: ECPCommand):
    """Disables the engineering mode."""

    modbus = command.actor.plc.modbus

    await command.actor.engineering_mode(False)

    await modbus.write_register("engineering_mode_hardware_remote", False)
    await modbus.write_register("engineering_mode_software_remote", False)

    return command.finish(engineering_mode=await get_eng_mode_status(command.actor))


@engineering_mode.command()
async def status(command: ECPCommand):
    """Returns the status of the engineering mode."""

    return command.finish(engineering_mode=await get_eng_mode_status(command.actor))


@engineering_mode.command()
async def reset_e_stops(command: ECPCommand):
    """Resets the e-stop relays."""

    await command.actor.plc.safety.reset_e_stops()

    return command.finish()
