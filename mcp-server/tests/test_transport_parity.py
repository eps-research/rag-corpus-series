"""REST and MCP must return the same envelope for the same request, over every
transport the server offers: in-process MCP, real Streamable HTTP on a socket,
and stdio (the mode desktop MCP clients use to launch the server)."""

import json
import os
import sys

import anyio
import pytest


from astro_rag_mcp.server import build_mcp

from .conftest import SERVER_ROOT, rest

CASES = [
    ("list_corpora", {}),
    ("list_objects", {"corpus": "gc", "limit": 7, "offset": 3}),
    ("list_objects", {"corpus": "v7", "survey": "THINGS", "quality_tier": 1}),
    ("get_object", {"corpus": "v7", "object_id": "NGC0024"}),
    ("get_object", {"corpus": "v7", "object_id": "NGC3198"}),            # error: ambiguous
    ("get_object", {"corpus": "z1", "object_id": "nope"}),               # error: not found
    ("search_metadata", {"corpus": "dwarf", "field": "survey", "value": "LVHIS"}),
    ("filter_objects", {"corpus": "v7", "field": "distance_mpc", "min_val": 1, "max_val": 10}),
    ("filter_objects", {"corpus": "intz", "field": "z_spec", "min_val": 0.5, "max_val": 1.0}),
    ("filter_objects", {"corpus": "v7", "field": "bogus", "min_val": 1}),   # error: unknown field
    ("get_corpus_schema", {"corpus": "z1"}),
    ("semantic_search", {"corpus": "z1", "query": "rotator", "top_k": 5}),
    ("semantic_search", {"corpus": "all", "query": "metal poor halo", "top_k": 8}),
]
EXPECTED_TOOLS = {"list_corpora", "list_objects", "get_object", "search_metadata",
                  "filter_objects", "get_corpus_schema", "semantic_search"}


def _payload(result):
    """Decode an MCP CallToolResult into the envelope dict."""
    if getattr(result, "structuredContent", None):
        sc = result.structuredContent
        return sc.get("result", sc) if set(sc) == {"result"} else sc
    return json.loads(result.content[0].text)


async def _mcp_calls(session):
    tools = await session.list_tools()
    names = {t.name for t in tools.tools}
    out = []
    for tool, args in CASES:
        out.append(_payload(await session.call_tool(tool, args)))
    return names, out


def _rest_calls(client):
    out = []
    for tool, args in CASES:
        _, body = rest(client, tool, **args)
        out.append(body)
    return out


def test_rest_status_codes(client):
    assert rest(client, "get_object", corpus="v7", object_id="NGC0024")[0] == 200
    assert rest(client, "get_object", corpus="v7", object_id="NGC3198")[0] == 409
    assert rest(client, "get_object", corpus="v7", object_id="zzzz")[0] == 404
    assert rest(client, "list_objects", corpus="xx")[0] == 400


def test_rest_parameter_aliases(client):
    a = rest(client, "filter_objects", corpus="v7", field="distance_mpc", min=1, max=10)[1]
    b = rest(client, "filter_objects", corpus="v7", field="distance_mpc", min_val=1, max_val=10)[1]
    assert a == b and a["data"]["n_matched"] == b["data"]["n_matched"]
    p = rest(client, "list_objects", corpus="v7", page=3, limit=10)[1]
    o = rest(client, "list_objects", corpus="v7", offset=20, limit=10)[1]
    assert p == o
    t = rest(client, "list_objects", corpus="v7", tier=1)[1]
    q = rest(client, "list_objects", corpus="v7", quality_tier=1)[1]
    assert t == q


def test_ui_docs_health(client):
    assert client.get("/").status_code == 200
    assert "semantic_search" in client.get("/").text
    assert client.get("/docs").status_code == 200
    spec = client.get("/openapi.json").json()
    assert {p.split("/api/")[1] for p in spec["paths"] if p.startswith("/api/")} == EXPECTED_TOOLS
    h = client.get("/health").json()
    assert h["status"] in ("ok", "degraded") and h["n_total"] == 2064
    stale = [k for k, i in h["semantic_search"]["indexes"].items() if i["state"] == "stale"]
    assert (h["status"] == "degraded") == bool(stale)


def test_parity_in_process(service, client):
    from mcp.shared.memory import create_connected_server_and_client_session

    mcp = build_mcp(service)

    async def go():
        async with create_connected_server_and_client_session(mcp._mcp_server) as s:
            return await _mcp_calls(s)

    names, via_mcp = anyio.run(go)
    assert names == EXPECTED_TOOLS
    assert via_mcp == _rest_calls(client)


def test_parity_streamable_http_socket(live_server, client):
    """A real MCP client over a real socket to /mcp (what Claude, LM Studio etc. do)."""
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    async def go():
        async with streamablehttp_client(f"{live_server}/mcp") as (r, w, _):
            async with ClientSession(r, w) as s:
                await s.initialize()
                return await _mcp_calls(s)

    names, via_mcp = anyio.run(go)
    assert names == EXPECTED_TOOLS
    assert via_mcp == _rest_calls(client)


def test_dns_rebinding_protection_on_loopback(live_server):
    import httpx

    r = httpx.post(f"{live_server}/mcp", headers={"Host": "evil.example.com",
                   "Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
                   json={"jsonrpc": "2.0", "id": 1, "method": "ping"})
    assert r.status_code in (400, 403, 421)


def test_stdio_transport(service, client):
    """Launch the server the way a desktop MCP client does (subprocess, stdio)."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "astro_rag_mcp", "serve", "--transport", "stdio", "--no-semantic",
              "--log-level", "WARNING"],
        cwd=str(SERVER_ROOT),
        env={**os.environ, "PYTHONPATH": str(SERVER_ROOT)},
    )

    async def go():
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                names = {t.name for t in (await s.list_tools()).tools}
                obj = _payload(await s.call_tool("get_object", {"corpus": "v7", "object_id": "NGC0024"}))
                filt = _payload(await s.call_tool("filter_objects",
                                                  {"corpus": "intz", "field": "z_spec",
                                                   "min_val": 0.5, "max_val": 1.0}))
                return names, obj, filt

    names, obj, filt = anyio.run(go)
    assert names == EXPECTED_TOOLS
    assert obj == rest(client, "get_object", corpus="v7", object_id="NGC0024")[1]
    assert filt["data"]["n_matched"] == 822


def test_server_info_reports_release_version(live_server):
    """MCP serverInfo must identify this release, not the SDK version."""
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    from astro_rag_mcp import __version__

    async def go():
        async with streamablehttp_client(f"{live_server}/mcp") as (r, w, _):
            async with ClientSession(r, w) as s:
                return (await s.initialize()).serverInfo

    info = anyio.run(go)
    assert info.name == "eps-astro-rag-mcp" and info.version == __version__
