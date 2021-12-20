# encoding: utf-8
#
# test_dome.py

import pytest

from lvmecp.actor.actor import LvmecpActor as EcpActor


@pytest.mark.asyncio
async def test_actor(actor: EcpActor):

    assert actor


#@pytest.mark.asyncio
#async def test_dome_status(actor: EcpActor):

    # status check of dome
#    command = await actor.invoke_mock_command("dome status")
#    await command

#    assert command.status.did_succeed
#    assert len(command.replies) == 4
#    assert command.replies[-2].message["status"]["Dome"]["enable"] == 0
#    assert command.replies[-2].message["status"]["Dome"]["drive"] == 0


# @pytest.mark.asyncio
# async def test_dome_move(actor: EcpActor):

# on check of light
# assert controllers[0].name == 'dome'

# command = await actor.invoke_mock_command("dome move")
# await command
# assert command.status.did_succeed
# assert len(command.replies) == 4
# assert command.replies[-2].message["status"]["Dome"]["enable"] == 1
# assert command.replies[-2].message["status"]["Dome"]["drive"] == 1

# off check of light
# command = await actor.invoke_mock_command("dome move")
# await command
# assert command.status.did_succeed
# assert len(command.replies) == 4
# assert command.replies[-2].message["status"]["Dome"]["enable"] == 0
# assert command.replies[-2].message["status"]["Dome"]["drive"] == 0


#@pytest.mark.asyncio
#async def test_dome_fail_connect(actor: EcpActor):

#    await actor.plcs[0].stop()

#    command = await actor.invoke_mock_command("dome status")
#    await command

#    assert command.status.did_fail
