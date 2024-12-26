#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2024-12-24
# @Filename: test_command_engineering_mode.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from lvmecp.actor import ECPActor


async def test_command_engineering_mode_status(actor: ECPActor):
    cmd = await actor.invoke_mock_command("engineering-mode status")
    await cmd

    assert cmd.status.did_succeed
    assert cmd.replies.get("engineering_mode")["enabled"] is False


async def test_command_engineering_mode_enable(actor: ECPActor, mocker: MockerFixture):
    eng_mode_mock = mocker.patch.object(actor, "engineering_mode")

    cmd = await actor.invoke_mock_command("engineering-mode enable --timeout 10")
    await cmd

    assert cmd.status.did_succeed
    eng_mode_mock.assert_called_once_with(True, timeout=10)


async def test_command_engineering_mode_no_mock(actor: ECPActor):
    cmd = await actor.invoke_mock_command("engineering-mode enable --timeout 10")
    await cmd

    assert actor.is_engineering_mode_enabled() is True

    cmd = await actor.invoke_mock_command("engineering-mode disable")
    await cmd

    assert actor.is_engineering_mode_enabled() is False


async def test_command_engineering_mode_timeouts(actor: ECPActor):
    actor._engineering_mode_hearbeat_interval = 0.1  # To speed up the test

    cmd = await actor.invoke_mock_command("engineering-mode enable --timeout 0.2")
    await cmd

    assert actor.is_engineering_mode_enabled() is True

    await asyncio.sleep(0.3)

    assert actor.is_engineering_mode_enabled() is False
