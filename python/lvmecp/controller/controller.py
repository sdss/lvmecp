#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong Yang (mingyeong@khu.ac.kr)
# @Date: 2021-10-03
# @Filename: controller.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
import configparser
import os
import pathlib
import re
import warnings
from collections.abc import AsyncIterator

from typing import Any, Callable, Iterable, Optional

import numpy
import yaml
from clu.device import Device

from sdsstools import read_yaml_file


__all__ = ["PlcController"]

class PlcController():
    """Talks to an Plc controller over TCP/IP.

    Parameters
    ----------
    name
        A name identifying this controller.
    host
        The hostname of the Plc.
    port
        The port on which the Plc listens to incoming connections.
    """

    def __init__(self, name: str, host: str, port: int):
        self.name = name
        self.host = host
        self.port = port


    def send_command(
        self,
        command,
    ):
        """Sends a command to the Plc.

        Parameters
        ----------
        command_string
            The command to send to the Plc. Will be converted to uppercase.
        command_id
            The command id to associate with this message. If not provided, a
            sequential, autogenerated one will be used.
        """