"""Orchestrator agent — implemented in A-PR4.

Plans the run, dispatches Scraper + Social, calls python_exec directly,
hands off to Synthesizer. Uses gpt-4o-mini.
See PRD §10 and TEAM_SPLIT §3 (A-PR4).
"""
# TODO (A-PR4): define orchestrator Agent using openai-agents SDK
# Example skeleton:
#
# from agents import Agent, handoff
# from app.tools.http_fetch import http_fetch
# from app.tools.python_exec_client import python_exec
#
# orchestrator = Agent(
#     name="Orchestrator",
#     model="gpt-4o-mini",
#     instructions=open("prompts/orchestrator.md").read(),
#     tools=[python_exec, handoff(scraper), handoff(synthesizer)],
# )
