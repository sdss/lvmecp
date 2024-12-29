#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2024-12-28
# @Filename: modbus.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING

import click

from . import parser


if TYPE_CHECKING:
    from lvmecp.actor import ECPCommand
    from lvmecp.modbus import ModbusRegister


def get_register(command: ECPCommand, address_or_name: str, register_type: str | None):
    """Returns a register from an address or name."""

    plc = command.actor.plc

    register: ModbusRegister | None = None
    try:
        address = int(address_or_name)  # type: ignore

        if isinstance(address, int) and not register_type:
            command.fail("When passing an address, --register-type must be specified.")
            return False

        for _, reg in plc.modbus.items():
            if reg.address == address:
                register = reg
                break
    except ValueError:
        register = plc.modbus.get(address_or_name)

    if register is None:
        command.fail(f"Register {address_or_name!r} not found.")
        return False

    return register


@parser.group()
def modbus():
    """Low-level access to the PLC Modbus variables."""

    pass


@modbus.command()
@click.argument("address", metavar="ADDRESS|NAME")
@click.option(
    "--register-type",
    type=click.Choice(["coil", "holding_register"]),
    default=None,
    help="The type of register to read. Required if an address is passed.",
)
async def read(command: ECPCommand, address: str, register_type: str | None = None):
    """Reads a Modbus register."""

    if not (register := get_register(command, address, register_type)):
        return False

    value = await register.read(use_cache=False)

    return command.finish(
        register={
            "name": register.name,
            "address": register.address,
            "value": value,
        }
    )


@modbus.command()
@click.argument("address", metavar="ADDRESS|NAME")
@click.argument("value", type=int)
@click.option(
    "--register-type",
    type=click.Choice(["coil", "holding_register"]),
    default=None,
    help="The type of register to read. Required if an address is passed.",
)
async def write(
    command: ECPCommand,
    address: str,
    value: int,
    register_type: str | None = None,
):
    """Writes a value to a Modbus register."""

    if not (register := get_register(command, address, register_type)):
        return False

    name = register.name

    if register.readonly:
        return command.fail(f"Register {name!r} is read-only.")

    if register.mode == "coil":
        value = bool(int(value))
    else:
        value = int(value)

    try:
        await register.write(value)
    except Exception as err:
        return command.fail(f"Error writing to register {name!r}: {err!r}")

    await asyncio.sleep(0.5)
    new_value = await register.read(use_cache=False)

    return command.finish(
        register={
            "name": name,
            "address": register.address,
            "value": new_value,
        }
    )
