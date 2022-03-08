.. _Examples:

Examples
=====================

Starting the Actor
----------------------

lvmecp actor provides the control system to manage the enclosure of LVM.
First you have to start the actor by the terminal command line in the python virtual environment that you installed the lvmnps package. ::

  $ lvmecp start


If you want to start with debugging mode, you can start like this.
In this case, you can finish the software by ctrl + c on the terminal ::

  $ lvmecp start --debug


Also you can check the status of the actor is running by this command ::

  $ lvmecp status


After your work is done, you can finish the actor by this command ::

  $ lvmecp stop


Finally, you can restart(stop -> start) the actor when the actor is running by this command ::

  $ lvmecp restart


Interface with the Actor
----------------------------------

If you started the actor by the *lvmecp start* command, you can interface with the actor by the clu CLI(Command Line Interface) ::

  $ clu


If you want to ignore the status message from other actors, you can use this command ::

  $ clu -b


Then you will enter to the clu CLI. 
You can check if the actor is running by the ping-pong commands. ::

    lvmecp ping
    04:08:06.973 lvmecp > 
    04:08:06.977 lvmecp : {
        "text": "Pong."
    }
 


Help command
----------------------
          
First you can confirm the existing commands of *lvmecp* by the *help* command ::

    lvmecp help
    13:05:25.386 lvmecp >
    13:05:25.387 lvmecp : {
        "help": [
            "Usage: lvmecp [OPTIONS] COMMAND [ARGS]...",
            "",
            "Options:",
            "  --help  Show this message and exit.",
            "",
            "Commands:",
            "  dome        tasks for Dome",
            "  estop       activate the emergency status.",
            "  get_schema  Returns the schema of the actor as a JSON schema.",
            "  help        Shows the help.",
            "  keyword     Prints human-readable information about a keyword.",
            "  light       tasks for lights",
            "  monitor     return the status of HVAC system and air purge system.",
            "  ping        Pings the actor.",
            "  telemetry   return the status of the enclosure",
            "  version     Reports the version."
        ]
    }


dome command
-------------------

If you run the dome command via lvmecp, you can control the roll-off dome in the enclosure. ::

    lvmecp dome status

will return this kind of reply.::

    lvmecp dome status
    13:05:56.294 lvmecp >
    13:05:56.295 lvmecp i {
        "text": "checking the Dome"
    }
    13:05:56.302 lvmecp i {
        "status": {
            "Dome": "CLOSE"
        }
    }
    13:05:56.302 lvmecp :


If you run the move command via lvmecp, you can on or off the roll-off dome in the enclosure. ::

    lvmecp dome move

will return this kind of reply.::

    lvmecp dome move
    13:06:21.701 lvmecp >
    13:06:21.703 lvmecp i {
        "text": "moving the Dome"
    }
    13:06:21.708 lvmecp i {
        "status": {
            "Dome": "OPEN"
        }
    }
    13:06:21.709 lvmecp :



light command
-----------------

If you run the light command via lvmecp, you can control the light in the enclosure. ::

    lvmecp light status

will return this kind of reply.::

    lvmecp light status
    04:14:05.039 lvmecp > 
    04:14:05.040 lvmecp i {
        "text": "checking the light"
    }
    04:14:05.058 lvmecp i {
        "status": {
            "Control room": 0,
            "Utilities room": 0,
            "Spectrograph room": 0,
            "UMA lights": 0,
            "Telescope room - bright": 0,
            "Telescope room - red": 0
        }
    }

As you can see the reply, we have 6 lights in the enclosure.
Therefore, if you want to turn on the lights in a specific room,
you should use a appropriate argument.

    Parameters
    
    cr
        Control room.
    ur
        Utilities room.
    sr
        Spectrograph room.
    uma
        UMA lights.
    tb
        Telescope room - bright light.
    tr
        Telescope room - red light.

For example, if you want to turn on the light of Control room,::

    lvmecp light move cr
    04:19:37.540 lvmecp > 
    04:19:37.542 lvmecp i {
        "text": "move the Control room"
    }
    04:19:37.546 lvmecp i {
        "status": {
            "Control room": 1
        }
    }

if you want to turn off the light, same.::

    lvmecp light move cr
    04:19:44.837 lvmecp > 
    04:19:44.839 lvmecp i {
        "text": "move the Control room"
    }
    04:19:44.841 lvmecp i {
        "status": {
            "Control room": 0
        }
    }


monitor command
---------------

If you run the monitor command via lvmecp, you can get the status of HVAC sensors in the enclosure.::

    lvmecp monitor

will return this kind of reply.::

    lvmecp monitor
    13:07:36.796 lvmecp >
    13:07:36.797 lvmecp i {
        "text": "monitoring HVAC system."
    }
    13:07:36.798 lvmecp i {
        "status": {
            "hvac": {
                "sensor1": {
                    "value": 187,
                    "unit": "TBD"
                },
                "sensor2": {
                    "value": 3926,
                    "unit": "TBD"
                }
            }
        }
    }
    13:07:36.799 lvmecp :

estop command
---------------

If you run the estop command via lvmecp, you can you can trigger the emergency status in the enclosure.

    lvmecp estop

will return this kind of reply.::

    lvmecp estop
    13:09:43.624 lvmecp >
    13:09:43.625 lvmecp i {
        "text": "start emergency stop of the enclosure ... "
    }
    13:09:43.625 lvmecp i {
        "status": {
            "emergency": {
                "E_status": 1
            }
        }
    }
    13:09:43.626 lvmecp :