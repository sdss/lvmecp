# encoding: utf-8
#
# test_dome.py

from __future__ import annotations

import time

import pytest

from lvmecp.actor.actor import LvmecpTestActor as EcpActor
from lvmecp.exceptions import LvmecpError


pytestmark = [pytest.mark.asyncio]


async def test_dome_status(actor: EcpActor):

    # status check of dome
    command = await actor.invoke_mock_command("dome status")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["dome"] == "CLOSE"

    # dome_status = command.replies[-1].message["dome"]
    # if dome_status == "CLOSE":
    #    pass
    # elif dome_status == "moving":
    #    pass


async def test_dome_enable(actor: EcpActor):

    command = await actor.invoke_mock_command("dome enable")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["dome"] == "OPEN"

    # dome_status = command.replies[-1].message["dome"]
    # if dome_status == "OPEN":
    #    pass
    # elif dome_status == "moving":
    #    pass

    command = await actor.invoke_mock_command("dome status")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    # assert command.replies[-1].message["dome"] == "OPEN"

    # dome_status = command.replies[-1].message["dome"]
    # if dome_status == "OPEN":
    #    pass
    # elif dome_status == "moving":
    #    pass

    command = await actor.invoke_mock_command("dome enable")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    # assert command.replies[-1].message["dome"] == "CLOSE"

    # dome_status = command.replies[-1].message["dome"]
    # if dome_status == "CLOSE":
    #    pass
    # elif dome_status == "moving":
    #    pass


async def test_dome_enable_fails(actor: EcpActor, mocker):

    # mocker.patch.object(actor.plcs[0], "send_command", return_value=None)
    mocker.patch.object(actor.plcs[0], "send_command", side_effect=LvmecpError)

    command = await actor.invoke_mock_command("dome enable")
    await command

    assert command.status.did_fail


async def test_dome_status_fails(actor: EcpActor, mocker):

    # mocker.patch.object(actor.plcs[0], "send_command", return_value=None)
    mocker.patch.object(actor.plcs[0], "send_command", side_effect=LvmecpError)

    command = await actor.invoke_mock_command("dome status")
    await command

    assert command.status.did_fail


async def test_dome_estop_fail(actor: EcpActor):

    command = await actor.invoke_mock_command("estop")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["emergency"] == 1

    command = await actor.invoke_mock_command("dome status")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["dome"] == "CLOSE"

    command = await actor.invoke_mock_command("dome enable")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 2
    assert isinstance(command.replies[-1].message["text"], str)
