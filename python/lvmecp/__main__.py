#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-03
# @Filename: __main__.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import os
import pathlib
from copy import deepcopy

import click
from click_default_group import DefaultGroup

from sdsstools.daemonizer import DaemonGroup, cli_coro

from lvmecp import config
from lvmecp.actor import ECPActor
from lvmecp.simulator import plc_simulator


@click.group(cls=DefaultGroup, default="actor", default_if_no_args=True)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Debug mode. Use additional v for more details.",
)
@click.pass_context
def lvmecp(ctx, verbose):
    """LCM enclosure control software."""

    ctx.obj = {"verbose": verbose}


@lvmecp.group(cls=DaemonGroup, prog="ecp-actor", workdir=os.getcwd())
@click.option(
    "--with-simulator/",
    is_flag=True,
    help="Runs the actor aginst the simulator.",
)
@click.pass_context
@cli_coro()
async def actor(ctx, with_simulator: bool = False):
    """Runs the actor."""

    ecp_config = deepcopy(config)
    if with_simulator:
        ecp_config["plc"]["host"] = "127.0.0.1"
        ecp_config["plc"]["port"] = 5020

    if not os.path.isabs(ecp_config["actor"]["schema"]):
        schema_rel = ecp_config["actor"]["schema"]
        ecp_config["actor"]["schema"] = str(pathlib.Path(__file__).parent / schema_rel)

    actor_obj = ECPActor.from_config(ecp_config)

    if ctx.obj["verbose"]:
        actor_obj.log.sh.setLevel(0)
        if actor_obj.log.fh:
            actor_obj.log.fh.setLevel(0)

    if with_simulator:
        await plc_simulator.start(serve_forever=False)

        assert plc_simulator.server and plc_simulator.server.server
        await plc_simulator.server.server.start_serving()

    await actor_obj.start()
    await actor_obj.run_forever()


@lvmecp.command()
@cli_coro()
async def simulator():
    """Runs the PLC simulator."""

    await plc_simulator.start()


if __name__ == "__main__":
    lvmecp()
