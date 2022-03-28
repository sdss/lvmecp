# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-11-19
# @Filename: test_02_proxy_async.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


import asyncio
import logging
import uuid
from time import sleep

import pytest
from clu import AMQPClient, CommandStatus

from lvmecp.actor import LvmecpActor as ECPActor
from lvmecp.proxy_async import LvmecpProxy


pytestmark = [pytest.mark.asyncio]


async def test_proxy_async_single_basic(async_proxy: LvmecpProxy):

    result = await async_proxy.ping()
    print(result)
    assert result
    assert result == {"text": "Pong."}


async def test_proxy_async_telemetry(async_proxy: LvmecpProxy):

    result = await async_proxy.telemetry()
    print(result)
    assert result


async def test_proxy_async_monitor(async_proxy: LvmecpProxy):

    result = await async_proxy.monitor()
    print(result)
    assert result["hvac"]


async def test_proxy_async_light(async_proxy: LvmecpProxy):

    result = await async_proxy.light("status")
    assert result

    result = await async_proxy.light("enable", "cr")
    assert result
    assert result["light"] == {"control room": 1}

    result = await async_proxy.light("enable", "cr")
    assert result
    assert result["light"] == {"control room": 0}


async def test_proxy_async_dome(async_proxy: LvmecpProxy):

    sleep(10)

    result = await async_proxy.dome("status")
    assert result
    assert result == {"dome": "CLOSE"}

    result = await async_proxy.dome("enable")
    assert result
    assert result == {"dome": "OPEN"}

    sleep(10)

    result = await async_proxy.dome("enable")
    assert result
    assert result == {"dome": "CLOSE"}


# async def test_proxy_async_estop(async_proxy: LvmecpProxy):

#    result = await async_proxy.estop()
#    print(result)
#    assert result
