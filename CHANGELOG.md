# Changelog

## 0.1.0 -Nov 9, 2021

Initial version of the library and actor. Supports communication with the enclosure in LVM project, lvmecp command to on and off the enclosure light and control the Dome.

## 0.2.0 -Jan 20, 2022

- update the commands "dome", "light" and "estop" which control elements of the LVM enclosure such as dome, control room light, and so on. 
- update the commands "monitor" which will return the values of HVAC sensors.
- add the command "telemetry" which show users the status of all elements in the enclosure,
- unit test for the commands and actor.
- update example section of sphinx docs.

## 0.3.0 - Mar 24, 2022

- Add LvmecpProxy code as API using cluplu
- Update test code for LvmecpProxy
- <DOCS>:Update sequence diagrams