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
from lvmecp.proxy import LvmecpProxy


def test_proxy_single_basic(test_proxy: LvmecpProxy):

    result = test_proxy.ping()
    print(result)
    assert result
    assert result == {"text": "Pong."}


def test_proxy_telemetry(test_proxy: LvmecpProxy):

    result = test_proxy.telemetry()
    print(result)
    assert result


def test_proxy_monitor(test_proxy: LvmecpProxy):

    result = test_proxy.monitor()
    print(result)
    assert result["hvac"]


#def test_proxy_light(test_proxy: LvmecpProxy):

#    result = test_proxy.lightstatus(room="cr")
#    assert result
#    assert result == {"Control room": 0}

#    result = test_proxy.lightenable(room="cr")
#    assert result
#    assert result == {"Control room": 1}


#def test_proxy_dome(test_proxy: LvmecpProxy):

#    result = test_proxy.domestatus()
#    print(result)
#    assert result
#    assert result == {'Dome': 'CLOSE'}

#    result = test_proxy.domenable()
#    print(result)
#    assert result
#    assert result == {'Dome': 'OPEN'}


# def test_proxy_estop(proxy: LvmecpProxy):

#    result = proxy.estop()
#    print(result)
#    assert result
