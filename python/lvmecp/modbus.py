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
from time import time

from typing import cast

from pymodbus.client.tcp import AsyncModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

from sdsstools import read_yaml_file
from sdsstools.utils import cancel_task

from lvmecp import config as lvmecp_config
from lvmecp import log
from lvmecp.exceptions import ECPError


MAX_RETRIES = 3
TIMEOUT = 10.0


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
        count: int = 1,
        group: str | None = None,
        decoder: str | None = None,
    ):
        self.modbus = modbus
        self.client = modbus.client

        self.name = name
        self.address = address
        self.mode = mode
        self.count = count
        self.group = group
        self.decoder = decoder

        self._last_value: int | float = 0
        self._last_seen: float = 0

    async def _get_internal(self, use_cache: bool = True):
        """Return the value of the modbus register."""

        cache_timeout = self.modbus.cache_timeout
        last_seen_interval = time() - self._last_seen
        if use_cache and last_seen_interval < cache_timeout:
            return self._last_value

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
            resp = await func(
                self.address,
                count=self.count,
                slave=self.modbus.slave,
            )  # type: ignore
        else:
            async with self.modbus:
                resp = await func(
                    self.address,
                    count=self.count,
                    slave=self.modbus.slave,
                )  # type: ignore

        if resp.function_code > 0x80:
            raise ValueError(
                f"Invalid response for element "
                f"{self.name!r}: 0x{resp.function_code:02X}."
            )

        if self.mode == "coil" or self.mode == "discrete_input":
            bits = resp.bits
            value = bits[0 : self.count] if self.count > 1 else bits[0]
        else:
            registers = resp.registers
            value = registers[0 : self.count] if self.count > 1 else registers[0]

            if self.decoder is not None:
                if self.decoder == "float_32bit":
                    bin_payload = BinaryPayloadDecoder.fromRegisters(
                        value,
                        byteorder=Endian.BIG,
                        wordorder=Endian.LITTLE,
                    )
                    value = round(bin_payload.decode_32bit_float(), 3)
                else:
                    raise ValueError(f"Unknown decoder {self.decoder}")

        if not isinstance(value, (int, float)):
            raise ValueError(f"Invalid type for {self.name!r} response.")

        self._last_value = value
        self._last_seen = time()

        return value

    async def get(self, open_connection: bool = True, use_cache: bool = True):
        """Return the value of the modbus register. Implements retry."""

        for ntries in range(1, MAX_RETRIES + 1):
            # If we need to open the connection, use the Modbus context
            # and call ourselves recursively with open_connection=False
            # (at that point it will be open).
            if open_connection:
                await self.modbus.connect()

            if not self.modbus.client or not self.modbus.client.connected:
                raise ConnectionError("Not connected to modbus server.")

            try:
                return await self._get_internal(use_cache=use_cache)
            except Exception:
                if ntries >= MAX_RETRIES:
                    raise

                await asyncio.sleep(0.5)
            finally:
                if open_connection:
                    await self.modbus.disconnect()

    async def set(self, value: int | bool):
        """Sets the value of the register."""

        for ntries in range(1, MAX_RETRIES + 1):
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

                try:
                    if self.client.connected:
                        resp = await func(self.address, value)  # type: ignore
                    else:
                        async with self.modbus:
                            resp = await func(self.address, value)  # type: ignore

                    if resp.function_code > 0x80:
                        raise ECPError(
                            f"Invalid response for element "
                            f"{self.name!r}: 0x{resp.function_code:02X}."
                        )
                    else:
                        self._last_value = int(value)
                        self._last_seen = time()

                        return

                except Exception as err:
                    if ntries >= MAX_RETRIES:
                        raise ECPError(f"Failed setting {self.name!r}: {err}")

                await asyncio.sleep(0.5)


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
            self.config = read_yaml_file(str(config))["modbus"]
        elif config is None:
            self.config = lvmecp_config["modbus"]
        elif isinstance(config, dict):
            self.config = config

        assert isinstance(self.config, dict)

        self.host = self.config["host"]
        self.port = self.config["port"]
        self.slave = self.config.get("slave", 0)

        # Cache results so that very close calls to get_all() don't need to
        # open a connection and read the registers.
        self.cache_timeout = self.config.get("cache_timeout", 0.5)
        self._register_cache: dict[str, int | float | None] = {}
        self._register_last_seen: float = 0

        self.client = AsyncModbusTcpClient(self.host, port=self.port)

        self.lock = asyncio.Lock()
        self._lock_release_task: asyncio.Task | None = None

        register_data = self.config["registers"]
        registers = {
            name: ModbusRegister(
                self,
                name,
                elem["address"],
                mode=elem.get("mode", "coil"),
                group=elem.get("group", None),
                count=elem.get("count", 1),
                decoder=elem.get("decoder", None),
            )
            for name, elem in register_data.items()
        }

        dict.__init__(self, registers)
        for name, elem in registers.items():
            setattr(self, name, elem)

    async def connect(self):
        """Connects to the client."""

        try:
            await asyncio.wait_for(self.lock.acquire(), TIMEOUT)
        except asyncio.TimeoutError:
            raise RuntimeError("Timed out waiting for lock to be released.")

        hp = f"{self.host}:{self.port}"
        log.debug(f"Trying to connect to modbus server on {hp}")

        did_connect: bool = False

        try:
            await asyncio.wait_for(self.client.connect(), timeout=5)
            did_connect = True
        except asyncio.TimeoutError:
            raise ConnectionError(f"Timed out connecting to server at {hp}.")
        except Exception as err:
            raise ConnectionError(f"Failed connecting to server at {hp}: {err}.")
        finally:
            if not did_connect and self.lock.locked():
                self.lock.release()

        log.debug(f"Connected to {hp}.")

        # Schedule a task to release the lock after 5 seconds. This is a safeguard
        # in case something fails and the connection is never closed and the lock
        # not released.
        self._lock_release_task = asyncio.create_task(self.unlock_on_timeout())

    async def disconnect(self):
        """Disconnects the client."""

        try:
            if self.client:
                self.client.close()
                log.debug(f"Disonnected from {self.host}:{self.port}.")

        finally:
            if self.lock.locked():
                self.lock.release()

            await cancel_task(self._lock_release_task)

    async def __aenter__(self):
        """Initialises the connection to the server."""

        await self.connect()

    async def __aexit__(self, exc_type, exc, tb):
        """Closes the connection to the server."""

        await self.disconnect()

    async def unlock_on_timeout(self):
        """Removes the lock after an amount of time."""

        await asyncio.sleep(TIMEOUT)
        if self.lock.locked():
            self.lock.release()

    async def get_all(self, use_cache: bool = True):
        """Returns a dictionary with all the registers."""

        if use_cache and time() - self._register_last_seen < self.cache_timeout:
            if None not in self._register_cache.values():
                return self._register_cache

        names = results = []

        async with self:
            names = [name for name in self]
            tasks = [
                elem.get(open_connection=False, use_cache=False)
                for elem in self.values()
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

        if any([isinstance(result, Exception) for result in results]):
            for ii, result in enumerate(results):
                if isinstance(result, Exception):
                    log.warning(f"Failed retrieving value for {names[ii]!r}")
                    results[ii] = None

        registers = cast(
            dict[str, int | float | None],
            {names[ii]: results[ii] for ii in range(len(names))},
        )

        self._register_cache = registers
        self._register_last_seen = time()

        return registers

    async def read_group(self, group: str, use_cache: bool = True):
        """Returns a dictionary of all read registers that match a ``group``."""

        registers = await self.get_all(use_cache=use_cache)

        group_registers = {}
        for name in self:
            register = self[name]
            if register.group is not None and register.group == group:
                if name not in registers:
                    continue

                group_registers[name] = registers[name]

        return group_registers
