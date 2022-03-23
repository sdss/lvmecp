import sys
import time
import uuid

from clu.actor import AMQPClient
from cluplus.proxy import Proxy


actor = "lvmecp"

amqpc = AMQPClient(name=f"proxy-{uuid.uuid4().hex[:8]}", host="localhost")
lvmecp = Proxy(amqpc, actor)
lvmecp.start()


class LvmecpProxy:
    async def ping():

        # sequential
        try:
            result = await lvmecp.ping()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        return result

    async def telemetry():

        # sequential
        try:
            result = await lvmecp.telemetry()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        return result

    async def monitor():

        # sequential
        try:
            result = await lvmecp.monitor()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        return result

    async def domenable():

        # sequential
        try:
            result = await lvmecp.dome("enable")

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        return result

    async def domestatus():

        # sequential
        try:
            result = await lvmecp.dome("status")

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        return result

    async def lightenable(room):

        # sequential
        try:
            result = await lvmecp.light("enable", room)

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        return result

    async def lightstatus(room=None):

        # sequential
        try:
            if room:
                result = await lvmecp.light("status", room)
            else:
                result = lvmecp.light("status")

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        return result

    async def estop():

        # sequential
        try:
            result = await lvmecp.estop()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        return result
