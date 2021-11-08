# lvmecp

![Versions](https://img.shields.io/badge/python->3.7-blue)
[![Documentation Status](https://readthedocs.org/projects/sdss-lvmecp/badge/?version=latest)](https://sdss-lvmecp.readthedocs.io/en/latest/?badge=latest)
[![Travis (.org)](https://img.shields.io/travis/sdss/lvmecp)](https://travis-ci.org/sdss/lvmecp)
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
```

## Quick Start

### Start the actor

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
## Test
     poetry run pytest
     poetry run pytest -p no:logging -s -vv 
     