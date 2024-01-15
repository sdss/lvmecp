# Changelog

## Next version

### 🚀 New

* Added a cache to the registers with default timeout 1 second.

### ✨ Improved

* Moved the logic to lock a connection while in use to `Modbus.connect()` and `disconnect()` from the context manager.

### 🔧 Fixed

* Use key `modbus` from configuration file to initialise a new `Modbus` instance when a configuration file path is passed.


## 0.6.0 - January 13, 2024

### 🚀 Added

* [#26](https://github.com/sdss/lvmecp/issues/26) Add heartbeat.

### ⚙️ Engineering

* Pinned `pymodbus` to 3.6.2 due to test errors in 3.11.


## 0.5.1 - November 24, 2023

### 🔧 Fixed

* Fixed cases in which the modbus lock could remain locked.


## 0.5.0 - November 5, 2023

### 🚀 New

* Added support for lights.
* Added support for O2 sensors.
* Added support for HVAC controller.

### 🔧 Fixed

* Additional improvments for dealing with PLC disconnections.


## 0.4.1 - August 25, 2023

### 🔧 Fixed

* Attempt at fixing sporadic failures to read Modbus variable by introducing a retry loop.

### ⚙️ Engineering

* Lint using `ruff`.


## 0.4.0 - July 9, 2023

### 🚀 New

* Complete rewrite with dome and door functionality.


## 0.3.1 - May 23, 2022

* Additional updates to documentation and testing.


## 0.3.0 - Mar 24, 2022

* Add `LvmecpProxy` code as API using cluplus.
* Update test code for LvmecpProxy.
* DOCS: Update sequence diagrams.


## 0.2.0 - Jan 20, 2022

* Update the commands `dome`, `light` and `estop` which control elements of the LVM enclosure such as dome, control room light, and so on.
* Update the commands `monitor` which will return the values of HVAC sensors.
* Add the command `telemetry` which show users the status of all elements in the enclosure,
* Unit test for the commands and actor.
* Update example section of sphinx docs.


## 0.1.0 - Nov 9, 2021

* Initial version of the library and actor. Supports communication with the enclosure in LVM project, lvmecp command to on and off the enclosure light and control the Dome.
