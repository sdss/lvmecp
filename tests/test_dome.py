# encoding: utf-8
#
# test_dome.py

import time

import pytest

from lvmecp.actor.actor import LvmecpActor as EcpActor
from lvmecp.exceptions import LvmecpError


@pytest.mark.asyncio
async def test_dome_status(actor: EcpActor):

    # status check of dome
    command = await actor.invoke_mock_command("dome status")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Dome"] == "CLOSE"


@pytest.mark.asyncio
async def test_dome_enable(actor: EcpActor):

    command = await actor.invoke_mock_command("dome enable")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Dome"] == "OPEN"

    command = await actor.invoke_mock_command("dome status")
    await command

    assert command.status.did_fail

    time.sleep(10)

    command = await actor.invoke_mock_command("dome status")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Dome"] == "OPEN"

    command = await actor.invoke_mock_command("dome enable")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Dome"] == "CLOSE"


@pytest.mark.asyncio
async def test_dome_fail_connect(actor: EcpActor):

    await actor.plcs[0].stop()

    command = await actor.invoke_mock_command("dome status")
    await command

    assert command.status.did_fail


@pytest.mark.asyncio
async def test_dome_fails(actor: EcpActor, mocker):

    # mocker.patch.object(actor.plcs[0], "send_command", return_value=None)
    mocker.patch.object(actor.plcs[0], "send_command", side_effect=LvmecpError)

    command = await actor.invoke_mock_command("dome enable")
    await command

    assert command.status.did_fail
