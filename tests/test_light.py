# encoding: utf-8
#
# test_light.py

import pytest

from lvmecp.actor.actor import lvmecp as EcpActor


@pytest.mark.asyncio
async def test_actor(actor: EcpActor):

    # status check of light
    assert actor
    command = await actor.invoke_mock_command("light status")
    await command
    print(command.replies)
    #assert command.status.did_succeed
    #assert len(command.replies) == 4
    #assert command.replies[-2].message["status"]["nps_dummy_1"]["port1"]["state"] == -1

