# encoding: utf-8
#
# test_dome.py

import time

import pytest

from lvmecp.actor.actor import LvmecpActor as EcpActor


@pytest.mark.asyncio
async def test_actor(actor: EcpActor):

    assert actor


@pytest.mark.asyncio
async def test_dome_status(actor: EcpActor):

    # status check of dome
    command = await actor.invoke_mock_command("dome status")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Dome"] == "CLOSE"


@pytest.mark.asyncio
async def test_dome_move(actor: EcpActor):

    command = await actor.invoke_mock_command("dome move")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Dome"] == "OPEN"

    command = await actor.invoke_mock_command("dome move")
    await command
    assert command.status.did_fail
    # assert len(command.replies) == 4
    # assert command.replies[-2].message["status"]["Dome"] == "CLOSE"


@pytest.mark.asyncio
async def test_dome_fail_connect(actor: EcpActor):

    await actor.plcs[0].stop()

    command = await actor.invoke_mock_command("dome status")
    await command

    assert command.status.did_fail
