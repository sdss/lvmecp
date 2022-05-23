import sys
import uuid

from cluplus.proxy import Proxy

from clu.actor import AMQPClient


# actor = "lvmecp"

# amqpc = AMQPClient(name=f"proxy-{uuid.uuid4().hex[:8]}")
# lvmecp = Proxy(amqpc, actor)
# lvmecp.start()


class LvmecpProxy:
    async def ping(self):

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmecp = Proxy(amqpc, "lvmecp")
            lvmecp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = await lvmecp.ping()

        except Exception as e:
            self.amqpc.log.error(f"Exception: {e}")

        return result

    async def telemetry(self):

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmecp = Proxy(amqpc, "lvmecp")
            lvmecp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = await lvmecp.telemetry()

        except Exception as e:
            self.amqpc.log.error(f"Exception: {e}")

        return result

    async def monitor(self):

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmecp = Proxy(amqpc, "lvmecp")
            lvmecp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = await lvmecp.monitor()

        except Exception as e:
            self.amqpc.log.error(f"Exception: {e}")

        return result

    async def dome(self, command: str):
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
            result = await lvmecp.dome(command)

        except Exception as e:
            self.amqpc.log.error(f"Exception: {e}")

        return result

    async def light(self, command: str, room=None):
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
            result = await lvmecp.light(command, room)

        except Exception as e:
            self.amqpc.log.error(f"Exception: {e}")

        return result

    async def estop(self):

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmecp = Proxy(amqpc, "lvmecp")
            lvmecp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = await lvmecp.estop()

        except Exception as e:
            self.amqpc.log.error(f"Exception: {e}")

        return result
