# encoding: utf-8
#
# test_light.py

import pytest

from lvmecp.actor.actor import LvmecpActor as EcpActor


@pytest.mark.asyncio
async def test_light_status(actor: EcpActor):

    # status check of light
    command = await actor.invoke_mock_command("light status")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Control room"] == 0
    assert command.replies[-2].message["status"]["Utilities room"] == 0
    assert command.replies[-2].message["status"]["Spectrograph room"] == 0
    assert command.replies[-2].message["status"]["UMA lights"] == 0
    assert command.replies[-2].message["status"]["Telescope room - bright"] == 0
    assert command.replies[-2].message["status"]["Telescope room - red"] == 0

    # status check of light
    command = await actor.invoke_mock_command("light status cr")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Control room"] == 0

    # status check of light
    command = await actor.invoke_mock_command("light status ur")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Utilities room"] == 0

    # status check of light
    command = await actor.invoke_mock_command("light status sr")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Spectrograph room"] == 0

    # status check of light
    command = await actor.invoke_mock_command("light status uma")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["UMA lights"] == 0

    # status check of light
    command = await actor.invoke_mock_command("light status tb")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Telescope room - bright"] == 0

    # status check of light
    command = await actor.invoke_mock_command("light status tr")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Telescope room - red"] == 0

@pytest.mark.asyncio
async def test_light_move(actor: EcpActor):

    # on check of light
    command = await actor.invoke_mock_command("light move cr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    #assert command.replies[-2].message["status"]["Control room"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light move cr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    #assert command.replies[-2].message["status"]["Control room"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light move ur")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    #assert command.replies[-2].message["status"]["Utilities room"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light move ur")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    #assert command.replies[-2].message["status"]["Utilities room"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light move sr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    #assert command.replies[-2].message["status"]["Spectrograph room"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light move sr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    #assert command.replies[-2].message["status"]["Spectrograph room"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light move ur")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    #assert command.replies[-2].message["status"]["Utilities room"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light move ur")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    #assert command.replies[-2].message["status"]["Utilities room"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light move uma")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    #assert command.replies[-2].message["status"]["UMA lights"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light move uma")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    #assert command.replies[-2].message["status"]["UMA lights"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light move tb")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    #assert command.replies[-2].message["status"]["Telescope room - bright"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light move tb")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    #assert command.replies[-2].message["status"]["Telescope room - bright"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light move tr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    #assert command.replies[-2].message["status"]["Telescope room - red"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light move tr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    #assert command.replies[-2].message["status"]["Telescope room - red"] == 0


@pytest.mark.asyncio
async def test_light_fail_bad_name(actor: EcpActor):

    command = await actor.invoke_mock_command("light status ar")
    await command

    assert command.status.did_fail

@pytest.mark.asyncio
async def test_light_fail_bad_connect(actor: EcpActor):

    await actor.plcs[0].stop()

    command = await actor.invoke_mock_command("light status cr")
    await command

    assert command.status.did_fail

@pytest.mark.asyncio
async def test_light_fail_no_argument(actor: EcpActor):

    command = await actor.invoke_mock_command("light move")
    await command

    assert command.status.did_fail
