# encoding: utf-8
#
# test_monitor.py

from __future__ import annotations

import pytest

from lvmecp.actor.actor import LvmecpTestActor as EcpActor
from lvmecp.exceptions import LvmecpError


pytestmark = [pytest.mark.asyncio]


async def test_monitor(actor: EcpActor):

    command = await actor.invoke_mock_command("monitor")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3


async def test_monitor_bad_name(actor: EcpActor):

    command = await actor.invoke_mock_command("monitor ar")
    await command

    assert command.status.did_fail


async def test_monitor_fails(actor: EcpActor, mocker):

    # mocker.patch.object(actor.plcs[0], "send_command", return_value=None)
    mocker.patch.object(actor.plcs[1], "send_command", side_effect=LvmecpError)

    command = await actor.invoke_mock_command("monitor")
    await command

    assert command.status.did_fail
