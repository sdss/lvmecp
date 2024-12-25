#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2024-12-24
# @Filename: test_command_heartbeat.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from lvmecp.actor import ECPActor


async def test_command_heartbeat(actor: ECPActor, mocker: MockerFixture):
    hb_set_mock = mocker.patch.object(actor.plc.modbus["hb_set"], "set")

    cmd = await actor.invoke_mock_command("heartbeat")
    await cmd

    assert cmd.status.did_succeed

    hb_set_mock.assert_called_once_with(True)


async def test_command_heartbeat_fails(actor: ECPActor, mocker: MockerFixture):
    mocker.patch.object(actor.plc.modbus["hb_set"], "set", side_effect=Exception)

    cmd = await actor.invoke_mock_command("heartbeat")
    await cmd

    assert cmd.status.did_fail
