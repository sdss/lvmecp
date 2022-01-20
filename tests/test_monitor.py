# encoding: utf-8
#
# test_monitor.py

import pytest

from lvmecp.actor.actor import LvmecpActor as EcpActor


@pytest.mark.asyncio
async def test_monitor(actor: EcpActor):

    command = await actor.invoke_mock_command("monitor")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["hvac"]["sensor1"]
    assert command.replies[-2].message["status"]["hvac"]["sensor2"]


@pytest.mark.asyncio
async def test_monitor_fail_connect(actor: EcpActor):

    await actor.plcs[1].stop()

    command = await actor.invoke_mock_command("monitor")
    await command

    assert command.status.did_fail


@pytest.mark.asyncio
async def test_monitor_bad_name(actor: EcpActor):

    command = await actor.invoke_mock_command("monitor ar")
    await command

    assert command.status.did_fail
