# EPS Research Astro-RAG MCP Server 2.4.0

A Model Context Protocol (MCP) server, REST API and browser interface for five
DOI-versioned astrophysical kinematic corpora (2,064 objects, z = 0 to 5.68),
with FAISS semantic search. MIT License.

[![mcp-server clean install: Linux, Windows, macOS](https://github.com/eps-research/rag-corpus-series/actions/workflows/mcp-server.yml/badge.svg)](https://github.com/eps-research/rag-corpus-series/actions/workflows/mcp-server.yml)

**Use it now:** <https://dflynn5656-astro-rag-mcp.hf.space> · MCP endpoint `…/mcp` · REST docs `…/docs`
**Run it locally:** `python launch.py` — see [INSTALL.md](INSTALL.md) (Windows, Ubuntu, macOS; Claude Desktop, LM Studio, Ollama)

## Corpora

| Key | Corpus | Objects | Range | Zenodo DOI |
|---|---|---|---|---|
| `v7` | Unified HI Rotation Curve Corpus v7.3 | 438 | z ≈ 0 | 10.5281/zenodo.23442703 |
| `dwarf` | Dwarf/Irregular HI Corpus v1.0 | 129 | z ≈ 0 | 10.5281/zenodo.20320362 |
| `gc` | Milky Way Globular Cluster Corpus v1.4.0 | 174 | Milky Way | 10.5281/zenodo.22077426 |
| `intz` | IntZ Kinematic Corpus v1.0 | 1,292 | z ≈ 0.38–2.68 | 10.5281/zenodo.21841382 |
| `z1` | High-z ALPINE Kinematic Corpus Z1 v3 | 31 | z = 4.26–5.68 | 10.5281/zenodo.21834678 |

Corrections that affect served data are attached to every affected response:
IntZ ω values are withdrawn and Z1 ω values recomputed (August 2026); GC v1.4.0
replaces the parser-defective v1.0–v1.3.3; HI v7.3 supersedes v7.0–v7.2; and
Dwarf v1.0 LITTLE THINGS curves contain unmarked model rows (flagged per record,
with a pointer to the observed curve in `v7`). Full history:
[CORRECTIONS.md](https://github.com/eps-research/rag-corpus-series/blob/main/CORRECTIONS.md)
(a copy is included in the release archive).

## Tools

The same seven operations are available as MCP tools and as `GET /api/<tool>`.
Both return the same envelope: `success`, `tool`, `data`, `human_text`,
`warnings`, `error` (with a stable `code`).

| Tool | Purpose | Main arguments |
|---|---|---|
| `list_corpora` | versions, counts, DOIs, checksums, correction notices | — |
| `list_objects` | object IDs, filterable, paginated | `corpus`, `survey`, `quality_tier`, `limit`, `offset` |
| `get_object` | full authoritative record with provenance | `corpus`, `object_id` |
| `search_metadata` | case-insensitive substring match on one field | `corpus`, `field`, `value` |
| `filter_objects` | inclusive numeric range on one field | `corpus`, `field`, `min_val`, `max_val`, `omega_ready_only` |
| `get_corpus_schema` | all fields (dotted paths), types, data columns | `corpus` |
| `semantic_search` | natural-language similarity (FAISS, MiniLM-L6-v2) | `corpus` (key or `all`), `query`, `top_k` |

REST also accepts `min`/`max` for `min_val`/`max_val`, `tier` for
`quality_tier`, and `page` for `offset`.

**Identifiers** are `SURVEY:name` (`SPARC:NGC0024`, `KROSS:C-HiZ_z1_111`,
`ALPINE:CG32`) or the cluster name for `gc` (`NGC 104`). Bare names and
spacing, case and zero-padding variants (`NGC 24`) resolve when unique; a name
present in two surveys (e.g. `NGC3198` in SPARC and THINGS) returns
`AMBIGUOUS_OBJECT_ID` with the qualified IDs rather than an arbitrary pick.

**Fields** may be top-level (`distance_mpc`), dotted (`redshift.z_spec`) or a
unique nested name (`z_spec`). An unknown field is an error with suggestions,
never a silent empty result.

**Semantic search** scores are squared L2 distances between unit-normalised
embeddings (lower = closer; `cosine_similarity = 1 − score/2`). Ranks are a
discovery aid; take values from `get_object`.

## Reliability checks at start-up

* corpus record counts (438, 129, 174, 1,292, 31; total 2,064) and unique IDs;
* `data/SHA256SUMS` in a release or container — any mismatch stops the server;
* each FAISS index: `IndexFlatL2`, d = 384, vectors = IDs = texts = records,
  every ID resolves to a record, finite unit vectors;
* index freshness: the text embedded for every record must agree with the
  record now served (distance, inclination, velocities, redshift, ω, caveats …),
  and, when `faiss/index_manifest.json` exists, the index must have been built
  from the loaded corpus file. A stale index is reported and semantic search on
  that corpus is refused; the other tools are unaffected;
* embedding self-test: one stored text per corpus is re-embedded and must
  reproduce its stored vector, so a different model cannot silently change
  rankings; query embeddings are L2-normalised explicitly.

Record-level data-quality flags: Dwarf v1.0 LITTLE THINGS records report
`data_quality` with the number of model rows and the `v7` record holding the
observed curve.

In release 2.4.0 all five indexes are current; the v7 index was rebuilt from
HI v7.3 ([RELEASING.md](RELEASING.md) describes the procedure).

`python -m astro_rag_mcp verify` prints the full report; `/health` serves it live.

## Layout

```
mcp-server/
├── launch.py              set up + run (Windows/Ubuntu)
├── astro_rag_mcp/         the server package
│   ├── corpus_service.py  the seven operations (shared by MCP and REST)
│   ├── semantic.py        FAISS loading, integrity checks, search
│   ├── index_text.py      index-text/record consistency rules (shared with the builder)
│   ├── server.py          MCP tools, REST routes, UI on one ASGI app
│   ├── cli.py             serve / verify / version
│   └── static/index.html  browser interface
├── clients/               Claude Desktop & LM Studio configs, local-LLM bridge
├── tests/                 pytest suite (parity, manuscript values, integrity)
├── tools/build_release.py builds the ZIP, MANIFEST.txt and SHA256SUMS
├── tools/llm_acceptance.py recorded pass/fail test of a real local LLM
├── tools/make_evidence.py  evidence bundle for independent audits
├── Dockerfile             Hugging Face Space image (built from the release)
└── requirements*.txt
```

The release ZIP additionally contains `data/` (the five corpus files, fifteen
FAISS files, `SHA256SUMS`), `RELEASE.json` and a top-level `SHA256SUMS`.

## Tests

```bash
python launch.py --check                       # or: pip install -r requirements-dev.txt && pytest
ASTRO_RAG_TEST_REAL_MODEL=1 pytest             # also run the real-model test (downloads MiniLM)
```

## Citation

Flynn, D. C. (2026). *EPS Research Astro-RAG MCP Server* (v2.4.0). Zenodo.
Machine-readable citation: [CITATION.cff](CITATION.cff).

Flynn, D. C. (2026). Astro-RAG MCP Server: AI-native, reproducible access to
cross-epoch astrophysical kinematic corpora. *Frontiers in Astronomy and Space
Sciences* (under review).
