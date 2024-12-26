#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-24
# @Filename: tools.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
from contextlib import suppress
from datetime import datetime, timezone

from typing import Any, Callable, Coroutine


__all__ = ["loop_coro", "cancel_tasks_by_name", "timestamp_to_iso"]


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


async def cancel_tasks_by_name(name: str):
    """Cancels all tasks with ``name``."""

    tasks = [tasks for tasks in asyncio.all_tasks() if tasks.get_name() == name]
    for task in tasks:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


def timestamp_to_iso(ts: float | None, timespec: str = "seconds") -> str | None:
    """Converts a timestamp to an ISO string."""

    if ts is None:
        return None

    return (
        datetime.fromtimestamp(ts, timezone.utc)
        .isoformat(timespec=timespec)
        .replace("+00:00", "Z")
    )
