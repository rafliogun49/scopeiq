"""python_exec MCP tool — interface contract §7.3.

Called by the Orchestrator agent with structured pricing / sentiment data.
Runs Python in a sandboxed subprocess (unshare -n, 30s, 256MB, whitelist).
Returns stdout + base64 PNGs from plt.savefig.

Input:  {code: str, dataset_id: str}
Output: {stdout: str, charts: list[str]}  ← base64 PNGs

Implemented in B-PR2. See PRD §10.3 §13 and TEAM_SPLIT §7.3.
"""
# TODO (B-PR2): subprocess sandbox with unshare -n, cgroup memory cap,
#               whitelisted imports (pandas, numpy, matplotlib, stdlib)


async def python_exec(code: str, dataset_id: str) -> dict:
    """Executes code in sandbox. Returns {stdout, charts}."""
    raise NotImplementedError
