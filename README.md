# lvmecp

![Versions](https://img.shields.io/badge/python->3.7-blue)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/lvmecp/badge/?version=latest)](https://lvmecp.readthedocs.io/en/latest/?badge=latest)
[![Docker](https://github.com/sdss/lvmecp/actions/workflows/Docker.yml/badge.svg)](https://github.com/sdss/lvmecp/actions/workflows/Docker.yml)
[![codecov](https://codecov.io/gh/sdss/lvmecp/branch/main/graph/badge.svg)](https://codecov.io/gh/sdss/lvmecp)

SDSS-V LVM Enclosure Control Package

## Features

- CLU Actor based interface
- Supports [DirectLogic 205 (Micro Modular PLC)](https://www.automationdirect.com/adc/overview/catalog/programmable_controllers/directlogic_series_plcs_(micro_to_small,_brick_-a-_modular)/directlogic_205_(micro_modular_plc))

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
09:57:01.762 lvmecp > 
09:57:01.767 lvmecp : {
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
        "  ping        Pings the actor.",
        "  version     Reports the version."
    ]
}
lvmecp light move
09:57:05.225 lvmecp > 
09:57:05.227 lvmecp i {
    "text": "move the light"
}
09:57:05.230 lvmecp i {
    "text": "ON"
}
09:57:05.231 lvmecp : 
lvmecp light status
09:57:14.577 lvmecp > 
09:57:14.579 lvmecp i {
    "text": "checking the light"
}
09:57:14.581 lvmecp i {
    "text": "ON"
}
09:57:14.583 lvmecp : 
```