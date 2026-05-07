"""MCP server entrypoint — implemented in B-PR2.

Exposes two tools over the MCP protocol:
  • python_exec — sandboxed Python execution (contract §7.3)
  • rag_query   — pgvector retrieval (contract §7.4)

Run via:  python -m mcp_server.server
See PRD §10.3 and TEAM_SPLIT §4 (B-PR2).
"""
# TODO (B-PR2): wire up mcp.Server with python_exec + rag_query handlers
# Acceptance: container starts; smoke test produces a valid base64 PNG

if __name__ == "__main__":
    raise NotImplementedError("MCP server not implemented yet — see B-PR2")
