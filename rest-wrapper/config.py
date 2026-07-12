import os

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://dflynn5656-astro-rag-mcp.hf.space/mcp")
API_KEY = os.getenv("REST_API_KEY", None)
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8080))
