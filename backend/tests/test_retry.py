"""Unit tests for async_retry — A-PR5."""

from __future__ import annotations

import httpx
import pytest

from app.core.retry import async_retry


@pytest.mark.asyncio
async def test_retry_succeeds_on_second_attempt():
    calls = []

    async def flaky():
        calls.append(1)
        if len(calls) < 2:
            raise httpx.ConnectError("timeout")
        return "ok"

    result = await async_retry(flaky, attempts=3, base_seconds=0.0)
    assert result == "ok"
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_retry_raises_after_all_attempts():
    async def always_fail():
        raise httpx.ConnectError("always")

    with pytest.raises(httpx.ConnectError):
        await async_retry(always_fail, attempts=3, base_seconds=0.0)


@pytest.mark.asyncio
async def test_retry_does_not_retry_unlisted_exceptions():
    calls = []

    async def bad():
        calls.append(1)
        raise ValueError("not retryable")

    with pytest.raises(ValueError):
        await async_retry(bad, attempts=3, base_seconds=0.0)

    assert len(calls) == 1  # no retry on ValueError


@pytest.mark.asyncio
async def test_retry_success_first_try():
    async def fine():
        return 42

    result = await async_retry(fine, attempts=3, base_seconds=0.0)
    assert result == 42
