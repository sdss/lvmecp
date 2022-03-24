# encoding: utf-8
#
# test_telemetry.py

from __future__ import annotations

import pytest

from lvmecp.actor.actor import LvmecpActor as EcpActor


@pytest.mark.asyncio
async def test_telemetry(actor: EcpActor):

    command = await actor.invoke_mock_command("telemetry")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 3
    assert command.replies[-1].message["status"]["emergency"] == 0
    # assert command.replies[-2].message["status"]["Dome"]
    assert command.replies[-1].message["status"]["lights"]["Control room"] == 0
    assert command.replies[-1].message["status"]["lights"]["Utilities room"] == 0
    assert command.replies[-1].message["status"]["lights"]["Spectrograph room"] == 0
    assert command.replies[-1].message["status"]["lights"]["UMA lights"] == 0
    assert (
        command.replies[-1].message["status"]["lights"]["Telescope room - bright"] == 0
    )
    assert command.replies[-1].message["status"]["lights"]["Telescope room - red"] == 0
    assert command.replies[-1].message["status"]["hvac"]["sensor1"]
    assert command.replies[-1].message["status"]["hvac"]["sensor2"]


# @pytest.mark.asyncio
# async def test_telemetry_fail_connect(actor: EcpActor):

# await actor.plcs[0].stop()

# command = await actor.invoke_mock_command("telemetry")
# await command

# assert command.status.did_fail