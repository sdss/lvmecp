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
    from pytest_mock import MockerFixture

    from lvmecp.actor import ECPActor


async def test_command_dome_open(actor: ECPActor, mocker: MockerFixture):
    mocker.patch.object(actor.plc.dome, "is_daytime", return_value=False)
    mocker.patch.object(actor.plc.dome, "_move", return_value=True)

    mocker.patch.object(actor.plc.dome, "status", return_value=DomeStatus.OPEN)

    cmd = await actor.invoke_mock_command("dome open")
    await cmd

    assert cmd.status.did_succeed


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
