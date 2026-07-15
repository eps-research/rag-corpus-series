"""
EPS Research Astro-RAG Platform – True MCP Server v2.0
=======================================================
Rebuilt using the official Anthropic MCP Python SDK (FastMCP).
Implements true MCP protocol with SSE transport and JSON-RPC 2.0.

Endpoints (provided by FastMCP):
  GET  /sse          – SSE stream (MCP client connects here)
  POST /messages/    – JSON-RPC message handler
  GET  /mcp          – Streamable HTTP transport (alternative)
  GET  /             – Health check / server info

Five EPS Research corpora served:
  v7:    Unified HI Rotation Curve Corpus v7.0    (438 galaxies,   z~0)
  dwarf: Dwarf/Irregular HI Corpus v1.0           (129 galaxies,   z~0)
  gc:    Milky Way Globular Cluster Corpus v1.3.1  (174 clusters,   z=0)
  intz:  IntZ Kinematic Corpus v1.0               (1,292 galaxies, z=0.38-2.68)
  z1:    High-z Kinematic Corpus Z1               (31 galaxies,    z=4.26-5.68)

Author: Flynn, D.C. (EPS Research) 2026
SDK:    mcp >= 1.0.0 (pip install mcp)
v2.1:   CORPORA_CACHE rename, filter_objects isinstance patch,
        get_corpus_schema dynamic schema inference fallback
v2.2:   ID normalization layer (Layer 1-3):
        - normalize() collapses spaces/underscores/hyphens/case
        - build_norm_index() builds lookup table at startup
        - resolve_object_id() returns canonical ID + fuzzy suggestions on miss
        - search_metadata normalized comparison
        - browser UI hint strings via /hint route
"""

import json
import asyncio
import logging
import re
from contextlib import asynccontextmanager
from difflib import get_close_matches
from typing import Optional, Any

import httpx
from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── CORPUS REGISTRY ───────────────────────────────────────────────────────────

CORPORA = {
    "v7": {
        "name": "Unified HI Rotation Curve Corpus v7.0",
        "description": "438 galaxies from SPARC, THINGS, LITTLE THINGS, WALLABY DR2. HI 21cm kinematics. Local universe.",
        "n_objects": 438,
        "object_type": "galaxy",
        "redshift_range": "z ~ 0",
        "tracer": "HI 21cm",
        "zenodo_doi": "10.5281/zenodo.20695697",
        "jsonl_url": "https://zenodo.org/records/20695697/files/rotation_curve_corpus_v7.jsonl",
        "id_field": "galaxy",
        "status": "published",
    },
    "dwarf": {
        "name": "Dwarf/Irregular HI Corpus v1.0",
        "description": "129 dwarf and irregular galaxies. Local Volume HI 21cm kinematics.",
        "n_objects": 129,
        "object_type": "galaxy",
        "redshift_range": "z ~ 0",
        "tracer": "HI 21cm",
        "zenodo_doi": "10.5281/zenodo.20320362",
        "jsonl_url": "https://zenodo.org/records/20320362/files/dwarf_irregular_corpus_v1.jsonl",
        "id_field": "galaxy",
        "status": "published",
    },
    "gc": {
        "name": "Milky Way Globular Cluster Corpus v1.3.1",
        "description": "174 Milky Way globular clusters. Multi-survey kinematic and structural parameters.",
        "n_objects": 174,
        "object_type": "cluster",
        "redshift_range": "z = 0 (Milky Way)",
        "tracer": "Multi-survey",
        "zenodo_doi": "10.5281/zenodo.19907766",
        "jsonl_url": "https://zenodo.org/records/19907766/files/harris_gc_corpus_v1.3.1.jsonl",
        "id_field": "cluster_id",
        "status": "published",
    },
    "intz": {
        "name": "IntZ Kinematic Corpus v1.0",
        "description": "1,292 galaxies at z=0.38-2.68. Intermediate-redshift Hα/[OIII] kinematics.",
        "n_objects": 1292,
        "object_type": "galaxy",
        "redshift_range": "z = 0.38-2.68",
        "tracer": "Hα / [O III]",
        "zenodo_doi": "10.5281/zenodo.20453189",
        "jsonl_url": "https://zenodo.org/records/20453189/files/intz_corpus_v1b.jsonl",
        "id_field": "name",
        "status": "published",
    },
    "z1": {
        "name": "High-z Kinematic Corpus Z1",
        "description": "31 star-forming galaxies at z=4.26-5.68. ALMA [CII] 158μm morpho-kinematic corpus.",
        "n_objects": 31,
        "object_type": "galaxy",
        "redshift_range": "z = 4.26-5.68",
        "tracer": "ALMA [CII] 158μm",
        "zenodo_doi": "10.5281/zenodo.20369286",
        "jsonl_url": "https://zenodo.org/records/20369286/files/high_z_kinematic_corpus_Z1.jsonl",
        "id_field": "galaxy",
        "status": "published",
    },
}

VALID_CORPUS_KEYS = list(CORPORA.keys())

# In-memory cache
CORPORA_CACHE: dict[str, list[dict]] = {}


# ── LAYER 1: ID NORMALIZATION ─────────────────────────────────────────────────
# Collapses spaces / underscores / hyphens / case so that:
#   DDO 133, DDO_133, DDO-133, ddo133, ddO 133  →  all resolve to same object

# Norm index: { corpus_key: { normalized_key: canonical_id } }
_NORM_INDEX: dict[str, dict[str, str]] = {}


def _normalize(s: str) -> str:
    """Collapse spaces/underscores/hyphens, lowercase."""
    return re.sub(r"[\s_\-]+", "", s).lower()


def build_norm_index() -> None:
    """Build normalization lookup table from CORPORA_CACHE. Call after loading."""
    global _NORM_INDEX
    _NORM_INDEX = {}
    for corpus_key, records in CORPORA_CACHE.items():
        mapping: dict[str, str] = {}
        id_field = CORPORA[corpus_key]["id_field"]
        for r in records:
            # Get the canonical ID using all possible id fields
            canonical = (
                r.get(id_field)
                or r.get("galaxy")
                or r.get("cluster")
                or r.get("cluster_id")
                or r.get("name")
                or r.get("id")
            )
            if canonical:
                canonical = str(canonical)
                norm = _normalize(canonical)
                if norm not in mapping:
                    mapping[norm] = canonical
                # Also index nested identifiers (intz corpus)
                for v in r.get("identifiers", {}).values():
                    if v:
                        mapping[_normalize(str(v))] = canonical
        _NORM_INDEX[corpus_key] = mapping
    total = sum(len(m) for m in _NORM_INDEX.values())
    logger.info(f"build_norm_index: indexed {total} objects across {len(_NORM_INDEX)} corpora")


# ── LAYER 2: FUZZY FALLBACK ───────────────────────────────────────────────────

def resolve_object_id(corpus_key: str, raw_id: str, fuzzy_n: int = 5) -> tuple[Optional[str], list[str]]:
    """
    Resolve a user-supplied ID to a canonical stored ID.
    Returns (canonical_id, suggestions):
      - canonical_id is the match if found, else None
      - suggestions is a list of close matches when canonical_id is None
    """
    mapping = _NORM_INDEX.get(corpus_key, {})
    norm = _normalize(raw_id)

    # Layer 1: exact normalized match
    canonical = mapping.get(norm)
    if canonical:
        return canonical, []

    # Layer 2: fuzzy fallback
    hits = get_close_matches(norm, list(mapping.keys()), n=fuzzy_n, cutoff=0.6)
    suggestions = [mapping[h] for h in hits]
    return None, suggestions


def _norm_contains(haystack: str, needle_norm: str) -> bool:
    """True if normalized haystack contains normalized needle."""
    return needle_norm in _normalize(haystack)


# ── CORPUS LOADER ─────────────────────────────────────────────────────────────

async def fetch_corpus(corpus_key: str) -> list[dict]:
    meta = CORPORA[corpus_key]
    url  = meta["jsonl_url"]
    logger.info(f"Fetching corpus '{corpus_key}' from {url}")
    async with httpx.AsyncClient(timeout=90.0, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()
    records = [json.loads(line) for line in r.text.splitlines() if line.strip()]
    logger.info(f"Corpus '{corpus_key}' loaded: {len(records)} records")
    return records


async def get_cached(corpus_key: str) -> list[dict]:
    if corpus_key not in CORPORA:
        raise ValueError(f"Unknown corpus '{corpus_key}'. Valid keys: {VALID_CORPUS_KEYS}")
    if not CORPORA_CACHE.get(corpus_key):
        CORPORA_CACHE[corpus_key] = await fetch_corpus(corpus_key)
        build_norm_index()
    return CORPORA_CACHE[corpus_key]


@asynccontextmanager
async def lifespan(server: FastMCP):
    logger.info("Loading all corpora into cache...")
    for key in CORPORA:
        try:
            CORPORA_CACHE[key] = await fetch_corpus(key)
        except Exception as e:
            logger.warning(f"Could not load corpus '{key}' at startup: {e}. Will retry on first request.")
            CORPORA_CACHE[key] = []
    build_norm_index()   # ← build after all corpora loaded
    logger.info("All corpora loaded. Server ready.")
    yield
    CORPORA_CACHE.clear()


# ── FASTMCP SERVER ────────────────────────────────────────────────────────────

mcp = FastMCP(
    name="eps-astro-rag-mcp",
    instructions=(
        "EPS Research Astro-RAG Platform. Provides machine-readable access to five "
        "astrophysical kinematic corpora spanning z=0 to z~6. Use list_corpora first "
        "to discover available datasets, then use get_object, search_metadata, or "
        "filter_objects to retrieve scientific data. "
        "Object IDs are format-flexible: 'DDO 133', 'DDO_133', 'ddo133' all work."
    ),
    host="0.0.0.0",
    port=7860,
    lifespan=lifespan,
)


# ── TOOLS ─────────────────────────────────────────────────────────────────────


@mcp.tool(
    description=(
        "List all available EPS Research corpora with metadata including "
        "object count, redshift range, tracer, and Zenodo DOI. "
        "Call this first to discover which corpora are available."
    )
)
async def list_corpora() -> dict:
    corpora_list = [
        {
            "key":            k,
            "name":           v["name"],
            "description":    v["description"],
            "n_objects":      v["n_objects"],
            "object_type":    v["object_type"],
            "redshift_range": v["redshift_range"],
            "tracer":         v["tracer"],
            "zenodo_doi":     v["zenodo_doi"],
            "status":         v["status"],
            "cached_records": len(CORPORA_CACHE.get(k, [])),
        }
        for k, v in CORPORA.items()
    ]

    human_lines = [
        f"• {c['key']}: {c['n_objects']} {c['object_type']}s "
        f"({c['tracer']}, {c['redshift_range']}), DOI {c['zenodo_doi']}"
        for c in corpora_list
    ]
    human_text = (
        f"Your platform contains {len(corpora_list)} published corpora:\n" +
        "\n".join(human_lines)
    )

    return {
        "corpora": corpora_list,
        "human_text": human_text,
    }


@mcp.tool(
    description=(
        "List object identifiers in a corpus. Optionally filter by survey name "
        "or quality tier. Supports pagination with limit and offset. "
        "Corpus keys: v7, dwarf, gc, intz, z1."
    )
)
async def list_objects(
    corpus: str,
    survey: Optional[str] = None,
    quality_tier: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    if corpus not in CORPORA:
        return {"error": f"Unknown corpus '{corpus}'. Valid keys: {VALID_CORPUS_KEYS}"}
    if limit < 1 or limit > 500:
        return {"error": "limit must be between 1 and 500"}
    if offset < 0:
        return {"error": "offset must be >= 0"}

    records  = await get_cached(corpus)
    id_field = CORPORA[corpus]["id_field"]

    filtered = []
    for r in records:
        if survey and r.get("survey", "").lower() != survey.lower():
            continue
        if quality_tier is not None and r.get("quality_tier") != quality_tier:
            continue
        obj_id = r.get(id_field) or r.get("galaxy") or r.get("cluster") or r.get("name") or r.get("id")
        filtered.append(obj_id if obj_id else list(r.values())[0] if r else "unknown")

    page = filtered[offset: offset + limit]
    return {
        "corpus":      corpus,
        "n_total":     len(records),
        "n_filtered":  len(filtered),
        "n_returned":  len(page),
        "offset":      offset,
        "limit":       limit,
        "object_ids":  page,
    }


@mcp.tool(
    description=(
        "Retrieve the full record for a specific object from a corpus. "
        "Returns all kinematic parameters, rotation curve data, and provenance. "
        "Object ID format is flexible: 'DDO 133', 'DDO_133', 'DDO-133', 'ddo133' all work. "
        "Corpus keys: v7, dwarf, gc, intz, z1."
    )
)
async def get_object(
    corpus: str,
    object_id: str,
) -> dict:
    if corpus not in CORPORA:
        return {"error": f"Unknown corpus '{corpus}'. Valid keys: {VALID_CORPUS_KEYS}"}

    records = await get_cached(corpus)
    id_field = CORPORA[corpus]["id_field"]

    # ── Layer 1 & 2: normalize then fuzzy fallback ──────────────────────────
    canonical, suggestions = resolve_object_id(corpus, object_id)

    if canonical is None:
        # Layer 2 response: structured error with suggestions
        if suggestions:
            hint = f" Did you mean one of these? {suggestions}"
        else:
            hint = f" No close matches found. Use list_objects(corpus='{corpus}') to browse valid IDs."
        return {
            "error": f"Object '{object_id}' not found in corpus '{corpus}'.{hint}",
            "suggestions": suggestions,
        }

    # Find the record matching the canonical ID
    for r in records:
        for field in [id_field, "galaxy", "cluster", "cluster_id", "name", "id"]:
            val = r.get(field)
            if val and _normalize(str(val)) == _normalize(canonical):
                return {"corpus": corpus, "object_id": canonical, "record": r}
        # Check nested identifiers dict (intz corpus)
        for val in r.get("identifiers", {}).values():
            if val and _normalize(str(val)) == _normalize(canonical):
                return {"corpus": corpus, "object_id": canonical, "record": r}

    # Should not reach here if norm index is consistent
    return {"error": f"Object '{object_id}' not found in corpus '{corpus}'"}


@mcp.tool(
    description=(
        "Search a corpus by any metadata field and value. "
        "Returns all records where the field matches the value (case-insensitive, "
        "spaces/underscores/hyphens ignored). "
        "Supports pagination. Corpus keys: v7, dwarf, gc, intz, z1."
    )
)
async def search_metadata(
    corpus: str,
    field: str,
    value: str,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    if corpus not in CORPORA:
        return {"error": f"Unknown corpus '{corpus}'. Valid keys: {VALID_CORPUS_KEYS}"}
    if limit < 1 or limit > 500:
        return {"error": "limit must be between 1 and 500"}

    records  = await get_cached(corpus)
    id_field = CORPORA[corpus]["id_field"]

    # ── Normalize query once ────────────────────────────────────────────────
    target_norm = _normalize(value)

    matches = []
    for r in records:
        field_val = r.get(field)
        if field_val is not None and _normalize(str(field_val)) == target_norm:
            matches.append({
                "id":    r.get(id_field) or r.get("galaxy") or r.get("cluster") or r.get("name") or r.get("id") or str(list(r.values())[0]),
                "match": field_val,
            })

    page = matches[offset: offset + limit]
    return {
        "corpus":     corpus,
        "field":      field,
        "value":      value,
        "n_matched":  len(matches),
        "n_returned": len(page),
        "offset":     offset,
        "limit":      limit,
        "results":    page,
    }


@mcp.tool(
    description=(
        "Filter a corpus by numeric range on any field. "
        "Returns all records where the field value falls within [min_val, max_val]. "
        "Set omega_ready_only=true to restrict to omega-correction-ready objects (v7 and dwarf). "
        "Supports pagination. Corpus keys: v7, dwarf, gc, intz, z1."
    )
)
async def filter_objects(
    corpus: str,
    field: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    omega_ready_only: bool = False,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    if corpus not in CORPORA:
        return {"error": f"Unknown corpus '{corpus}'. Valid keys: {VALID_CORPUS_KEYS}"}
    if limit < 1 or limit > 500:
        return {"error": "limit must be between 1 and 500"}
    if min_val is not None and max_val is not None and min_val > max_val:
        return {"error": f"min_val ({min_val}) must be <= max_val ({max_val})"}

    records  = await get_cached(corpus)
    id_field = CORPORA[corpus]["id_field"]

    matches = []
    for r in records:
        if omega_ready_only and not r.get("omega_ready", False):
            continue
        val = r.get(field)
        if val is None:
            continue
        if isinstance(val, (int, float)):
            num = float(val)
        else:
            try:
                num = float(val)
            except (TypeError, ValueError):
                continue
        if min_val is not None and num < min_val:
            continue
        if max_val is not None and num > max_val:
            continue
        matches.append({
            "id":    r.get(id_field) or r.get("galaxy") or r.get("cluster") or r.get("name") or r.get("id") or str(list(r.values())[0]),
            "value": num,
        })

    page = matches[offset: offset + limit]
    return {
        "corpus":           corpus,
        "field":            field,
        "min_val":          min_val,
        "max_val":          max_val,
        "omega_ready_only": omega_ready_only,
        "n_matched":        len(matches),
        "n_returned":       len(page),
        "offset":           offset,
        "limit":            limit,
        "results":          page,
    }


@mcp.tool(
    description=(
        "Return the field schema for a corpus – all metadata field names and types, "
        "plus the data column definitions (units and descriptions) from the columns dict. "
        "Corpus keys: v7, dwarf, gc, intz, z1."
    )
)
async def get_corpus_schema(corpus: str) -> dict:
    if corpus not in CORPORA:
        return {"error": f"Unknown corpus '{corpus}'. Valid keys: {VALID_CORPUS_KEYS}"}

    records = await get_cached(corpus)
    if not records:
        return {"error": f"Corpus '{corpus}' is empty or failed to load"}

    first   = records[0]
    columns = first.get("columns")
    if not columns:
        data_array = first.get("data", [])
        if data_array and isinstance(data_array, list):
            columns = {k: {"unit": "unknown", "description": "inferred from data"}
                       for k in data_array[0].keys()}
        else:
            columns = {}
    meta_fields = {k: type(v).__name__ for k, v in first.items() if k not in ("data", "columns")}

    return {
        "corpus":          corpus,
        "name":            CORPORA[corpus]["name"],
        "n_records":       len(records),
        "id_field":        CORPORA[corpus]["id_field"],
        "object_type":     CORPORA[corpus]["object_type"],
        "metadata_fields": meta_fields,
        "data_columns":    columns,
        "zenodo_doi":      CORPORA[corpus]["zenodo_doi"],
    }


# ── CUSTOM ROUTES ─────────────────────────────────────────────────────────────

@mcp.custom_route("/", methods=["GET"])
async def health_route(request: Request) -> JSONResponse:
    return JSONResponse({
        "name":        "eps-astro-rag-mcp",
        "version":     "2.2.0",
        "sdk":         "mcp (FastMCP)",
        "transport":   "SSE + Streamable HTTP",
        "sse_url":     "/sse",
        "mcp_url":     "/mcp",
        "corpora":     {k: len(CORPORA_CACHE.get(k, [])) for k in CORPORA},
        "platform":    "https://github.com/eps-research/rag-corpus-series",
        "id_format":   "Flexible: 'DDO 133', 'DDO_133', 'DDO-133', 'ddo133' all accepted",
    })


# ── LAYER 3: browser UI hint endpoint ─────────────────────────────────────────

@mcp.custom_route("/hint", methods=["GET"])
async def hint_route(request: Request) -> JSONResponse:
    """
    Returns tooltip/placeholder strings for the browser UI input fields.
    Usage: GET /hint?corpus=v7
    """
    corpus = request.query_params.get("corpus")
    example = ""
    if corpus and corpus in _NORM_INDEX:
        ids = list(_NORM_INDEX[corpus].values())
        if ids:
            example = ids[0]
    return JSONResponse({
        "placeholder": f"e.g. DDO 133 · DDO_133 · NGC3198{' · ' + example if example else ''}",
        "tooltip":     "Spaces, underscores, hyphens, and case are all ignored. "
                       "DDO 133 · DDO_133 · DDO-133 · ddo133 all work.",
        "aria_label":  "Object ID – format is flexible",
    })


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
