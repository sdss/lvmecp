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
    assert isinstance(cmd.replies.get("lights"), dict)


async def test_command_lights_one(actor: ECPActor):
    cmd = await actor.invoke_mock_command("lights tr")
    await cmd

    assert cmd.status.did_succeed
    assert cmd.replies.get("lights") == {"telescope_red": False}


@pytest.mark.parametrize("action", ["on", "off", "switch"])
@pytest.mark.parametrize("light", ["telescope_bright", "tb", "telescope bright"])
async def test_command_lights_action(actor: ECPActor, action: str, light: str):
    cmd = await actor.invoke_mock_command(f'lights "{light}" {action}')
    await cmd

    assert cmd.status.did_succeed

    if action == "on" or action == "switch":
        result = True
    else:
        result = False

    assert cmd.replies.get("lights") == {"telescope_bright": result}
