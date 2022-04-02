#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2022-03-31
# @Filename: conftest.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import os
import sys
import types
from functools import partial
from unittest.mock import MagicMock

import clu.testing
import pytest
from clu import AMQPClient
from clu.actor import AMQPActor

from sdsstools import merge_config, read_yaml_file
from sdsstools.logger import get_logger

from lvmecp import config
from lvmecp.actor import LvmecpTestActor as ECPActor
from lvmecp.controller.testing import TestPlcController


if sys.version_info.major < 3:
    raise ValueError("Python 2 is not supported.")
if sys.version_info.minor <= 7:
    from asyncmock import AsyncMock
else:
    from unittest.mock import AsyncMock


@pytest.fixture()
async def test_config():

    extra = read_yaml_file(os.path.join(os.path.dirname(__file__), "test_lvmecp.yml"))
    yield merge_config(extra, config)


@pytest.fixture()
async def actor(test_config: dict, mocker):

    _actor = ECPActor.from_config(test_config)
    await _actor.start()

    _actor = await clu.testing.setup_test_actor(_actor)  # type: ignore

    yield _actor

    _actor.mock_replies.clear()
    await _actor.stop()
