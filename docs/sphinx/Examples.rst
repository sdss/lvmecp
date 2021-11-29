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
    04:08:31.636 lvmecp > 
    04:08:31.640 lvmecp : {
        "help": [
            "Usage: lvmecp [OPTIONS] COMMAND [ARGS]...",
            "",
            "Options:",
            "  --help  Show this message and exit.",
            "",
            "Commands:",
            "  dome        tasks for Dome",
            "  get_schema  Returns the schema of the actor as a JSON schema.",
            "  help        Shows the help.",
            "  keyword     Prints human-readable information about a keyword.",
            "  light       tasks for lights",
            "  monitor",
            "  ping        Pings the actor.",
            "  version     Reports the version."
        ]
    }


dome command
-------------------

If you run the dome command via lvmecp, you can control the roll-off dome in the enclosure. ::

    lvmecp dome status

will return this kind of reply.::

    lvmecp dome status
    04:11:16.285 lvmecp > 
    04:11:16.289 lvmecp i {
        "text": "checking the Dome"
    }
    04:11:16.291 lvmecp i {
        "status": {
            "Dome": {
                "enable": 0,
                "drive": 0
            }
        }
    }


If you run the move command via lvmecp, you can on or off the roll-off dome in the enclosure. ::

    lvmecp dome move

will return this kind of reply.::




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
    -----------
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

If you run the monitor command via lvmecp, you can get the status of elements in the enclosure.::

    lvmecp monitor

will return this kind of reply.::

    lvmecp monitor
    06:21:42.663 lvmecp > 
    06:21:42.671 lvmecp i {
        "text": "monitoring ... "
    }
    06:21:42.674 lvmecp i {
        "status": {
            "emergengy": {
                "E_stop": 0,
                "E_status": 0,
                "E_relay": 0
            },
            "hvac": {
                "key1": 2366,
                "key2": 724
            }
        }
    }

