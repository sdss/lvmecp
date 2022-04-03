# encoding: utf-8
#
# test_light.py

from __future__ import annotations

import pytest

from lvmecp.actor.actor import LvmecpTestActor as EcpActor
from lvmecp.exceptions import LvmecpError


pytestmark = [pytest.mark.asyncio]


async def test_light_status(actor: EcpActor):

    # status check of light
    command = await actor.invoke_mock_command("light status")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["control room"] == 0
    assert command.replies[-1].message["light"]["utilities room"] == 0
    assert command.replies[-1].message["light"]["spectrograph room"] == 0
    assert command.replies[-1].message["light"]["uma lights"] == 0
    assert command.replies[-1].message["light"]["telescope room - bright"] == 0
    assert command.replies[-1].message["light"]["telescope room - red"] == 0

    # status check of light
    command = await actor.invoke_mock_command("light status cr")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["control room"] == 0

    # status check of light
    command = await actor.invoke_mock_command("light status ur")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["utilities room"] == 0

    # status check of light
    command = await actor.invoke_mock_command("light status sr")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["spectrograph room"] == 0

    # status check of light
    command = await actor.invoke_mock_command("light status uma")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["uma lights"] == 0

    # status check of light
    command = await actor.invoke_mock_command("light status tb")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["telescope room - bright"] == 0

    # status check of light
    command = await actor.invoke_mock_command("light status tr")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["telescope room - red"] == 0


async def test_light_enable(actor: EcpActor):

    # on check of light
    command = await actor.invoke_mock_command("light enable cr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["control room"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light enable cr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["control room"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light enable ur")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["utilities room"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light enable ur")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["utilities room"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light enable sr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["spectrograph room"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light enable sr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["spectrograph room"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light enable uma")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["uma lights"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light enable uma")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["uma lights"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light enable tb")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["telescope room - bright"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light enable tb")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["telescope room - bright"] == 0

    # on check of light
    command = await actor.invoke_mock_command("light enable tr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["telescope room - red"] == 1

    # off check of light
    command = await actor.invoke_mock_command("light enable tr")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["light"]["telescope room - red"] == 0


async def test_light_fail_bad_name(actor: EcpActor):

    command = await actor.invoke_mock_command("light status ar")
    await command

    assert command.status.did_fail


async def test_light_fail_no_argument(actor: EcpActor):

    command = await actor.invoke_mock_command("light enable")
    await command

    assert command.status.did_fail


async def test_light_estop_fail(actor: EcpActor):

    command = await actor.invoke_mock_command("estop")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["emergency"] == 1

    command = await actor.invoke_mock_command("light status")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3

    command = await actor.invoke_mock_command("light enable cr")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert isinstance(command.replies[-2].message["text"], str)


async def test_light_status_fails(actor: EcpActor, mocker):

    # mocker.patch.object(actor.plcs[0], "send_command", return_value=None)
    mocker.patch.object(actor.plcs[0], "send_command", side_effect=LvmecpError)

    command = await actor.invoke_mock_command("light status")
    await command

    assert command.status.did_fail


async def test_light_enable_fails(actor: EcpActor, mocker):

    # mocker.patch.object(actor.plcs[0], "send_command", return_value=None)
    mocker.patch.object(actor.plcs[0], "send_command", side_effect=LvmecpError)

    command = await actor.invoke_mock_command("light enable cr")
    await command

    assert command.status.did_fail
