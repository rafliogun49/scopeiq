"""Model pricing table for cost tracking — A-PR5."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# (input_per_1m_tokens, output_per_1m_tokens) in USD
MODEL_PRICES: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (5.00, 15.00),
    "gpt-4o-2024-11-20": (2.50, 10.00),
    "gpt-4o-mini-2024-07-18": (0.15, 0.60),
}

_FALLBACK = "gpt-4o-mini"


def cost_for(model: str, input_tokens: int, output_tokens: int) -> float:
    """Return cost in USD for the given token counts."""
    prices = MODEL_PRICES.get(model)
    if prices is None:
        logger.warning("Unknown model %r for cost calculation; using %s rates", model, _FALLBACK)
        prices = MODEL_PRICES[_FALLBACK]
    input_price, output_price = prices
    return (input_tokens * input_price + output_tokens * output_price) / 1_000_000
