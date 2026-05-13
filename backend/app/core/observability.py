"""Langfuse observability helpers — A-PR6.

Re-exports `observe` from the langfuse package. When LANGFUSE_PUBLIC_KEY is
not set the SDK self-disables and all decorated calls are no-ops, so this
module is safe to import in tests without any key configured.
"""
from __future__ import annotations

from langfuse import get_client, observe

__all__ = ["observe", "get_client"]
