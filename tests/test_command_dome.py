#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2024-12-24
# @Filename: test_command_dome.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import TYPE_CHECKING

from lvmecp.maskbits import DomeStatus


if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from lvmecp.actor import ECPActor


async def test_command_dome_open(actor: ECPActor, mocker: MockerFixture):
    mocker.patch.object(actor.plc.dome, "is_allowed", return_value=True)
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


async def test_command_dome_daytime_eng_mode(actor: ECPActor, mocker: MockerFixture):
    mocker.patch.object(actor.plc.dome, "is_daytime", return_value=True)
    mocker.patch.object(actor.plc.dome, "_move", return_value=True)
    mocker.patch.object(actor, "_engineering_mode", return_value=True)

    mocker.patch.object(actor.plc.dome, "status", return_value=DomeStatus.OPEN)

    cmd = await actor.invoke_mock_command("dome open")
    await cmd

    assert cmd.status.did_succeed
