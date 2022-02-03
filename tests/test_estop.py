# encoding: utf-8
#
# test_estop.py

import pytest

from lvmecp.actor.actor import LvmecpActor as EcpActor
from lvmecp.exceptions import LvmecpError


@pytest.mark.asyncio
async def test_estop(actor: EcpActor):

    command = await actor.invoke_mock_command("estop")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["emergency"]["E_status"] == 1

    command = await actor.invoke_mock_command("estop")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert isinstance(command.replies[-2].message["text"], str)


@pytest.mark.asyncio
async def test_estop_fail_connect(actor: EcpActor):

    await actor.plcs[0].stop()

    command = await actor.invoke_mock_command("estop")
    await command

    assert command.status.did_fail


@pytest.mark.asyncio
async def test_estop_fails(actor: EcpActor, mocker):

    # mocker.patch.object(actor.plcs[0], "send_command", return_value=None)
    mocker.patch.object(actor.plcs[0], "send_command", side_effect=LvmecpError)

    command = await actor.invoke_mock_command("estop")
    await command

    assert command.status.did_fail
