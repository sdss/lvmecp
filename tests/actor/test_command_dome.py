# encoding: utf-8
#
# test_dome.py

from __future__ import annotations

import time

import pytest

from lvmecp.actor.actor import LvmecpActor as EcpActor
from lvmecp.exceptions import LvmecpError


pytestmark = [pytest.mark.asyncio]


async def test_dome_status(actor: EcpActor):

    # status check of dome
    command = await actor.invoke_mock_command("dome status")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    dome_status = command.replies[-1].message["dome"]
    if dome_status == "CLOSE":
        pass
    elif dome_status == "moving":
        time.sleep(10)
        command = await actor.invoke_mock_command("dome status")
        await command

        assert command.status.did_succeed
        assert len(command.replies) == 3
        assert command.replies[-1].message["dome"] == "CLOSE"
        pass


async def test_dome_enable(actor: EcpActor):

    command = await actor.invoke_mock_command("dome enable")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    dome_status = command.replies[-1].message["dome"]
    if dome_status == "OPEN":
        pass
    elif dome_status == "moving":
        time.sleep(10)
        command = await actor.invoke_mock_command("dome enable")
        await command
        assert command.status.did_succeed
        assert len(command.replies) == 3
        assert command.replies[-1].message["dome"] == "OPEN"

    command = await actor.invoke_mock_command("dome status")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    dome_status = command.replies[-1].message["dome"]
    if dome_status == "OPEN":
        pass
    elif dome_status == "moving":
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
