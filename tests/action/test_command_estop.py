# encoding: utf-8
#
# test_estop.py

import pytest

from lvmecp.actor.actor import LvmecpActor as EcpActor
from lvmecp.exceptions import LvmecpError


"""
@pytest.mark.asyncio
async def test_estop(actor: EcpActor):

    command = await actor.invoke_mock_command("estop")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["emergency"] == 1

    command = await actor.invoke_mock_command("estop")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert isinstance(command.replies[-2].message["text"], str)
"""
