#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-25
# @Filename: test_command_lights.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from lvmecp.actor import ECPActor


async def test_command_lights(actor: ECPActor):
    cmd = await actor.invoke_mock_command("lights")
    await cmd

    assert cmd.status.did_succeed
    assert isinstance(cmd.replies.get("lights"), str)


async def test_command_lights_one(actor: ECPActor):
    cmd = await actor.invoke_mock_command("lights on tr")
    await cmd

    assert cmd.status.did_succeed
    assert cmd.replies.get("lights_labels") == "TELESCOPE_RED"


@pytest.mark.parametrize("action", ["on", "off", "toggle"])
@pytest.mark.parametrize("light", ["telescope_bright", "tb", "telescope bright"])
async def test_command_lights_action(actor: ECPActor, action: str, light: str):
    cmd = await actor.invoke_mock_command(f'lights {action} "{light}"')
    await cmd

    assert cmd.status.did_succeed

    if action == "on" or action == "toggle":
        result = True
    else:
        result = False

    if result:
        assert cmd.replies.get("lights_labels") == "TELESCOPE_BRIGHT"
    else:
        assert cmd.replies.get("lights_labels") == ""
