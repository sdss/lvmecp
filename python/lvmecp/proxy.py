import sys
import time
import uuid

from clu.actor import AMQPClient
from cluplus.proxy import Proxy


actor = "lvmecp"

amqpc = AMQPClient(name=f"proxy-{uuid.uuid4().hex[:8]}")
lvmecp = Proxy(amqpc, actor)
lvmecp.start()


class LvmecpProxy:
    def ping():

        # sequential
        try:
            result = lvmecp.ping()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        return result

    def telemetry():

        # sequential
        try:
            result = lvmecp.telemetry()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        return result

    def monitor():

        # sequential
        try:
            result = lvmecp.monitor()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        return result

    def dome(command: str):
        """
        parameters
        ------------
        command
            enable
            status
        """

        # sequential
        try:
            result = lvmecp.dome(command)

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        return result

    def light(command: str, room=None):
        """
        parameters
        ------------
        command
            enable
            status
        """

        # sequential
        try:
            result = lvmecp.light(command, room)

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        return result

    def estop():

        # sequential
        try:
            result = lvmecp.estop()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        return result
