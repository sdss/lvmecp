# lvmecp

![Versions](https://img.shields.io/badge/python->3.10-blue)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Test](https://github.com/sdss/lvmecp/actions/workflows/test.yml/badge.svg)](https://github.com/sdss/lvmecp/actions/workflows/test.yml)
[![Documentation Status](https://readthedocs.org/projects/lvmecp/badge/?version=latest)](https://lvmecp.readthedocs.io/en/latest/?badge=latest)
[![Docker](https://github.com/sdss/lvmecp/actions/workflows/docker.yml/badge.svg)](https://github.com/sdss/lvmecp/actions/workflows/docker.yml)
[![codecov](https://codecov.io/gh/sdss/lvmecp/branch/develop/graphs/badge.svg)](https://codecov.io/gh/sdss/lvmecp)

SDSS-V LVM Enclosure Control Package

## Features

- CLU Actor based interface
- Supports [DirectLogic 205 (Micro Modular PLC)](https://www.automationdirect.com/adc/overview/catalog/programmable_controllers/directlogic_series_plcs_(micro_to_small,_brick_-a-_modular)/directlogic_205_(micro_modular_plc))

## Prerequisite

Install [Poetry](https://python-poetry.org/) by using PyPI.

```
$ pip install poetry
$ python create_setup.py
$ pip install -e .
```

Install [RabbitMQ](https://www.rabbitmq.com/) by using apt-get.

```
$ sudo apt-get install -y erlang
$ sudo apt-get install -y rabbitmq-server
$ sudo systemctl enable rabbitmq-server
$ sudo systemctl start rabbitmq-server
```

Install [CLU](https://clu.readthedocs.io/en/latest/) by using PyPI.
```
$ pip install sdss-clu
```

## Installation


Clone this repository.
```
$ git clone https://github.com/sdss/lvmecp
$ cd lvmecp
$ poetry install
```

## Quick Start

### Start the actor

Before you start the actor, you must have the PLC or simulator.

Start `lvmecp` actor.
```
$ lvmecp start
```

In another terminal, type `clu` and `lvmecp ping` for test.
```
$ clu
lvmecp ping
     07:41:22.636 lvmecp >
     07:41:22.645 lvmecp : {
         "text": "Pong."
         }
```

Stop `lvmecp` actor.
```
$ lvmecp stop
```

## Example

In terminal which you are turning clu on, you can use the command for lvmecp.

```
$ clu
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
```
