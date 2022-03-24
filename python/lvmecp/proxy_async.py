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

    async def dome(command: str):
        """
        parameters
        ------------
        command
            enable
            status
        """

        # sequential
        try:
            result = await lvmecp.dome(command)

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        return result

    async def light(command: str, room=None):
        """
        parameters
        ------------
        command
            enable
            status
        """

        # sequential
        try:
            result = await lvmecp.light(command, room)

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
