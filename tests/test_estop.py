# encoding: utf-8
#
# test_estop.py

import pytest

from lvmecp.actor.actor import LvmecpActor as EcpActor


@pytest.mark.asyncio
async def test_estop_status(actor: EcpActor):

    command = await actor.invoke_mock_command("estop status")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["emergency"]["E_status"] == 0

@pytest.mark.asyncio
async def test_estop_trigger(actor: EcpActor):

    command = await actor.invoke_mock_command("estop trigger")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["emergency"]["E_status"] == 1

    command = await actor.invoke_mock_command("estop stop")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["emergency"]["E_status"] == 0

@pytest.mark.asyncio
async def test_estop_fail_connect(actor: EcpActor):

    await actor.plcs[0].stop()

    command = await actor.invoke_mock_command("estop status")
    await command

    assert command.status.did_fail
