# encoding: utf-8
#
# test_telemetry.py

from __future__ import annotations

import pytest

from lvmecp.actor.actor import LvmecpTestActor as EcpActor
from lvmecp.exceptions import LvmecpError


pytestmark = [pytest.mark.asyncio]


async def test_telemetry(actor: EcpActor):

    command = await actor.invoke_mock_command("telemetry")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["status"]["emergency"] == 0
    # assert command.replies[-2].message["status"]["Dome"]
    assert command.replies[-1].message["status"]["lights"]["control room"] == 0
    assert command.replies[-1].message["status"]["lights"]["utilities room"] == 0
    assert command.replies[-1].message["status"]["lights"]["spectrograph room"] == 0
    assert command.replies[-1].message["status"]["lights"]["uma lights"] == 0
    assert (
        command.replies[-1].message["status"]["lights"]["telescope room - bright"] == 0
    )
    assert command.replies[-1].message["status"]["lights"]["telescope room - red"] == 0
    assert command.replies[-1].message["status"]["hvac"]["sensor1"]
    assert command.replies[-1].message["status"]["hvac"]["sensor2"]


async def test_telemetry_fails(actor: EcpActor, mocker):

    # mocker.patch.object(actor.plcs[0], "send_command", return_value=None)
    mocker.patch.object(actor.plcs[0], "send_command", side_effect=LvmecpError)

    command = await actor.invoke_mock_command("telemetry")
    await command

    assert command.status.did_fail
