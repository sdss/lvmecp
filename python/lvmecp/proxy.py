import sys
import time
import uuid

from clu.actor import AMQPClient
from cluplus.proxy import Proxy


# actor = "lvmecp"

# amqpc = AMQPClient(name=f"proxy-{uuid.uuid4().hex[:8]}")
# lvmecp = Proxy(amqpc, actor)
# lvmecp.start()


class LvmecpProxy:
    def ping(self):

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
            self.amqpc.log.error(f"Exception: {e}")

        return result

    def telemetry(self):

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
            self.amqpc.log.error(f"Exception: {e}")

        return result

    def monitor(self):

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
            self.amqpc.log.error(f"Exception: {e}")

        return result

    def dome(self, command: str):
        """
        parameters
        ------------
        command
            enable
            status
        """

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmecp = Proxy(amqpc, "lvmecp")
            lvmecp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = lvmecp.dome(command)

        except Exception as e:
            self.amqpc.log.error(f"Exception: {e}")

        return result

    def light(self, command: str, room=None):
        """
        parameters
        ------------
        command
            enable
            status
        """

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmecp = Proxy(amqpc, "lvmecp")
            lvmecp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = lvmecp.light(command, room)

        except Exception as e:
            self.amqpc.log.error(f"Exception: {e}")

        return result

    def estop(self):

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
            self.amqpc.log.error(f"Exception: {e}")

        return result
