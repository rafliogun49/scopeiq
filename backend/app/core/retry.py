"""Exponential-backoff retry helper — A-PR5."""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

import httpx

T = TypeVar("T")


async def async_retry(
    fn: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    base_seconds: float = 2.0,
    retry_on: tuple[type[Exception], ...] = (httpx.HTTPError,),
) -> T:
    """Call `fn()` up to `attempts` times with 2x exponential backoff + jitter.

    Raises the last exception if all attempts fail.
    """
    last_exc: Exception
    for i in range(attempts):
        try:
            return await fn()
        except retry_on as exc:
            last_exc = exc
            if i < attempts - 1:
                delay = base_seconds * (2**i) + random.uniform(0, 0.25)
                await asyncio.sleep(delay)
    raise last_exc  # type: ignore[possibly-undefined]
