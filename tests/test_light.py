# encoding: utf-8
#
# test_light.py

import pytest

from lvmecp.actor.actor import LvmecpActor as EcpActor


@pytest.mark.asyncio
async def test_actor(actor: EcpActor):

    assert actor
    assert len(actor.plcs) == 2


@pytest.mark.asyncio
async def test_light_status(actor: EcpActor):

    # assert controllers[0].name == 'dome'
    # assert controllers[0].result == 1

    # status check of light
    command = await actor.invoke_mock_command("light status")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    # test with CK 20211213
    assert command.replies[-2].message["status"]["Control room"] == 0
    assert command.replies[-2].message["status"]["Utilities room"] == 0
    assert command.replies[-2].message["status"]["Spectrograph room"] == 0
    assert command.replies[-2].message["status"]["UMA lights"] == 0
    assert command.replies[-2].message["status"]["Telescope room - bright"] == 0
    assert command.replies[-2].message["status"]["Telescope room - red"] == 0

    # assert controllers[0].modules[1].name == "lights"
    # assert controllers[0].result == 0

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
async def test_light_enable(actor: EcpActor):

    # on check of light
    command = await actor.invoke_mock_command("light enable cr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Control room"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light enable cr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Control room"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light enable ur")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Utilities room"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light enable ur")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Utilities room"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light enable sr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Spectrograph room"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light enable sr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Spectrograph room"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light enable ur")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Utilities room"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light enable ur")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Utilities room"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light enable uma")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["UMA lights"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light enable uma")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["UMA lights"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light enable tb")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Telescope room - bright"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light enable tb")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Telescope room - bright"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light enable tr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Telescope room - red"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light enable tr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["Telescope room - red"] == 0


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

    command = await actor.invoke_mock_command("light enable")
    await command

    assert command.status.did_fail
