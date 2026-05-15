"""Unit tests for RunBudget and pricing — A-PR5."""

from __future__ import annotations

import pytest

from app.core.pricing import cost_for
from app.workers.budget import BudgetExceeded, RunBudget


def _budget(**kwargs) -> RunBudget:
    defaults = dict(
        max_input_tokens=1000,
        max_output_tokens=500,
        max_fetches=5,
        max_searches=3,
        max_agent_turns=2,
    )
    defaults.update(kwargs)
    return RunBudget(**defaults)


# ── cost_for ──────────────────────────────────────────────────────────────────


def test_cost_for_gpt4o_mini():
    # 1M input @ $0.15/M + 1M output @ $0.60/M = $0.75
    assert cost_for("gpt-4o-mini", 1_000_000, 1_000_000) == pytest.approx(0.75)


def test_cost_for_gpt4o():
    # 1M input @ $5/M + 1M output @ $15/M = $20
    assert cost_for("gpt-4o", 1_000_000, 1_000_000) == pytest.approx(20.0)


def test_cost_for_unknown_model_falls_back():
    # Unknown model should not raise; uses gpt-4o-mini rates
    cost = cost_for("gpt-unknown", 1_000_000, 0)
    assert cost == pytest.approx(0.15)


# ── add_tokens ────────────────────────────────────────────────────────────────


def test_add_tokens_accumulates():
    b = _budget()
    b.add_tokens(100, 50, "gpt-4o-mini")
    b.add_tokens(200, 100, "gpt-4o-mini")
    assert b.input_tokens == 300
    assert b.output_tokens == 150
    assert b.cost_usd > 0


def test_add_tokens_raises_on_input_overflow():
    b = _budget(max_input_tokens=100)
    with pytest.raises(BudgetExceeded) as exc_info:
        b.add_tokens(101, 0, "gpt-4o-mini")
    assert exc_info.value.reason == "input_tokens"


def test_add_tokens_raises_on_output_overflow():
    b = _budget(max_output_tokens=10)
    with pytest.raises(BudgetExceeded) as exc_info:
        b.add_tokens(0, 11, "gpt-4o-mini")
    assert exc_info.value.reason == "output_tokens"


def test_add_tokens_partial_counters_persist_after_raise():
    b = _budget(max_input_tokens=50)
    b.add_tokens(30, 0, "gpt-4o-mini")  # ok
    with pytest.raises(BudgetExceeded):
        b.add_tokens(30, 0, "gpt-4o-mini")  # pushes total to 60, over cap
    # Counters include the tokens that caused the overflow
    assert b.input_tokens == 60


# ── record_tool_call ──────────────────────────────────────────────────────────


def test_record_tool_call_fetch_ok():
    b = _budget(max_fetches=3)
    for _ in range(3):
        b.record_tool_call("fetch")
    assert b.fetches == 3


def test_record_tool_call_fetch_raises_over_cap():
    b = _budget(max_fetches=2)
    b.record_tool_call("fetch")
    b.record_tool_call("fetch")
    with pytest.raises(BudgetExceeded) as exc_info:
        b.record_tool_call("fetch")
    assert exc_info.value.reason == "fetches"


def test_record_tool_call_search_raises_over_cap():
    b = _budget(max_searches=1)
    b.record_tool_call("search")
    with pytest.raises(BudgetExceeded) as exc_info:
        b.record_tool_call("search")
    assert exc_info.value.reason == "searches"


# ── check_turn ────────────────────────────────────────────────────────────────


def test_check_turn_ok():
    b = _budget(max_agent_turns=2)
    b.check_turn("orchestrator")
    b.check_turn("orchestrator")  # at cap, not over


def test_check_turn_raises_over_cap():
    b = _budget(max_agent_turns=1)
    b.check_turn("orchestrator")
    with pytest.raises(BudgetExceeded) as exc_info:
        b.check_turn("orchestrator")
    assert exc_info.value.reason == "agent_turns"


def test_check_turn_independent_per_agent():
    b = _budget(max_agent_turns=1)
    b.check_turn("orchestrator")  # uses orchestrator's slot
    b.check_turn("scraper")  # scraper starts fresh — should be fine


# ── caps_snapshot ─────────────────────────────────────────────────────────────


def test_caps_snapshot_has_all_keys():
    b = _budget()
    snap = b.caps_snapshot()
    for key in (
        "max_input_tokens",
        "max_output_tokens",
        "max_fetches",
        "max_searches",
        "max_agent_turns",
    ):
        assert key in snap
