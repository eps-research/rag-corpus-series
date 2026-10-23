# Changelog

## 2.4.0 — 2026-10 (response to Frontiers review, manuscript 2001275)

### Audit round 1 (Sol, 2026-10-23)
- **Stale v7 semantic index detected and enforced.** The v7 FAISS text was built
  from HI v7.0 (0 disagreements with v7.0; 438 of 438 with v7.3: WALLABY
  distances/geometry/velocities, LITTLE THINGS velocities and extents, superseded
  caveat wording). The server now checks index text against the served records
  at start-up and refuses semantic search on a stale corpus (`INDEX_STALE`).
  The builder regenerates v7 text from v7.3 and writes `faiss/index_manifest.json`;
  the rebuild itself needs the real model (RELEASING.md §2).
- **Dwarf v1.0 LITTLE THINGS model rows flagged.** 839 unmarked Oh et al. (2015)
  model rows in 25 of 26 curves (matching CORRECTIONS.md). Records now carry
  `data_quality` and a warning naming the observed curve in `v7`. No data changed.
- Explicit L2 normalisation of query and index embeddings; model revision
  recorded by the builder and pinned by the server.
- Release ZIP bundles CORRECTIONS.md and a software CITATION.cff; the builder
  fails on broken relative links and on stale indexes (`--allow-stale` produces
  a `-prerelease` archive).
- Full dependency lock (`requirements-full.lock.txt`, Python 3.10–3.13, Linux and
  Windows) and `launch.py --locked`; the Docker image installs from it.
- `tools/llm_acceptance.py` (recorded pass/fail runs with a real local model) and
  `tools/make_evidence.py` (evidence bundle for independent audits).
- `filter_objects(..., omega_ready_only=True)` warns when a corpus has no ω field.

Fixes to make local installation and reproduction work from a clean download.

### Fixed
- **Local mode now runs locally.** `launch.py` previously started a REST proxy
  that forwarded every request to the Hugging Face Space; no MCP endpoint ran on
  the user's machine, so local LLM clients had nothing to connect to. The server
  now runs in one local process serving `/mcp`, `/api/*`, `/docs`, `/health`
  and `/`, reading bundled corpus files; no network access is needed except the
  one-time embedding-model download.
- **`semantic_search` is in the published source.** The repository contained
  only the six-tool v2.2.0 server; the FAISS search code was not committed.
  It is now implemented in `astro_rag_mcp/semantic.py` and covered by tests.
- **Fresh installs failed** because `requirements.txt` allowed `mcp>=1.0.0`,
  which now resolves to mcp 2.x, where `mcp.server.fastmcp` no longer exists.
  Dependencies are bounded (`mcp>=1.26,<2`) and a lock file records the tested set.
- **REST parameters were silently dropped.** The wrapper sent `min`/`max`,
  `tier`, `page` while the server expected `min_val`/`max_val`,
  `quality_tier`, `offset`; filters were ignored. REST and MCP now call the same
  function; REST accepts both spellings.
- **Nested fields** (e.g. IntZ `redshift.z_spec`) can be filtered and searched,
  by dotted path or unique leaf name. Unknown fields return `UNKNOWN_FIELD` with
  suggestions instead of zero matches.
- **Ambiguous names** present in two surveys (e.g. `NGC3198`) return
  `AMBIGUOUS_OBJECT_ID` listing `SPARC:NGC3198` / `THINGS:NGC3198` instead of the
  first match. IDs from `semantic_search` resolve directly in `get_object`;
  zero-padding variants (`NGC 24` → `NGC0024`) resolve.
- `search_metadata` performs the documented substring match (was exact match).
- Two divergent copies of the REST wrapper (`/rest-wrapper` and
  `/mcp-server/rest-wrapper`) are removed; there is one implementation.
- `.gitignore` excluded all `*.json` files, so JSON files under the server
  directory that were not force-added never reached GitHub. Now excluded from that rule.
- Version strings, endpoint descriptions and transport statements are consistent
  (2.4.0; MCP at `/mcp`; Streamable HTTP; no SSE endpoint).

### Added
- MCP over **stdio** (`--transport stdio`) for Claude Desktop and similar clients.
- Start-up integrity gate: record counts, `data/SHA256SUMS`, FAISS structure and
  ID resolution, and an embedding self-test; status at `/health` and via
  `python -m astro_rag_mcp verify`.
- Provenance (corpus version, DOI, source SHA-256, server version) and
  correction notices in every response; explicit warning on records holding
  withdrawn ω values.
- `clients/local_llm_chat.py`: bridge for Ollama / LM Studio / llama.cpp / vLLM
  models via the OpenAI-compatible API; example client configurations.
- `semantic_search` over `corpus="all"`; `cosine_similarity` alongside the score.
- Reproducible release builder (`tools/build_release.py`): ZIP, `MANIFEST.txt`,
  `SHA256SUMS`, `RELEASE.json`; Dockerfile for the Space built from the same tree,
  which fails to build unless verification with the real model passes.
- Test suite: REST/MCP parity over in-process, socket and stdio transports;
  manuscript values; integrity tamper tests; error envelopes; LLM bridge.
- DNS-rebinding protection when bound to loopback.

### Changed
- Every tool returns the envelope `success`, `tool`, `data`, `human_text`,
  `warnings`, `error`. REST errors use HTTP status codes (400/404/409/503).
- `launch.py` runs in the terminal (no tkinter pop-ups or extra terminal
  windows), uses `.venv/`, and never terminates other processes.
- Corpus data are read from local files instead of being fetched from Zenodo at
  each start.

## 2.3.0 — 2026-07
Added FAISS semantic search to the hosted deployment (see 2.4.0: the source was not committed).

## 2.2.0 — 2026-07
ID normalisation layer; REST wrapper; cross-platform launcher.
