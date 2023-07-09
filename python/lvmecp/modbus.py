#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2023-05-23
# @Filename: modbus.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
import pathlib

from pymodbus.client.tcp import AsyncModbusTcpClient

from sdsstools import read_yaml_file

from lvmecp import config as lvmecp_config
from lvmecp import log


class ModbusRegister:
    """A Modbus register/variable.

    Parameters
    ----------
    modbus
        The `.Modbus` connection.
    name
        The name assigned to this register.
    address
        The PDU ``address`` (note this is 0-indexed, and one less than the
        register in the memory block) for the element.
    mode
        The type of data block: `coil``, ``holding_register``, ``discrete_input``,
        or ``input_register``.
    group
        A grouping key for registers.

    """

    def __init__(
        self,
        modbus: Modbus,
        name: str,
        address: int,
        mode: str = "coil",
        group: str | None = None,
    ):
        self.modbus = modbus
        self.client = modbus.client

        self.name = name
        self.address = address
        self.mode = mode
        self.group = group

    async def _get_internal(self):
        """Return the value of the modbus register."""

        if self.mode == "coil":
            func = self.client.read_coils
        elif self.mode == "holding_register":
            func = self.client.read_holding_registers
        elif self.mode == "discrete_input":
            func = self.client.read_discrete_inputs
        elif self.mode == "input_register":
            func = self.client.read_input_registers
        else:
            raise ValueError(f"Invalid block mode {self.mode!r}.")

        if self.client.connected:
            resp = await func(self.address, count=1)  # type: ignore
        else:
            async with self.modbus:
                resp = await func(self.address, count=1)  # type: ignore

        if resp.function_code > 0x80:
            raise ValueError(
                f"Invalid response for element "
                f"{self.name!r}: 0x{resp.function_code:02X}."
            )

        if self.mode == "coil" or self.mode == "discrete_input":
            value = resp.bits[0]
        else:
            value = resp.registers[0]

        return value

    async def get(self, open_connection: bool = True):
        """Return the value of the modbus register. Implements retry."""

        # If we need to open the connection, use the Modbus context
        # and call ourselves recursively with open_connection=False
        # (at that point it will be open).
        if open_connection:
            await self.modbus.connect()

        try:
            return await self._get_internal()
        finally:
            if open_connection:
                await self.modbus.disconnect()

    async def set(self, value: int | bool):
        """Sets the value of the register."""

        # Always open the connection.
        async with self.modbus:
            if self.mode == "coil":
                func = self.client.write_coil
            elif self.mode == "holding_register":
                func = self.client.write_register
            elif self.mode == "discrete_input" or self.mode == "input_register":
                raise ValueError(f"Block of mode {self.mode!r} is read-only.")
            else:
                raise ValueError(f"Invalid block mode {self.mode!r}.")

            if self.client.connected:
                resp = await func(self.address, value)  # type: ignore
            else:
                async with self.modbus:
                    resp = await func(self.address, value)  # type: ignore

            if resp.function_code > 0x80:
                raise ValueError(
                    f"Invalid response for element "
                    f"{self.name!r}: 0x{resp.function_code:02X}."
                )


class Modbus(dict[str, ModbusRegister]):
    """A simple dictionary of Modbus registers.

    Parameters
    ----------
    config
        A YAML configuration file or dictionary with the keys ``host`` and ``port``
        for the Modbus server, and a dictionary ``registers`` with modbus registers.
        Each one must include a PDU ``address`` (note this is 0-indexed, and one
        less than the register in the memory block) and optionally ``mode`` for
        the block type (``coil``, ``holding_register``, ``discrete_input``,
        or ``input_register``; defaults to ``coil``). If `None`, defaults to the
        internal configuration.

    """

    def __init__(self, config: dict | pathlib.Path | str | None = None):
        if isinstance(config, (str, pathlib.Path)):
            self.config = read_yaml_file(str(config))
        elif config is None:
            self.config = lvmecp_config["modbus"]
        elif isinstance(config, dict):
            self.config = config

        assert isinstance(config, dict)

        self.host = self.config["host"]
        self.port = self.config["port"]

        self.client = AsyncModbusTcpClient(self.host, port=self.port)
        self.lock = asyncio.Lock()

        register_data = self.config["registers"]
        registers = {
            name: ModbusRegister(
                self,
                name,
                elem["address"],
                mode=elem.get("mode", "coil"),
                group=elem.get("group", None),
            )
            for name, elem in register_data.items()
        }

        dict.__init__(self, registers)
        for name, elem in registers.items():
            setattr(self, name, elem)

    async def connect(self):
        """Connects to the client."""

        if self.lock:
            await self.lock.acquire()

        hp = f"{self.host}:{self.port}"
        log.debug(f"Trying to connect to modbus server on {hp}")

        try:
            # After a self.client.close() pymodbus sets the host to None.
            self.client.params.host = self.host
            await asyncio.wait_for(self.client.connect(), timeout=1)
        except asyncio.TimeoutError:
            raise ConnectionError(f"Timed out connecting to server at {hp}.")
        except Exception as err:
            raise ConnectionError(f"Failed connecting to server at {hp}: {err}.")
        finally:
            if self.lock and self.lock.locked() and not self.client.connected:
                self.lock.release()

        log.debug(f"Connected to {hp}.")

    async def disconnect(self):
        """Disconnects the client."""

        if self.client:
            self.client.close()

        log.debug(f"Disonnected from {self.host}:{self.port}.")

        if self.lock and self.lock.locked():
            self.lock.release()

    async def __aenter__(self):
        """Initialises the connection to the server."""

        await self.connect()

    async def __aexit__(self, exc_type, exc, tb):
        """Closes the connection to the server."""

        await self.disconnect()

    async def get_all(self):
        """Returns a dictionary with all the registers."""

        async with self:
            names = [name for name in self]
            tasks = [elem.get(open_connection=False) for elem in self.values()]

            results = await asyncio.gather(*tasks)

        return dict(zip(names, results))

    async def read_group(self, group: str):
        """Returns a dictionary of all read registers that match a ``group``."""

        names = []
        tasks = []
        async with self:
            for name in self:
                register = self[name]
                if register.group is not None and register.group == group:
                    names.append(name)
                    tasks.append(register.get(open_connection=False))

            results = await asyncio.gather(*tasks)

        return dict(zip(names, results))
