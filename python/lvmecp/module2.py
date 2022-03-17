import sys
import time
import uuid

from clu.actor import AMQPClient
from cluplus.proxy import Proxy


actor = "lvmecp"

amqpc = AMQPClient(name=f"proxy-{uuid.uuid4().hex[:8]}", host="localhost")
lvmecp = Proxy(amqpc, actor)
lvmecp.start()


class API:
    def __init__():
        lvmecp.start()

    def ping():

        # sequential
        try:
            result = lvmecp.ping()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result

    def telemetry():

        # sequential
        try:
            result = lvmecp.telemetry()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result

    def monitor():

        # sequential
        try:
            result = lvmecp.monitor()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result

    def domenable():

        # sequential
        try:
            result = lvmecp.dome("enable")

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result

    def domestatus():

        # sequential
        try:
            result = lvmecp.dome("status")

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result

    def lightenable(room):

        # sequential
        try:
            result = lvmecp.light("enable", room)

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result

    def lightstatus(room=None):

        # sequential
        try:
            if room:
                result = lvmecp.light("status", room)
            else:
                result = lvmecp.light("status")

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result

    def estop():

        # sequential
        try:
            result = lvmecp.estop()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result
