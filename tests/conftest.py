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

import os

import clu.testing
import pytest
from clu import AMQPActor, AMQPClient
from clu.actor import AMQPBaseActor

from sdsstools import merge_config, read_yaml_file
from sdsstools.logger import get_logger

from lvmecp import config
from lvmecp.actor.actor import LvmecpActor as ECPActor
from lvmecp.controller.controller import PlcController


@pytest.fixture()
def test_config():

    extra = read_yaml_file(os.path.join(os.path.dirname(__file__), "test_lvmecp.yml"))
    yield merge_config(extra, config)


@pytest.fixture
def controllers():
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
async def actor(test_config: dict, mocker):

    # We need to call the actor .start() method to force it to create the
    # controllers and to start the tasks, but we don't want to run .start()
    # on the actor.
    mocker.patch.object(AMQPBaseActor, "start")

    # test_config["controllers"]["sp1"]["host"] = controller.host
    # test_config["controllers"]["sp1"]["port"] = controller.port

    _actor = ECPActor.from_config(test_config)
    await _actor.start()

    _actor = await clu.testing.setup_test_actor(_actor)  # type: ignore

    yield _actor

    #_actor.mock_replies.clear()
    #await _actor.stop()


@pytest.fixture()
async def actor_stop():
    _actor = ECPActor.from_config(test_config)
    
    _actor.mock_replies.clear()
    await _actor.stop()