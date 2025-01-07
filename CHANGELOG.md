# Changelog

## Next version

### 🚀 New

* [#33](https://github.com/sdss/lvmecp/pull/33) Add a mode to close the dome using only drive overcurrent to determine when the movement has completed.

## 1.1.0 - January 1, 2025

### ✨ Improved

* [#32](https://github.com/sdss/lvmecp/pull/32) Major refactor of the `Modbus` and `ModbusRegister` classes. The main change is that the performance has been greatly improved, with `Modbus.get_all()` going from taking ~0.6 seconds to under 0.1. The register and coil blocks are now read completely, in chunks as large as the device will accept, as opposed to before, when we would read each variable with one read command (although the connection was not closed in between). Note that several methods and variables have been renamed; see the PR for details.


## 1.0.2 - December 27, 2024

### ✨ Improved

* Report last time the heartbeat was set in the PLC in the `status` command.
* Report timeout of the engineering mode.
* Report ``last_heartbeat_set` as an ISO string.


## 1.0.1 - December 26, 2024

### ⚙️ Engineering

* Bump `CLU` to 2.4.3.

### 🔧 Fixed

* Do not command the dome to close during daytime if it is already closed.


## 1.0.0 - December 25, 2024

### 🚀 New

* [#29](https://github.com/sdss/lvmecp/pull/29) Add a new engineering mode that can be used to bypass the heartbeat and to allow the dome to open during daytime. Part of RORR RID-025.
* [#30](https://github.com/sdss/lvmecp/pull/30) Prevent the dome from opening during daytime. Close if daytime is detected. Part of RORR RID-025.
* [#31](https://github.com/sdss/lvmecp/pull/31) Prevent the dome from opening multiple times in a short period of time. RORR RID-019.

### ✨ Improved

* Add reporting of roll-off error state and allow resetting on error.
* Prevent the PLC modules from running before the actor is ready.

### 🏷️ Changed

* [#28](https://github.com/sdss/lvmecp/pull/28) Removed the automatic setting of the heartbeat variable. Added a `heartbeat` command that will be triggered by a heartbeat middleware.

### 🔧 Fixed

* Restore GS3 status registers and fix addresses for roll-off lockout and error.

### ⚙️ Engineering

* Updated workflows.


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
