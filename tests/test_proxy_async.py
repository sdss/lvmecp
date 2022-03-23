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


@pytest.mark.asyncio
async def test_proxy_async_single_basic(async_proxy: LvmecpProxy):

    result = await async_proxy.ping()
    print(result)
    assert result
    assert result == {"text": "Pong."}


@pytest.mark.asyncio
async def test_proxy_async_telemetry(async_proxy: LvmecpProxy):

    result = await async_proxy.telemetry()
    print(result)
    assert result


@pytest.mark.asyncio
async def test_proxy_async_monitor(async_proxy: LvmecpProxy):

    result = await async_proxy.monitor()
    print(result)
    assert result["hvac"]


# @pytest.mark.asyncio
# async def test_proxy_async_light(async_proxy: LvmecpProxy):

#    result = await async_proxy.lightstatus(room="cr")
#    assert result
#    assert result == {"Control room": 0}

#    result = await async_proxy.lightenable(room="cr")
#    assert result
#    assert result == {"Control room": 1}

# @pytest.mark.asyncio
# async def test_proxy_async_dome(async_proxy: LvmecpProxy):

#    result = await async_proxy.domestatus()
#    print(result)
#    assert result
#    assert result == {'Dome': 'CLOSE'}

#    result = await async_proxy.domenable()
#    print(result)
#    assert result
#    assert result == {'Dome': 'OPEN'}

# @pytest.mark.asyncio
# async def test_proxy_async_estop(async_proxy: LvmecpProxy):

#    result = await async_proxy.estop()
#    print(result)
#    assert result
