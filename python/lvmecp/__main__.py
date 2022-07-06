#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-03
# @Filename: __main__.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import os

import click
from click_default_group import DefaultGroup
from clu.tools import cli_coro

from sdsstools.daemonizer import DaemonGroup

from lvmecp.actor.actor import LvmecpActor as ECPActorInstance


@click.group(cls=DefaultGroup, default="actor", default_if_no_args=True)
@click.option(
    "-c",
    "--config",
    "config_file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the user configuration file.",
)
@click.option(
    "-r",
    "--rmq_url",
    "rmq_url",
    default=None,
    type=str,
    help="rabbitmq url, eg: amqp://guest:guest@localhost:5672/",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Debug mode. Use additional v for more details.",
)
@click.pass_context
def lvmecp(ctx, config_file, rmq_url, verbose):
    """ECP controller"""

    ctx.obj = {"verbose": verbose, "config_file": config_file, "rmq_url": rmq_url}


@lvmecp.group(cls=DaemonGroup, prog="ecp_actor", workdir=os.getcwd())
@click.pass_context
@cli_coro
async def actor(ctx):
    """Runs the actor."""
    default_config_file = os.path.join(os.path.dirname(__file__), "etc/lvmecp.yml")
    config_file = ctx.obj["config_file"] or default_config_file

    lvmecp_obj = ECPActorInstance.from_config(config_file, url=ctx.obj["rmq_url"], verbose=ctx.obj["verbose"])

    if ctx.obj["verbose"]:
        lvmecp_obj.log.fh.setLevel(0)
        lvmecp_obj.log.sh.setLevel(0)

    await lvmecp_obj.start()
    await lvmecp_obj.run_forever()


if __name__ == "__main__":
    lvmecp()
