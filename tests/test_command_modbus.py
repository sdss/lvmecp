#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2024-12-28
# @Filename: test_command_modbus.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_mock import MockerFixture


if TYPE_CHECKING:
    from lvmecp.actor import ECPActor


async def test_command_modbus_read(actor: ECPActor):
    read_cmd = await actor.invoke_mock_command("modbus read door_locked")
    await read_cmd

    assert read_cmd.status.did_succeed
    assert read_cmd.replies.get("register")["value"]


async def test_command_modbus_read_address(actor: ECPActor):
    read_cmd = await actor.invoke_mock_command("modbus read --register-type coil 1")
    await read_cmd

    assert read_cmd.status.did_succeed

    assert read_cmd.replies.get("register")["name"] == "door_closed"
    assert read_cmd.replies.get("register")["value"]


async def test_command_modbus_read_address_no_register_type(actor: ECPActor):
    read_cmd = await actor.invoke_mock_command("modbus read 1")
    await read_cmd

    assert read_cmd.status.did_fail

    assert "--register-type must be specified" in read_cmd.replies.get("error")


async def test_command_modbus_read_bad_register(actor: ECPActor):
    read_cmd = await actor.invoke_mock_command("modbus read bad_register")
    await read_cmd

    assert read_cmd.status.did_fail

    assert "not found" in read_cmd.replies.get("error")


async def test_modbus_write_register(actor: ECPActor):
    pre_value = await actor.plc.modbus["motor_direction"].read(use_cache=False)
    assert pre_value == 0

    write_cmd = await actor.invoke_mock_command("modbus write motor_direction 1")
    await write_cmd

    assert write_cmd.status.did_succeed

    new_value = await actor.plc.modbus["motor_direction"].read(use_cache=False)
    assert new_value == 1


async def test_modbus_write_register_readonly(actor: ECPActor):
    write_cmd = await actor.invoke_mock_command("modbus write door_locked 1")
    await write_cmd

    assert write_cmd.status.did_fail
    assert "is read-only" in write_cmd.replies.get("error")


async def test_modbus_write_register_fails(actor: ECPActor, mocker: MockerFixture):
    mocker.patch.object(
        actor.plc.modbus["motor_direction"],
        "write",
        side_effect=ValueError("cannot write"),
    )

    write_cmd = await actor.invoke_mock_command("modbus write motor_direction 1")
    await write_cmd

    assert write_cmd.status.did_fail
    assert "cannot write" in write_cmd.replies.get("error")
