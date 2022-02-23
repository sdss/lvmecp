# this is the example code of how to use the lvmscp as an API
import time

from lvmecp.module import API as enclosure_interface


enclosure_interface.ping()

"""
This is the example code for telemetry
"""

enclosure_interface.telemetry()
enclosure_interface.monitor()
# enclosure_interface.domenable()
enclosure_interface.domestatus()
enclosure_interface.lightenable(room="cr")
enclosure_interface.lightstatus()
# enclosure_interface.estop()
