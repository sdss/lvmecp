# encoding: utf-8
#
# conftest.py

"""
Here you can add fixtures that will be used for all the tests in this
directory. You can also add conftest.py files in underlying subdirectories.
Those conftest.py will only be applies to the tests in that subdirectory and
underlying directories. See https://docs.pytest.org/en/2.7.3/plugins.html for
more information.
"""

from __future__ import annotations

import os
import uuid

import pytest
from cluplus.proxy import Proxy

import clu.testing
from clu import AMQPClient
from clu.actor import AMQPActor
from sdsstools import merge_config, read_yaml_file
from sdsstools.logger import get_logger

from lvmecp import config
from lvmecp.actor import LvmecpActor as ECPActor
from lvmecp.controller.controller import PlcController


@pytest.fixture()
async def test_config():

    extra = read_yaml_file(os.path.join(os.path.dirname(__file__), "test_lvmecp.yml"))
    yield merge_config(extra, config)


@pytest.fixture()
async def actor(test_config: dict, controllers: PlcController, mocker):

    mocker.patch.object(AMQPActor, "start")

    # test_config["plcs"]["dome"]["host"] = controller.host
    # test_config["plcs"]["dome"]["port"] = controller.port

    _actor = ECPActor.from_config(test_config)
    await _actor.start()

    _actor = await clu.testing.setup_test_actor(_actor)  # type: ignore

    yield _actor

    _actor.mock_replies.clear()
    await _actor.stop()


@pytest.fixture()
async def controllers():
    default_config_file = os.path.join(os.path.dirname(__file__), "test_lvmecp.yml")
    default_config = AMQPActor._parse_config(default_config_file)

    assert "plcs" in default_config

    plcs = []
    for (name, conf) in default_config["plcs"].items():
        print(f"plcs {name}: {conf}")
        try:
            plcs.append(PlcController(name, conf, get_logger("test")))

        except Exception as ex:
            print(f"Error in {type(ex)}: {ex}")

    return plcs


@pytest.fixture()
def amqp_client(actor: ECPActor):

    client = AMQPClient(name=f"{actor.name}_client-{uuid.uuid4().hex[:8]}")
    client.start()

    yield client

    client.stop()


@pytest.fixture()
def test_proxy(amqp_client, actor: ECPActor):

    proxy = Proxy(amqp_client, actor.name)
    proxy.start()

    yield proxy


@pytest.fixture()
async def async_amqp_client(actor: ECPActor):

    client = AMQPClient(name=f"{actor.name}_client-{uuid.uuid4().hex[:8]}")
    await client.start()

    yield client

    await client.stop()


@pytest.fixture()
async def async_proxy(async_amqp_client, actor: ECPActor):

    proxy = Proxy(async_amqp_client, actor.name)
    await proxy.start()

    yield proxy
