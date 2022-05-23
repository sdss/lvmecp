#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-09-30
# @Filename: __init__.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

"""
isort:skip_file
"""

import glob
import importlib
import os

import click
from clu.command import Command
from clu.parsers.click import (
    CluGroup,
    get_schema,
    help_,
    keyword,
    ping,
    version,
    command_parser,
)


@click.group(cls=CluGroup)
def parser(*args):
    pass


parser.add_command(ping)
parser.add_command(version)
parser.add_command(help_)
parser.add_command(get_schema)
parser.add_command(keyword)


@command_parser.command(name="__commands")
@click.pass_context
def __commands(ctx, command: Command, *args):
    # Returns all commands.

    # we have to use the help key for the command list,
    # don't want to change the standard model.
    command.finish(help=[k for k in ctx.command.commands.keys() if k[:2] != "__"])


parser.add_command(__commands)

# Autoimport all modules in this directory so that they are added to the parser.

exclusions = ["__init__.py"]

cwd = os.getcwd()
os.chdir(os.path.dirname(os.path.realpath(__file__)))

files = [
    file_ for file_ in glob.glob("**/*.py", recursive=True) if file_ not in exclusions
]

for file_ in files:
    modname = file_[0:-3].replace("/", ".")
    mod = importlib.import_module("lvmecp.actor.commands." + modname)

os.chdir(cwd)
