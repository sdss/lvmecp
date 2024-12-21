#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-25
# @Filename: conftest.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
import os
from contextlib import suppress
from copy import deepcopy

import pytest

from clu.testing import setup_test_actor

import lvmecp
from lvmecp import config
from lvmecp.actor import ECPActor
from lvmecp.simulator import Simulator, plc_simulator


@pytest.fixture()
async def simulator():
    plc_simulator.reset()
    simulator_task = asyncio.create_task(plc_simulator.start())

    yield plc_simulator

    await plc_simulator.stop()

    with suppress(asyncio.CancelledError):
        simulator_task.cancel()
        await simulator_task


@pytest.fixture()
async def actor(simulator: Simulator, mocker):
    ecp_config = deepcopy(config)
    ecp_config["modbus"]["host"] = "127.0.0.1"
    ecp_config["modbus"]["port"] = 5020

    schema_path = ecp_config["actor"]["schema"]
    ecp_config["actor"]["schema"] = os.path.dirname(lvmecp.__file__) + "/" + schema_path

    _actor = ECPActor.from_config(ecp_config)

    mocker.patch.object(_actor.plc.hvac.modbus, "get_all", return_value={})

    _actor = await setup_test_actor(_actor)  # type: ignore
    _actor.connection.connection = mocker.MagicMock(spec={"is_closed": False})

    yield _actor

    _actor.mock_replies.clear()
    await _actor.stop()
