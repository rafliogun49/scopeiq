"""Per-run budget tracker — A-PR5.

Mirrors the run_id_var contextvar pattern from run_events.py.
Tools and the agent runner mutate the RunBudget; when a cap is exceeded,
BudgetExceeded is raised and the Celery task marks the run failed.
"""
from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Literal

from app.core.pricing import cost_for


class BudgetExceeded(Exception):
    """Raised when any per-run budget cap is breached."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"budget_exceeded: {reason}")


Category = Literal["fetch", "search"]


@dataclass
class RunBudget:
    # caps (set from settings at task start)
    max_input_tokens: int = 100_000
    max_output_tokens: int = 25_000
    max_fetches: int = 15
    max_searches: int = 8
    max_agent_turns: int = 12

    # running totals
    input_tokens: int = 0
    output_tokens: int = 0
    fetches: int = 0
    searches: int = 0
    cost_usd: float = 0.0
    _turns: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_settings(cls) -> "RunBudget":
        from app.core.config import settings

        return cls(
            max_input_tokens=settings.BUDGET_INPUT_TOKENS,
            max_output_tokens=settings.BUDGET_OUTPUT_TOKENS,
            max_fetches=settings.MAX_FETCHES,
            max_searches=settings.MAX_SEARCHES,
            max_agent_turns=settings.MAX_AGENT_TURNS,
        )

    def caps_snapshot(self) -> dict:
        return {
            "max_input_tokens": self.max_input_tokens,
            "max_output_tokens": self.max_output_tokens,
            "max_fetches": self.max_fetches,
            "max_searches": self.max_searches,
            "max_agent_turns": self.max_agent_turns,
        }

    def add_tokens(self, input_tokens: int, output_tokens: int, model: str) -> None:
        """Accumulate token counts and update cost. Raises BudgetExceeded if over cap."""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.cost_usd += cost_for(model, input_tokens, output_tokens)
        if self.input_tokens > self.max_input_tokens:
            raise BudgetExceeded("input_tokens")
        if self.output_tokens > self.max_output_tokens:
            raise BudgetExceeded("output_tokens")

    def record_tool_call(self, category: Category) -> None:
        """Increment tool-call counter. Raises BudgetExceeded if cap reached."""
        if category == "fetch":
            self.fetches += 1
            if self.fetches > self.max_fetches:
                raise BudgetExceeded("fetches")
        elif category == "search":
            self.searches += 1
            if self.searches > self.max_searches:
                raise BudgetExceeded("searches")

    def check_turn(self, agent: str) -> None:
        """Increment per-agent turn counter. Raises BudgetExceeded if cap reached."""
        self._turns[agent] = self._turns.get(agent, 0) + 1
        if self._turns[agent] > self.max_agent_turns:
            raise BudgetExceeded("agent_turns")


budget_var: ContextVar[RunBudget | None] = ContextVar("scopeiq_budget", default=None)


def get_budget() -> RunBudget | None:
    """Return the current run's budget, or None if outside a run context."""
    return budget_var.get()
