import sys
import uuid
import time

from clu.actor import AMQPClient
from cluplus.proxy import Proxy


class API:
    def ping():

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmecp = Proxy(amqpc, "lvmecp")
            lvmecp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = lvmecp.ping()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result

    def telemetry():

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmecp = Proxy(amqpc, "lvmecp")
            lvmecp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = lvmecp.telemetry()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result

    def monitor():

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmecp = Proxy(amqpc, "lvmecp")
            lvmecp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = lvmecp.monitor()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result

    def domenable():

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmecp = Proxy(amqpc, "lvmecp")
            lvmecp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = lvmecp.dome("enable")

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result

    def domestatus():

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmecp = Proxy(amqpc, "lvmecp")
            lvmecp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = lvmecp.dome("status")

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result

    def lightenable(room):

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmecp = Proxy(amqpc, "lvmecp")
            lvmecp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = lvmecp.light("enable", room)

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result

    def lightstatus(room=None):

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmecp = Proxy(amqpc, "lvmecp")
            lvmecp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

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

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmecp = Proxy(amqpc, "lvmecp")
            lvmecp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = lvmecp.estop()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result