#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-24
# @Filename: tools.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
from typing import Any, Callable, Coroutine


__all__ = ["loop_coro"]


def loop_coro(
    coro: Coroutine[Any, Any, Any] | Callable[[], Any],
    interval: float = 1.0,
) -> asyncio.Task:
    """Creates a task that calls a function or coroutine on an interval."""

    async def _task_body():

        while True:
            if asyncio.iscoroutine(coro):
                await coro
            elif callable(coro):
                if asyncio.iscoroutinefunction(coro):
                    await coro()
                else:
                    coro()

            await asyncio.sleep(interval)

    return asyncio.create_task(_task_body())
