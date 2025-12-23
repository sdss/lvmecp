#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-25
# @Filename: test_command_status.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from lvmecp.actor import ECPActor


async def test_command_status(actor: ECPActor):
    cmd = await actor.invoke_mock_command("status")
    await cmd

    assert cmd.status.did_succeed
    assert isinstance(cmd.replies.get("registers"), dict)
    assert cmd.replies.get("register_overrides") == []
