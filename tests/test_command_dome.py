#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2024-12-24
# @Filename: test_command_dome.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING

import pytest

import lvmecp.actor.actor
import lvmecp.dome
from lvmecp.exceptions import DomeError
from lvmecp.maskbits import DomeStatus


if TYPE_CHECKING:
    from pymodbus.datastore import ModbusSlaveContext
    from pytest_mock import MockerFixture

    from lvmecp.actor import ECPActor


@pytest.mark.parametrize("open", [True, False])
async def test_command_dome_status(
    context: ModbusSlaveContext,
    actor: ECPActor,
    open: bool,
):
    if open:
        address = actor.plc.modbus["dome_open"].address
    else:
        address = actor.plc.modbus["dome_closed"].address

    context.setValues(1, address, [1])

    cmd = await actor.invoke_mock_command("dome status")
    await cmd

    assert cmd.status.did_succeed


async def test_command_dome_moving(context: ModbusSlaveContext, actor: ECPActor):
    address = actor.plc.modbus["drive_enabled"].address

    context.setValues(1, address, [1])

    cmd = await actor.invoke_mock_command("dome status")
    await cmd

    assert cmd.status.did_succeed
    text = cmd.replies.get("text")
    assert text == "Dome is moving!!!"


async def test_command_dome_position_unknown(
    context: ModbusSlaveContext,
    actor: ECPActor,
):
    context.setValues(1, actor.plc.modbus["dome_closed"].address, [0])

    cmd = await actor.invoke_mock_command("dome status")
    await cmd

    assert cmd.status.did_succeed
    text = cmd.replies.get("text")
    assert text == "Dome position is unknown!!!"


async def test_command_dome_stop(actor: ECPActor):
    await actor.plc.modbus["drive_enabled"].write(1)

    cmd = await actor.invoke_mock_command("dome stop")
    await cmd

    assert cmd.status.did_succeed

    assert (await actor.plc.modbus["drive_enabled"].read(use_cache=False)) == 0


async def test_command_dome_reset(context: ModbusSlaveContext, actor: ECPActor):
    context.setValues(1, actor.plc.modbus["dome_error"].address, [1])

    cmd = await actor.invoke_mock_command("dome reset")
    await cmd

    assert cmd.status.did_succeed

    assert (await actor.plc.modbus["dome_error"].read(use_cache=False)) == 0


async def test_command_dome_open_mock(actor: ECPActor, mocker: MockerFixture):
    mocker.patch.object(actor.plc.dome, "is_daytime", return_value=False)
    mocker.patch.object(actor.plc.dome, "_move", return_value=True)

    mocker.patch.object(actor.plc.dome, "status", return_value=DomeStatus.OPEN)

    cmd = await actor.invoke_mock_command("dome open")
    await cmd

    assert cmd.status.did_succeed


async def test_command_dome_open(
    actor: ECPActor,
    context: ModbusSlaveContext,
    mocker: MockerFixture,
):
    async def open_with_delay():
        context.setValues(1, actor.plc.modbus["dome_closed"].address, [0])

        await asyncio.sleep(0.3)

        context.setValues(1, actor.plc.modbus["dome_open"].address, [1])
        context.setValues(1, actor.plc.modbus["drive_enabled"].address, [0])

    mocker.patch.object(actor.plc.dome, "is_daytime", return_value=False)
    mocker.patch.object(lvmecp.dome, "MOVE_CHECK_INTERVAL", 0.1)

    cmd = await actor.invoke_mock_command("dome open")

    await asyncio.sleep(0.1)
    asyncio.create_task(open_with_delay())

    await cmd

    assert cmd.status.did_succeed

    assert (await actor.plc.modbus["drive_enabled"].read(use_cache=False)) == 0
    assert (await actor.plc.modbus["dome_open"].read(use_cache=False)) == 1


async def test_command_dome_close(actor: ECPActor, mocker: MockerFixture):
    mocker.patch.object(actor.plc.dome, "_move", return_value=True)

    mocker.patch.object(actor.plc.dome, "status", return_value=DomeStatus.CLOSED)

    cmd = await actor.invoke_mock_command("dome close")
    await cmd

    assert cmd.status.did_succeed


async def test_command_dome_daytime(actor: ECPActor, mocker: MockerFixture):
    mocker.patch.object(actor.plc.dome, "is_daytime", return_value=True)
    mocker.patch.object(actor.plc.dome, "_move", return_value=True)

    cmd = await actor.invoke_mock_command("dome open")
    await cmd

    assert cmd.status.did_fail


async def test_command_dome_daytime_allowed(actor: ECPActor, mocker: MockerFixture):
    mocker.patch.dict(
        "lvmecp.dome.config",
        {
            "dome": {
                "daytime_allowed": True,
                "anti_flap_tolerance": [3, 600],
            }
        },
    )

    mocker.patch.object(actor.plc.dome, "is_daytime", return_value=True)
    mocker.patch.object(actor.plc.dome, "_move", return_value=True)

    mocker.patch.object(actor.plc.dome, "status", return_value=DomeStatus.OPEN)

    cmd = await actor.invoke_mock_command("dome open")
    await cmd

    assert cmd.status.did_succeed


async def test_command_dome_daytime_eng_mode(actor: ECPActor, mocker: MockerFixture):
    mocker.patch.object(actor.plc.dome, "is_daytime", return_value=True)
    mocker.patch.object(actor.plc.dome, "_move", return_value=True)
    mocker.patch.object(actor, "_engineering_mode", return_value=True)

    mocker.patch.object(actor.plc.dome, "status", return_value=DomeStatus.OPEN)

    cmd = await actor.invoke_mock_command("dome open")
    await cmd

    assert cmd.status.did_succeed


async def test_actor_daytime_task(actor: ECPActor, mocker: MockerFixture):
    mocker.patch.object(actor.plc.dome, "is_daytime", return_value=True)
    mocker.patch.object(lvmecp.actor.actor, "send_notification")

    dome_close_mock = mocker.patch.object(actor.plc.dome, "close")

    task = asyncio.create_task(actor.monitor_dome(delay=0.1))
    await asyncio.sleep(0.2)

    dome_close_mock.assert_called()

    task.cancel()


async def test_actor_daytime_task_closed(actor: ECPActor, mocker: MockerFixture):
    mocker.patch.object(actor.plc.dome, "is_daytime", return_value=True)
    mocker.patch.object(actor.plc.dome, "status", return_value=DomeStatus.CLOSED)
    mocker.patch.object(lvmecp.actor.actor, "send_notification")

    dome_close_mock = mocker.patch.object(actor.plc.dome, "close")

    task = asyncio.create_task(actor.monitor_dome(delay=0.1))
    await asyncio.sleep(0.2)

    dome_close_mock.assert_not_called()

    task.cancel()


async def test_actor_daytime_task_eng_mode(actor: ECPActor, mocker: MockerFixture):
    mocker.patch.object(actor.plc.dome, "is_daytime", return_value=True)
    mocker.patch.object(actor, "_engineering_mode", return_value=True)
    mocker.patch.object(lvmecp.actor.actor, "send_notification")

    dome_close_mock = mocker.patch.object(actor.plc.dome, "close")

    task = asyncio.create_task(actor.monitor_dome(delay=0.1))
    await asyncio.sleep(0.2)

    dome_close_mock.assert_not_called()

    task.cancel()


async def test_dome_anti_flap(actor: ECPActor, mocker: MockerFixture):
    mocker.patch.dict("lvmecp.dome.config", {"dome": {"anti_flap_tolerance": [3, 1]}})

    mocker.patch.object(actor.plc.dome, "is_daytime", return_value=False)
    mocker.patch.object(actor.plc.dome, "_move", return_value=True)

    await actor.plc.dome.open()
    await asyncio.sleep(0.1)

    await actor.plc.dome.open()
    await asyncio.sleep(0.1)

    with pytest.raises(DomeError):
        await actor.plc.dome.open()
        await asyncio.sleep(0.1)


async def test_dome_not_allowed(actor: ECPActor, mocker: MockerFixture):
    mocker.patch.object(actor.plc.dome, "is_allowed", return_value=False)

    with pytest.raises(DomeError, match="Dome is not allowed to open."):
        await actor.plc.dome.open()
