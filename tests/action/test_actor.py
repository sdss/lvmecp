# encoding: utf-8
#
# test_actor.py

import pytest

from lvmecp.actor.actor import LvmecpTestActor as EcpActor


pytestmark = [pytest.mark.asyncio]


async def test_actor(actor: EcpActor):

    assert actor
    assert len(actor.plcs) == 2


async def test_ping(actor: EcpActor):

    command = await actor.invoke_mock_command("ping")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 2
    assert command.replies[1].message["text"] == "Pong."


async def test_actor_no_config():

    with pytest.raises(RuntimeError):
        EcpActor.from_config(None)
