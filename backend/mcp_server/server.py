"""MCP server entrypoint — B-PR2."""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from mcp_server.python_exec import python_exec
from mcp_server.rag_query import rag_query

app = Server("scopeiq-mcp")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="python_exec",
            description="Jalankan Python di sandbox. Cocok untuk chart & analisis data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python source code"},
                    "dataset_id": {"type": "string", "description": "JSON string dataset"},
                },
                "required": ["code", "dataset_id"],
            },
        ),
        types.Tool(
            name="rag_query",
            description="Vector search ke pgvector, scoped per run_id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "run_id": {"type": "string", "description": "UUID run"},
                    "top_k": {"type": "integer", "default": 8},
                },
                "required": ["query", "run_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "python_exec":
        result = await python_exec(
            code=arguments["code"],
            dataset_id=arguments.get("dataset_id", "{}"),
        )
        return [types.TextContent(type="text", text=json.dumps(result))]

    elif name == "rag_query":
        result = await rag_query(
            query=arguments["query"],
            run_id=arguments["run_id"],
            top_k=arguments.get("top_k", 8),
        )
        return [types.TextContent(type="text", text=json.dumps(result))]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
