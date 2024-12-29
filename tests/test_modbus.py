#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2024-12-29
# @Filename: test_modbus.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING, cast

import pytest
from pytest_mock import MockerFixture

import lvmecp.modbus
from lvmecp.modbus import ModbusRegister, RegisterModes


if TYPE_CHECKING:
    from pymodbus.datastore import ModbusSlaveContext

    from lvmecp.modbus import Modbus


async def test_modbus_read(modbus: Modbus):
    resp = await modbus.read_register("door_locked")
    assert resp == 1


@pytest.mark.parametrize(
    "register_type",
    ["coil", "discrete_input", "input_register", "holding_register"],
)
async def test_modbus_register_read(
    context: ModbusSlaveContext,
    modbus: Modbus,
    register_type: str,
):
    is_discrete = register_type in ["coil", "discrete_input"]

    write_func_code = 1
    if register_type == "discrete_input":
        write_func_code = 2
    elif register_type == "holding_register":
        write_func_code = 3
    elif register_type == "input_register":
        write_func_code = 4

    context.setValues(write_func_code, 99, [1 if is_discrete else 101])

    register = ModbusRegister(
        modbus,
        name="test_register",
        address=99,
        mode=cast(RegisterModes, register_type),
        count=1,
        readonly=True,
    )

    resp = await register.read(use_cache=False)
    assert resp == (1 if is_discrete else 101)


async def test_modbus_register_read_decoder_float_32bit(
    context: ModbusSlaveContext,
    modbus: Modbus,
):
    context.setValues(3, 99, [4000, 16000])

    register = ModbusRegister(
        modbus,
        name="test_register",
        address=99,
        mode="holding_register",
        count=2,
        readonly=True,
        decoder="float_32bit",
    )

    resp = await register.read(use_cache=False)

    assert resp == 0.250


@pytest.mark.parametrize("register_type", ["coil", "holding_register"])
async def test_modbus_register_write(
    context: ModbusSlaveContext,
    modbus: Modbus,
    register_type: str,
):
    is_discrete = register_type in ["coil", "discrete_input"]
    write_func_code = 1 if is_discrete else 3

    register = ModbusRegister(
        modbus,
        name="test_register",
        address=99,
        mode=cast(RegisterModes, register_type),
        count=1,
        readonly=False,
    )

    await register.write(1 if is_discrete else 101)

    value = context.getValues(write_func_code, 99)
    assert value[0] == (1 if is_discrete else 101)


@pytest.mark.parametrize("register_type", ["discrete_input", "input_register"])
async def test_modbus_register_write_on_readonly(modbus: Modbus, register_type: str):
    register = ModbusRegister(
        modbus,
        name="test_register",
        address=99,
        mode=cast(RegisterModes, register_type),
        count=1,
        readonly=False,
    )

    with pytest.raises(ValueError) as err:
        await register.write(1)

    assert "is read-only" in str(err.value)


async def test_modbus_connection_fails(modbus: Modbus, mocker: MockerFixture):
    mocker.patch.object(modbus.client, "connect", side_effect=ConnectionError)

    with pytest.raises(ConnectionError):
        await modbus.read_register("door_locked")


async def test_modbus_connection_timeouts(modbus: Modbus, mocker: MockerFixture):
    mocker.patch.object(modbus.client, "connect", side_effect=asyncio.TimeoutError)

    with pytest.raises(ConnectionError):
        await modbus.read_register("door_locked")


async def test_modbus_lock_release(modbus: Modbus, mocker: MockerFixture):
    mocker.patch.object(lvmecp.modbus, "CONNECTION_TIMEOUT", 0.1)

    async with modbus:
        assert modbus.client.connected
        assert modbus.lock.locked()

        await asyncio.sleep(0.2)

        assert not modbus.client.connected
        assert not modbus.lock.locked()
