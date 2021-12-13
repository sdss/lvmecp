# encoding: utf-8
#
# test_estop.py

import pytest

from lvmecp.actor.actor import LvmecpActor as EcpActor

@pytest.mark.asyncio
async def test_estop(actor: EcpActor):

    command = await actor.invoke_mock_command("estop")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["emergency"]["E_stop"] == 0
    assert command.replies[-2].message["status"]["emergency"]["E_status"] == 0
    assert command.replies[-2].message["status"]["emergency"]["E_relay"] == 0

@pytest.mark.asyncio
async def test_estop_fail_connect(actor: EcpActor):
    
    await actor.plcs[0].stop()
    
    command = await actor.invoke_mock_command("estop")
    await command

    assert command.status.did_fail
