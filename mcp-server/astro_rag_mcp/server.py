"""MCP tools, REST endpoints and the browser UI, served from one process.

Routes (HTTP mode):

    POST/GET /mcp            Model Context Protocol, Streamable HTTP (JSON-RPC 2.0)
    GET      /api/<tool>     REST equivalent of each of the seven tools
    GET      /docs           OpenAPI (Swagger) documentation for the REST API
    GET      /health         Liveness, data versions, checksum and FAISS status
    GET      /               Browser query interface

There is no separate SSE endpoint. Every MCP tool and REST endpoint calls
:meth:`CorpusService.call`, so both interfaces return the same envelope.
"""

from __future__ import annotations

import contextlib
import ipaddress
import logging
from pathlib import Path
from typing import Annotated, Optional

import anyio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import Field

from . import __version__
from .config import CORPUS_KEYS, resolve_data_layout
from .corpus_service import CorpusService
from .semantic import SemanticIndex

logger = logging.getLogger("astro_rag_mcp")
STATIC_DIR = Path(__file__).resolve().parent / "static"

INSTRUCTIONS = (
    "EPS Research Astro-RAG: five DOI-versioned astrophysical kinematic corpora "
    "(v7 HI rotation curves, dwarf, gc Milky Way globular clusters, intz z~0.4-2.7, "
    "z1 ALPINE z~4.3-5.7; 2,064 objects). Start with list_corpora. Use get_corpus_schema "
    "to learn field names, filter_objects for numeric ranges, search_metadata for text, "
    "semantic_search for natural-language discovery, and get_object for the authoritative "
    "record. Semantic rank is not a measurement: take values from get_object. IDs are "
    "'SURVEY:name' (e.g. 'SPARC:NGC0024'); bare names work when unique. Every response "
    "carries provenance; read any correction_notice or warnings before using omega values."
)

CorpusKey = Annotated[str, Field(description="Corpus key: v7, dwarf, gc, intz or z1")]


def _security(host: str) -> TransportSecuritySettings:
    """DNS-rebinding protection for loopback binds; open for public deployments."""
    try:
        loopback = host in ("localhost",) or ipaddress.ip_address(host).is_loopback
    except ValueError:
        loopback = False
    if loopback:
        return TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=["127.0.0.1:*", "localhost:*", "[::1]:*", "127.0.0.1", "localhost"],
            allowed_origins=["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"],
        )
    return TransportSecuritySettings(enable_dns_rebinding_protection=False)


def build_service(data_dir: Optional[str] = None, semantic: bool = True,
                  encoder=None) -> CorpusService:
    layout = resolve_data_layout(data_dir)
    service = CorpusService(layout)
    service.load()
    if semantic:
        service.semantic = SemanticIndex(layout, service.corpora, encoder=encoder)
    return service


def build_mcp(service: CorpusService, host: str = "127.0.0.1", port: int = 8080) -> FastMCP:
    mcp = FastMCP(
        name="eps-astro-rag-mcp",
        instructions=INSTRUCTIONS,
        host=host,
        port=port,
        streamable_http_path="/mcp",
        stateless_http=True,
        transport_security=_security(host),
    )
    # Report this server's release, not the MCP SDK's version, in serverInfo.
    mcp._mcp_server.version = __version__

    async def run(tool: str, **kw) -> dict:
        return await anyio.to_thread.run_sync(lambda: service.call(tool, **kw))

    @mcp.tool(description="List the five corpora with version, object count, redshift range, "
                          "tracer, Zenodo DOI, data checksum and correction notices. Call this first.")
    async def list_corpora() -> dict:
        return await run("list_corpora")

    @mcp.tool(description="List object IDs in a corpus, optionally filtered by survey "
                          "(e.g. SPARC, THINGS, KROSS) or integer quality tier. Paginated.")
    async def list_objects(
        corpus: CorpusKey,
        survey: Annotated[Optional[str], Field(description="Survey name, case-insensitive")] = None,
        quality_tier: Annotated[Optional[int], Field(description="Quality tier, e.g. 1 or 2")] = None,
        limit: Annotated[int, Field(ge=1, le=500)] = 100,
        offset: Annotated[int, Field(ge=0)] = 0,
    ) -> dict:
        return await run("list_objects", corpus=corpus, survey=survey,
                         quality_tier=quality_tier, limit=limit, offset=offset)

    @mcp.tool(description="Return the full authoritative record for one object, with provenance. "
                          "IDs are 'SURVEY:name' (e.g. 'SPARC:NGC0024', 'THINGS:NGC3198'); bare names "
                          "and spacing/case variants ('DDO 154', 'ddo154') work when unique. "
                          "If a name is ambiguous the error lists the qualified IDs to use.")
    async def get_object(corpus: CorpusKey,
                         object_id: Annotated[str, Field(description="Object identifier")]) -> dict:
        return await run("get_object", corpus=corpus, object_id=object_id)

    @mcp.tool(description="Case-insensitive substring search on one metadata field "
                          "(spaces/underscores/hyphens ignored). Field may be a top-level name, "
                          "a dotted path such as 'identifiers.survey', or a unique nested name.")
    async def search_metadata(
        corpus: CorpusKey,
        field: Annotated[str, Field(description="Field name or dotted path")],
        value: Annotated[str, Field(description="Text to look for")],
        limit: Annotated[int, Field(ge=1, le=500)] = 100,
        offset: Annotated[int, Field(ge=0)] = 0,
    ) -> dict:
        return await run("search_metadata", corpus=corpus, field=field, value=value,
                         limit=limit, offset=offset)

    @mcp.tool(description="Numeric range filter (inclusive) on one field, e.g. field='distance_mpc', "
                          "min_val=1, max_val=10, or field='z_spec' (resolves to redshift.z_spec in intz). "
                          "omega_ready_only keeps records with a currently valid omega value.")
    async def filter_objects(
        corpus: CorpusKey,
        field: Annotated[str, Field(description="Numeric field name or dotted path")],
        min_val: Annotated[Optional[float], Field(description="Lower bound, inclusive")] = None,
        max_val: Annotated[Optional[float], Field(description="Upper bound, inclusive")] = None,
        omega_ready_only: bool = False,
        limit: Annotated[int, Field(ge=1, le=500)] = 100,
        offset: Annotated[int, Field(ge=0)] = 0,
    ) -> dict:
        return await run("filter_objects", corpus=corpus, field=field, min_val=min_val,
                         max_val=max_val, omega_ready_only=omega_ready_only,
                         limit=limit, offset=offset)

    @mcp.tool(description="List every metadata field (dotted paths, types, non-null counts) and the "
                          "rotation-curve data columns for a corpus.")
    async def get_corpus_schema(corpus: CorpusKey) -> dict:
        return await run("get_corpus_schema", corpus=corpus)

    @mcp.tool(description="Natural-language similarity search over curated record summaries using "
                          "FAISS (all-MiniLM-L6-v2, exact IndexFlatL2). corpus may be one key or 'all'. "
                          "Returns ranked IDs with squared-L2 scores (lower = closer). A discovery aid: "
                          "confirm values with get_object.")
    async def semantic_search(
        corpus: Annotated[str, Field(description="v7, dwarf, gc, intz, z1 or all")],
        query: Annotated[str, Field(description="Natural-language description")],
        top_k: Annotated[int, Field(ge=1, le=50)] = 5,
    ) -> dict:
        return await run("semantic_search", corpus=corpus, query=query, top_k=top_k)

    return mcp


_STATUS = {
    "UNKNOWN_CORPUS": 400, "INVALID_ARGUMENT": 400, "UNKNOWN_FIELD": 400,
    "AMBIGUOUS_FIELD": 400, "AMBIGUOUS_OBJECT_ID": 409, "OBJECT_NOT_FOUND": 404,
    "SEMANTIC_UNAVAILABLE": 503, "SEMANTIC_LOADING": 503, "INDEX_INTEGRITY_FAILED": 503,
    "INTERNAL_ERROR": 500,
}


def build_app(service: CorpusService, host: str = "127.0.0.1", port: int = 8080) -> FastAPI:
    mcp = build_mcp(service, host, port)
    mcp_starlette = mcp.streamable_http_app()      # creates the session manager

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        if service.semantic is not None:
            service.semantic.start_model_load(background=True)
        async with mcp.session_manager.run():
            yield

    app = FastAPI(
        title="EPS Research Astro-RAG API",
        version=__version__,
        description=(
            "REST interface to the EPS Research Astro-RAG corpora. Every endpoint mirrors the "
            "MCP tool of the same name (MCP endpoint: `/mcp`) and returns the same envelope: "
            "`success`, `tool`, `data`, `human_text`, `warnings`, `error`."
        ),
        lifespan=lifespan,
    )
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST", "OPTIONS"],
                       allow_headers=["*"], expose_headers=["mcp-session-id"])

    # MCP Streamable HTTP route (/mcp) taken from FastMCP's own app.
    for route in mcp_starlette.routes:
        app.router.routes.append(route)

    def respond(env: dict) -> JSONResponse:
        code = 200 if env["success"] else _STATUS.get(env["error"]["code"], 400)
        return JSONResponse(env, status_code=code)

    # Documented as an enum in OpenAPI but validated by the service, so an unknown
    # key returns the standard UNKNOWN_CORPUS envelope rather than a bare 422.
    C = Query(..., description="Corpus key: " + ", ".join(CORPUS_KEYS), examples=["v7"],
              json_schema_extra={"enum": CORPUS_KEYS})

    @app.get("/api/list_corpora", tags=["Corpora"])
    def api_list_corpora():
        return respond(service.call("list_corpora"))

    @app.get("/api/get_corpus_schema", tags=["Corpora"])
    def api_get_corpus_schema(corpus: str = C):
        return respond(service.call("get_corpus_schema", corpus=corpus))

    @app.get("/api/list_objects", tags=["Objects"])
    def api_list_objects(
        corpus: str = C,
        survey: Optional[str] = None,
        quality_tier: Optional[int] = Query(None, description="Quality tier (alias: tier)"),
        tier: Optional[int] = Query(None, include_in_schema=False),
        limit: int = Query(100, ge=1, le=500),
        offset: Optional[int] = Query(None, ge=0),
        page: Optional[int] = Query(None, ge=1, description="1-based page; alternative to offset"),
    ):
        off = offset if offset is not None else ((page - 1) * limit if page else 0)
        return respond(service.call("list_objects", corpus=corpus, survey=survey,
                                    quality_tier=quality_tier if quality_tier is not None else tier,
                                    limit=limit, offset=off))

    @app.get("/api/get_object", tags=["Objects"])
    def api_get_object(corpus: str = C, object_id: str = Query(..., examples=["NGC0024"])):
        return respond(service.call("get_object", corpus=corpus, object_id=object_id))

    @app.get("/api/search_metadata", tags=["Search"])
    def api_search_metadata(corpus: str = C, field: str = Query(...), value: str = Query(...),
                            limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
        return respond(service.call("search_metadata", corpus=corpus, field=field, value=value,
                                    limit=limit, offset=offset))

    @app.get("/api/filter_objects", tags=["Search"])
    def api_filter_objects(
        corpus: str = C,
        field: str = Query(..., examples=["distance_mpc"]),
        min: Optional[float] = Query(None, description="Lower bound, inclusive (alias: min_val)"),
        max: Optional[float] = Query(None, description="Upper bound, inclusive (alias: max_val)"),
        min_val: Optional[float] = Query(None, include_in_schema=False),
        max_val: Optional[float] = Query(None, include_in_schema=False),
        omega_ready_only: bool = False,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ):
        return respond(service.call(
            "filter_objects", corpus=corpus, field=field,
            min_val=min if min is not None else min_val,
            max_val=max if max is not None else max_val,
            omega_ready_only=omega_ready_only, limit=limit, offset=offset))

    @app.get("/api/semantic_search", tags=["Search"])
    def api_semantic_search(corpus: str = Query(..., description="Corpus key or 'all'"),
                            query: str = Query(...), top_k: int = Query(5, ge=1, le=50)):
        return respond(service.call("semantic_search", corpus=corpus, query=query, top_k=top_k))

    @app.get("/health", tags=["Health"])
    def health():
        return service.health()

    @app.get("/", include_in_schema=False)
    def ui():
        return FileResponse(STATIC_DIR / "index.html")

    return app
