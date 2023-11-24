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
import warnings
from contextlib import suppress

from pymodbus.client.tcp import AsyncModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

from sdsstools import read_yaml_file

from lvmecp import config as lvmecp_config
from lvmecp import log
from lvmecp.exceptions import ECPWarning


MAX_RETRIES = 3


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

        return value

    async def get(self, open_connection: bool = True):
        """Return the value of the modbus register. Implements retry."""

        for ntries in range(1, MAX_RETRIES + 1):
            # If we need to open the connection, use the Modbus context
            # and call ourselves recursively with open_connection=False
            # (at that point it will be open).
            if open_connection:
                await self.modbus.connect()

            try:
                return await self._get_internal()
            except Exception as err:
                if ntries >= MAX_RETRIES:
                    raise

                warnings.warn(
                    f"Failed getting status of {self.name!r}: {err}",
                    ECPWarning,
                )
                open_connection = True  # Force a reconnection.
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

                if self.client.connected:
                    resp = await func(self.address, value)  # type: ignore
                else:
                    async with self.modbus:
                        resp = await func(self.address, value)  # type: ignore

                if resp.function_code > 0x80:
                    msg = (
                        f"Invalid response for element "
                        f"{self.name!r}: 0x{resp.function_code:02X}."
                    )

                    if ntries >= MAX_RETRIES:
                        raise ValueError(msg)

                    warnings.warn(msg, ECPWarning)
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
            self.config = read_yaml_file(str(config))
        elif config is None:
            self.config = lvmecp_config["modbus"]
        elif isinstance(config, dict):
            self.config = config

        assert isinstance(config, dict)

        self.host = self.config["host"]
        self.port = self.config["port"]
        self.slave = self.config.get("slave", 0)

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

        hp = f"{self.host}:{self.port}"
        log.debug(f"Trying to connect to modbus server on {hp}")

        try:
            await asyncio.wait_for(self.client.connect(), timeout=5)
        except asyncio.TimeoutError:
            raise ConnectionError(f"Timed out connecting to server at {hp}.")
        except Exception as err:
            raise ConnectionError(f"Failed connecting to server at {hp}: {err}.")

        log.debug(f"Connected to {hp}.")

    async def disconnect(self):
        """Disconnects the client."""

        if self.client:
            self.client.close()

        log.debug(f"Disonnected from {self.host}:{self.port}.")

    async def __aenter__(self):
        """Initialises the connection to the server."""

        try:
            await asyncio.wait_for(self.lock.acquire(), 10)
        except asyncio.TimeoutError:
            raise RuntimeError("Timed out waiting for lock to be released.")

        try:
            await self.connect()
        except Exception:
            if self.lock.locked():
                self.lock.release()

            raise

        # Schedule a task to release the lock after 5 seconds. This is a safeguard
        # in case something fails and the connection is never closed and the lock
        # not released.
        self._lock_release_task = asyncio.create_task(self.unlock_on_timeout())

    async def __aexit__(self, exc_type, exc, tb):
        """Closes the connection to the server."""

        try:
            await self.disconnect()
        finally:
            if self.lock.locked():
                self.lock.release()

            if self._lock_release_task and not self._lock_release_task.done():
                self._lock_release_task.cancel()
                with suppress(asyncio.CancelledError):
                    await self._lock_release_task

    async def unlock_on_timeout(self):
        """Removes the lock after an amount of time."""

        await asyncio.sleep(10)
        if self.lock.locked():
            self.lock.release()

    async def get_all(self):
        """Returns a dictionary with all the registers."""

        names = results = []

        async with self:
            names = [name for name in self]
            tasks = [elem.get(open_connection=False) for elem in self.values()]

            results = await asyncio.gather(*tasks, return_exceptions=True)

        if any([isinstance(result, Exception) for result in results]):
            for result in results:
                if isinstance(result, Exception):
                    log.warning(
                        "Failed retrieving all registers. First exception:",
                        exc_info=result,
                    )
                    break

        return {
            names[ii]: results[ii]
            for ii in range(len(names))
            if not isinstance(results[ii], Exception)
        }

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
