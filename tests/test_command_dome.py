# encoding: utf-8
#
# test_dome.py

from __future__ import annotations

import time

import pytest

from lvmecp.actor.actor import LvmecpActor as EcpActor
from lvmecp.exceptions import LvmecpError


@pytest.mark.asyncio
async def test_dome_status(actor: EcpActor):

    time.sleep(10)

    # status check of dome
    command = await actor.invoke_mock_command("dome status")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["dome"] == "CLOSE"


@pytest.mark.asyncio
async def test_dome_enable(actor: EcpActor):

    time.sleep(10)

    command = await actor.invoke_mock_command("dome enable")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["dome"] == "OPEN"

    command = await actor.invoke_mock_command("dome status")
    await command

    assert command.status.did_fail

    time.sleep(10)

    command = await actor.invoke_mock_command("dome status")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["dome"] == "OPEN"

    command = await actor.invoke_mock_command("dome enable")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["dome"] == "CLOSE"
