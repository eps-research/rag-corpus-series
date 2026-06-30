import asyncio
import logging
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from config import MCP_SERVER_URL

logger = logging.getLogger(__name__)

async def call_tool(tool_name, arguments):
    arguments = {k: v for k, v in arguments.items() if v is not None}
    
    result_holder = {}
    
    async def _run():
        async with streamablehttp_client(MCP_SERVER_URL) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                result_holder["result"] = result
    
    await _run()
    
    result = result_holder["result"]
    if result.isError:
        raise RuntimeError(f"MCP tool error: {result.content}")
    if result.content and len(result.content) == 1:
        block = result.content[0]
        if hasattr(block, "text"):
            try:
                return json.loads(block.text)
            except (json.JSONDecodeError, TypeError):
                return block.text
    return [block.model_dump() for block in result.content]

async def close_session():
    pass
