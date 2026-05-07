"""rag_query MCP tool — interface contract §7.4.

Called by the Synthesizer agent to ground each report section.

Input:  {query: str, run_id: str, top_k: int = 8}
Output: [{chunk: str, source_url: str, score: float}]

Implemented in B-PR2. See PRD §10.3 and TEAM_SPLIT §7.4.
"""
# TODO (B-PR2): call app.rag.retrieval.query via the DB session


async def rag_query(query: str, run_id: str, top_k: int = 8) -> list[dict]:
    """Vector search scoped to run_id. Returns ranked chunks with source URLs."""
    raise NotImplementedError
