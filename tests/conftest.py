#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-25
# @Filename: conftest.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import os
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
    await plc_simulator.start(serve_forever=False)

    assert plc_simulator.server and plc_simulator.server.server
    await plc_simulator.server.server.start_serving()

    yield plc_simulator

    await plc_simulator.stop()


@pytest.fixture()
async def actor(simulator: Simulator):

    ecp_config = deepcopy(config)
    ecp_config["plc"]["address"] = "127.0.0.1"

    schema_path = ecp_config["actor"]["schema"]
    ecp_config["actor"]["schema"] = os.path.dirname(lvmecp.__file__) + "/" + schema_path

    _actor = ECPActor.from_config(ecp_config)
    _actor = await setup_test_actor(_actor)  # type: ignore

    yield _actor

    _actor.mock_replies.clear()
    await _actor.stop()
