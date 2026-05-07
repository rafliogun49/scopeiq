"""Eval pipeline — implemented in B-PR5.

Runs the system on 10 hand-curated indie-founder ideas from dataset.jsonl.
Scores via LLM-judge + assertion checks.
Metrics: accuracy, coverage (≥3 competitors), citation density, cost, latency.

Run nightly only (not on every PR — saves CI cost).
See PRD §10.5 and TEAM_SPLIT §4 (B-PR5).
"""
# TODO (B-PR5)

if __name__ == "__main__":
    raise NotImplementedError("Eval pipeline not implemented yet — see B-PR5")
