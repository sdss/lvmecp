# Changelog

## Next version

### ✨ Improved

* Add reporting of roll-off error state and allow resetting on error.

### 🔧 Fixed

* Restore GS3 status registers and fix addresses for roll-off lockout and error.


## 0.8.4 - November 3, 2024

### ✨ Improved

* Add a lock for the status command to prevent multiple concurrent requests.

### ⚙️ Engineering

* Use `uv` for packaging.


## 0.8.3 - September 7, 2024

### 🔧 Fixed

* Fixed a bug that would make a module notification fail in some cases if its maskbit value was zero.


## 0.8.2 - August 19, 2024

### ✨ Improved

* Fail open/close dome if the drive becomes disabled (usually due to the dome being stopped).


## 0.8.1 - July 23, 2024

### 🚀 New

* Added rain sensor.

### ⚙️ Engineering

* Format code using `ruff`.


## 0.8.0 - June 1, 2024

### 🚀 New

* Allow not outputting the registers in `status` with `--no-registers`.
* Use `LVMActor` as the base class for the ECP actor.

### ✨ Improved

* Use `dome_open` and `dome_closed` modbus variables to determine the state of the roll-off.


## 0.7.0 - January 19, 2024

### 🚀 New

* Added a cache to the registers with default timeout 0.5 second.
* `Modbus.read_group()` calls `Modbus.get_all()` instead of reading individual registers sequentially. Since during a `status` all groups are read in quick succession, and with caching, this results in much faster status outputs.

### ✨ Improved

* Moved the logic to lock a connection while in use to `Modbus.connect()` and `disconnect()` from the context manager.

### 🔧 Fixed

* Use key `modbus` from configuration file to initialise a new `Modbus` instance when a configuration file path is passed.
* Fixed output of status flags with value zero.


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
