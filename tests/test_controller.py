# encoding: utf-8
#
# test_controller.py

import os

import pytest
from clu import AMQPActor
from clu.testing import setup_test_actor

from sdsstools.logger import get_logger

from lvmecp.actor.commands import parser as ecp_command_parser
from lvmecp.controller.controller import PlcController


async def send_command(actor, command_string):
    command = actor.invoke_mock_command(command_string)
    await command
    # assert command.status.is_done

    plc_num = len(actor.parser_args[0])
    status_all_reply = []
    #assert actor.mock_replies[-1]["text"] == "done"
    status_reply = actor.mock_replies
    print(status_reply)
    
    return status_reply


@pytest.mark.asyncio
async def test_actor(controllers):

    test_actor = await setup_test_actor(
        AMQPActor("lvmecp", host="localhost", port=9999)
    )

    test_actor.parser = ecp_command_parser
    test_actor.parser_args = [controllers]

    # command dome/ light/ monitor
    status = await send_command(test_actor, "dome status")
    print(status)

