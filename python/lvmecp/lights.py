#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-24
# @Filename: lights.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import TYPE_CHECKING

from lvmecp.maskbits import LightStatus
from lvmecp.tools import loop_coro


if TYPE_CHECKING:
    from .plc import PLC


__all__ = ["LightsController", "CODE_TO_LIGHT", "CODE_TO_FLAG"]


CODE_TO_LIGHT = {
    "cr": "control_room",
    "sr": "spectrograph_room",
    "ur": "utilities_room",
    "uma": "uma_room",
    "tb": "telescope_bright",
    "tr": "telescope_red",
}

CODE_TO_FLAG = {
    "cr": LightStatus.CONTROL_ROOM,
    "sr": LightStatus.SPECTROGRAPH_ROOM,
    "ur": LightStatus.UTILITY_ROOM,
    "uma": LightStatus.UMA_ROOM,
    "tb": LightStatus.TELESCOPE_BRIGHT,
    "tr": LightStatus.TELESCOPE_RED,
}


class LightsController:
    """Controller for the light settings."""

    def __init__(self, plc: PLC):
        self.plc = plc
        self.client = plc.modbus.client

        self.status = LightStatus(0)

        self.__update_loop_task = loop_coro(self.update, 60)

    def __del__(self):
        self.__update_loop_task.cancel()

    async def update(self):
        """Refreshes the lights status."""

        lights = await self.plc.modbus.read_group("lights")

        for light, value in lights.items():
            code = light.split("_")[0]
            flag = CODE_TO_FLAG[code]

            if value is True:
                self.status |= flag
            else:
                self.status &= ~flag

        return self.status

    def get_code(self, light: str):
        """Returns the short-form code for a light. Case-insensitive.

        Parameters
        ----------
        light
            The light for which the code is seeked.

        Examples
        --------
        >>> get_code('telescope_red')
        'tr'
        >>> get_code('telescope bright')
        'tb'
        >>> get_code('uMa Room')
        'uma'

        Raises
        ------
        ValueError
            When a code cannot be found for the input light.

        """

        light = light.lower()

        if light in CODE_TO_LIGHT:
            return light

        for code, descr in CODE_TO_LIGHT.items():
            if light == descr:
                return code

            for repl in [" ", "-", ""]:
                if light == descr.replace("_", repl):
                    return code

        raise ValueError(f"Cannot find matching code for {light!r}.")

    def get_flag(self, light: str):
        """Gets the `.LightStatus` flag associated with a light.

        Parameters
        ----------
        light
            The light for which the `.LightStatus` a flag is requested. It can
            be specified in short form (e.g., `tr`), using underscores
            (`telescope_red`), or spaces (`telescope red`). The light name
            is case-insensitive.

        """

        code = self.get_code(light)

        return CODE_TO_FLAG[code]

    async def get_light_status(self, light: str, update: bool = True) -> bool:
        """Returns the status of a light.

        Parameters
        ----------
        light
            The light for which to get the status.
        update
            Whether to update the status of all lights before returning
            the status. If `False`, the last cached status will be used.

        Returns
        -------
        status
            `True` if the light is on, `False` otherwise.

        Raises
        ------
        ValueError
            If the light is unknown.

        """

        if update:
            await self.update()

        flag = self.get_flag(light)

        return bool(self.status & flag)

    async def get_all(self, update: bool = True) -> dict[str, bool]:
        """Returns a dictionary with the status of all the lights.

        Parameters
        ----------
        update
            Whether to update the status of all lights before returning.
            If `False`, the last cached status will be used.

        Returns
        -------
        status
            A dictionary of light name to status (`True` for on, `False` for off).

        """

        if update:
            await self.update()

        status = {}
        for code, light in CODE_TO_LIGHT.items():
            status[light] = bool(self.status & CODE_TO_FLAG[code])

        return status

    async def set(self, light: str, action: bool | None = None):
        """Turns a light on/off.

        Updates the internal status dictionary.

        Parameters
        ----------
        light
            The light to command.
        action
            `True` to turn on the light, `False` for off. If `None`, the light
            status will be switched. Doesn't do anything if the light is
            already at the desired state.

        """

        current = await self.get_light_status(light, update=True)

        code_new = self.get_code(light) + "_new"

        if action is None:
            action = not current

        if current == action:
            return

        await self.plc.modbus[code_new].set(action)

        flag = self.get_flag(light)
        if action is True:
            self.status |= flag
        else:
            self.status &= ~flag
