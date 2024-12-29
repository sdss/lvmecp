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


def get_register(command: ECPCommand, address_or_name: str):
    """Returns a register from an address or name."""

    plc = command.actor.plc

    register: ModbusRegister | None = None
    try:
        address = int(address_or_name)  # type: ignore
        for _, reg in plc.modbus.items():
            if reg.address == address:
                register = reg
                break
    except ValueError:
        register = plc.modbus.get(address_or_name)

    if register is None:
        command.fail(f"Register {address!r} not found.")
        return False

    return register


@parser.group()
def modbus():
    """Low-level access to the PLC Modbus variables."""

    pass


@modbus.command()
@click.argument("address", metavar="ADDRESS|NAME")
async def read(command: ECPCommand, address: str):
    """Reads a Modbus register."""

    if not (register := get_register(command, address)):
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
async def write(command: ECPCommand, address: str, value: int):
    """Writes a value to a Modbus register."""

    if not (register := get_register(command, address)):
        return False

    name = register.name

    if register.readonly:
        return command.fail(f"Register {name!r} is read-only.")

    if register.mode == "coil":
        try:
            value = bool(int(value))
        except Exception:
            return command.fail(f"Invalid value for coil register {name!r}: {value!r}")
        else:
            value = int(value)

    await register.write(value)

    await asyncio.sleep(0.5)
    new_value = await register.read(use_cache=False)

    return command.finish(
        register={
            "name": name,
            "address": register.address,
            "value": new_value,
        }
    )
