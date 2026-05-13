"""Langfuse observability + prompt management — A-PR6.

Two surfaces:
  • get_client()   → wrapper with update_current_span / start_observation / get_prompt
  • observe(...)   → decorator that creates a Langfuse span around a function

Both surfaces degrade gracefully to no-ops when Langfuse credentials are absent,
so tests and local dev work without a Langfuse account.
"""
from __future__ import annotations

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

try:
    from langfuse import Langfuse
    from langfuse.decorators import langfuse_context
    from langfuse.decorators import observe as _lf_observe

    _LANGFUSE_AVAILABLE = True
except ImportError:  # pragma: no cover
    _LANGFUSE_AVAILABLE = False
    logger.warning("langfuse package not installed — observability disabled")


# ---------------------------------------------------------------------------
# Noop fallbacks (used when Langfuse is not configured)
# ---------------------------------------------------------------------------

class _NoopSpan:
    def update(self, **kwargs: Any) -> "_NoopSpan":
        return self

    def end(self, **kwargs: Any) -> None:
        pass


# ---------------------------------------------------------------------------
# Real handle returned by start_observation
# ---------------------------------------------------------------------------

class _TraceHandle:
    """Wraps a Langfuse trace, exposing the update/end interface expected by tasks.py."""

    def __init__(self, trace: Any, client: "Langfuse") -> None:
        self._trace = trace
        self._client = client

    def update(self, metadata: dict[str, Any] | None = None, **kwargs: Any) -> "_TraceHandle":
        try:
            self._trace.update(metadata=metadata or {})
        except Exception as exc:
            logger.debug("Langfuse trace update failed: %s", exc)
        return self

    def end(self) -> None:
        try:
            self._client.flush()
        except Exception as exc:
            logger.debug("Langfuse flush failed: %s", exc)


# ---------------------------------------------------------------------------
# Central wrapper
# ---------------------------------------------------------------------------

class _LangfuseWrapper:
    def __init__(self) -> None:
        self._client: "Langfuse | None" = None
        self._initialized = False

    def _get(self) -> "Langfuse | None":
        if not _LANGFUSE_AVAILABLE:
            return None
        if not self._initialized:
            self._initialized = True
            try:
                from app.core.config import settings

                if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
                    self._client = Langfuse(
                        public_key=settings.LANGFUSE_PUBLIC_KEY,
                        secret_key=settings.LANGFUSE_SECRET_KEY,
                        host=settings.LANGFUSE_HOST,
                    )
                    logger.info("Langfuse client initialised (host=%s)", settings.LANGFUSE_HOST)
                else:
                    logger.info("Langfuse keys not set — observability disabled")
            except Exception as exc:
                logger.warning("Langfuse init failed: %s", exc)
        return self._client

    # -- used inside @observe-decorated functions ----------------------------

    def update_current_span(self, metadata: dict[str, Any]) -> None:
        if not _LANGFUSE_AVAILABLE:
            return
        try:
            langfuse_context.update_current_observation(metadata=metadata)
        except Exception as exc:
            logger.debug("update_current_span failed: %s", exc)

    # -- used outside @observe (e.g. in Celery tasks) -----------------------

    def start_observation(
        self,
        name: str,
        as_type: str = "span",
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        client = self._get()
        if client is None:
            return _NoopSpan()
        try:
            trace = client.trace(name=name, metadata=metadata or {})
            return _TraceHandle(trace, client)
        except Exception as exc:
            logger.debug("start_observation failed: %s", exc)
            return _NoopSpan()

    # -- prompt management ---------------------------------------------------

    def get_prompt(self, name: str, *, fallback: str = "") -> str:
        """Return the compiled Langfuse text prompt called *name*, or *fallback*."""
        client = self._get()
        if client is None:
            return fallback
        try:
            prompt_client = client.get_prompt(name, type="text", cache_ttl_seconds=60)
            return prompt_client.compile()
        except Exception:
            logger.debug("Langfuse prompt %r not found — using local fallback", name)
            return fallback


_wrapper = _LangfuseWrapper()


def get_client() -> _LangfuseWrapper:
    return _wrapper


# ---------------------------------------------------------------------------
# @observe decorator
# ---------------------------------------------------------------------------

def observe(name: str, as_type: str = "span") -> Callable:
    """Wrap a sync or async function with a Langfuse observation.

    *as_type* is passed through only when Langfuse supports it ('generation');
    other values (e.g. 'agent') are silently treated as a plain span to avoid
    SDK validation errors.
    """
    if _LANGFUSE_AVAILABLE:
        try:
            kwargs: dict[str, Any] = {"name": name}
            if as_type == "generation":
                kwargs["as_type"] = "generation"
            return _lf_observe(**kwargs)
        except Exception as exc:
            logger.debug("observe decorator setup failed: %s", exc)

    def _passthrough(fn: Callable) -> Callable:
        return fn

    return _passthrough
