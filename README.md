# EPS Research Astro-RAG Platform
![Hits](https://hits.sh/github.com/eps-research/rag-corpus-series.svg)

[![Zenodo Platform](https://img.shields.io/badge/Zenodo-Platform-blue)](https://doi.org/10.5281/zenodo.20398430)
[![Zenodo MCP Server](https://img.shields.io/badge/Zenodo-MCP_Server-blue)](https://doi.org/10.5281/zenodo.21154451)
[![Zenodo Astro Extractor](https://img.shields.io/badge/Zenodo-Astro_Extractor-blue)](https://doi.org/10.5281/zenodo.20534420)
[![Zenodo FAISS Indexes](https://img.shields.io/badge/Zenodo-FAISS_Indexes-blue)](https://doi.org/10.5281/zenodo.21147895)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)
[![arXiv](https://img.shields.io/badge/arXiv-2604.13489-b31b1b)](https://arxiv.org/abs/2604.13489)

**EPS Research** | Laurel, MD | [eps-research.com](https://eps-research.com) | ORCID: [0000-0002-2768-6650](https://orcid.org/0000-0002-2768-6650)

A unified platform of open astrophysics corpora, cross-epoch kinematic analysis tools, LLM-assisted scientific workflows, and educational resources — spanning Milky Way globular clusters to the epoch approaching cosmic reionization.

> **✅ Correction Complete (August 2026):** A formula-implementation discrepancy and data-provenance issue in the cross-epoch omega values have been corrected. Z1 omega recomputed under canonical Eq.6 — all 8 tier-1 rotators positive (median +13.776 rad/Gyr). IntZ omega nulled pending independent boundary-ring data. The z=0 SPARC result is peer-reviewed and unaffected. See [CORRECTIONS.md](CORRECTIONS.md) for full details.

---

## 🚀 Launch the Astro-RAG Query Interface

➡ **[Open in Browser](https://dflynn5656-astro-rag-mcp.hf.space)** — no install required

Click the link above — the interface loads instantly in your browser via HuggingFace Spaces.

| Interface | URL | Use for |
|-----------|-----|---------|
| Query UI | [dflynn5656-astro-rag-mcp.hf.space](https://dflynn5656-astro-rag-mcp.hf.space) | Daily research — human-readable results, download options |
| REST API / Swagger | [.../docs](https://dflynn5656-astro-rag-mcp.hf.space/docs) | Developer integration — full OpenAPI explorer |
| MCP endpoint | `https://dflynn5656-astro-rag-mcp.hf.space/` | AI assistant integration (Claude, Copilot, etc.) |
| Semantic search | [.../api/semantic_search](https://dflynn5656-astro-rag-mcp.hf.space/api/semantic_search) | Natural-language similarity search via FAISS |

Corpus keys: `v7` · `dwarf` · `gc` · `intz` · `z1`

---

## 💻 Local Installation (offline / high-performance use)

For local deployment on Windows 11 or Ubuntu:

Download: [astro-rag-mcp-server-v2.3.0.zip from Zenodo](https://doi.org/10.5281/zenodo.21154451) · MIT License

```bash
# Windows
python launch.py

# Ubuntu / Linux
python3 launch.py
```

The launcher installs all dependencies automatically (first run ~60 seconds), then opens your browser to `http://localhost:8080`.

---

## 🔭 EPS Astro Extractor — Local Database Mining Tool

A portable Streamlit app that crawls any publicly accessible astronomical database URL, feeds the content to a local LLM via LM Studio, and returns structured JSON — parameters, table data, and export options. No API key. No cloud inference. Runs entirely on your own hardware.

Download v1.1.0: [10.5281/zenodo.20534420](https://doi.org/10.5281/zenodo.20534420)

**Windows — one-click launch**
1. Install Python 3.10+ and LM Studio
2. Download and unzip the Zenodo deposit
3. Load a model in LM Studio and start the local server (default port 1234)
4. Double-click `run_extractor.bat` — browser opens automatically

**Linux / macOS**
```bash
bash run.sh
```

Suitable for high school students — no command line required on Windows, no API key, no cost.

---

## MCP Server

All five corpora are available via a persistent Model Context Protocol (MCP) server — a true LLM-native data API implementing the Anthropic MCP specification with SSE and Streamable HTTP transports.

**Endpoint:** `https://dflynn5656-astro-rag-mcp.hf.space/`

| Tool | Description |
|------|-------------|
| `list_corpora` | List all five corpora with metadata, record counts, and Zenodo DOIs |
| `list_objects` | List object IDs with optional survey/tier filter and pagination |
| `get_object` | Retrieve full record for any galaxy or cluster by name |
| `search_metadata` | Search any metadata field by value (case-insensitive) |
| `filter_objects` | Filter by numeric range on any field; supports `omega_ready_only` flag |
| `get_corpus_schema` | Return field schema and column definitions for any corpus |
| `semantic_search` | Natural-language similarity search across any corpus using FAISS vector indexes |

---

## Platform Architecture

```
EPS Research Astro-RAG Platform
│
├── Silo 1 — z = 0 Data         Local Universe RAG Corpora                   ✓ Stage 1
├── Silo 2 — z ~ 0.4–6 Data     Intermediate & High-z RAG Corpora            ✓ Stage 1
├── Silo 3 — Example Library    Notebooks + High-School Track                ✓ Stage 1
├── Silo 4 — Papers & Preprints Published Research Arc                       ✓ Stage 1
└── Silo 5 — LLMs & Tools       Fine-tuned Models + RAG Utilities            ○ Stage 2
```

---

## Silo 1 — z = 0 Data: Local Universe RAG Corpora

Three unified, machine-readable corpora of the local universe, designed for both traditional kinematic analysis and LLM retrieval-augmented generation (RAG) pipelines.

| Corpus | N | Tracer | Zenodo | arXiv |
|--------|---|--------|--------|-------|
| Unified HI Rotation Curve Corpus v7.0 | 438 galaxies | HI 21cm | [10.5281/zenodo.19563417](https://doi.org/10.5281/zenodo.19563417) | [2604.13489](https://arxiv.org/abs/2604.13489) |
| Dwarf/Irregular HI Corpus v1.0 | 129 galaxies | HI 21cm | [10.5281/zenodo.20320362](https://doi.org/10.5281/zenodo.20320362) | [2605.22163](https://arxiv.org/abs/2605.22163) |
| Milky Way Globular Cluster Corpus v1.3.2 | 174 clusters | Multi-survey | [10.5281/zenodo.19907766](https://doi.org/10.5281/zenodo.19907766) | [2605.03099](https://arxiv.org/abs/2605.03099) |

All three corpora share a common design philosophy: structured JSON + flat CSV + RAG-ready JSONL, with explicit quality tiers, verified kinematic parameters, and self-describing schemas for LLM ingestion.

---

## Silo 2 — z ~ 0.4–6 Data: Intermediate & High-z RAG Corpora

Two corpora spanning the intermediate and high-redshift universe, bridging local kinematic surveys to the epoch approaching cosmic reionization.

| Corpus | N | z range | Tracer | Zenodo | arXiv |
|--------|---|---------|--------|--------|-------|
| IntZ Kinematic Corpus v1.0 | 1,292 galaxies | z = 0.38–2.68 | Hα / [O III] | [10.5281/zenodo.20453189](https://doi.org/10.5281/zenodo.20453189) | in prep |
| High-z Kinematic Corpus Z1 | 31 galaxies | z = 4.26–5.68 | ALMA [CII] 158μm | [10.5281/zenodo.20369286](https://doi.org/10.5281/zenodo.20369286) | [2605.25339](https://arxiv.org/abs/2605.25339) |

IntZ\_v1 combines two major IFU surveys into a unified schema:
- **KROSS** (Harrison et al. 2017): 586 galaxies, z = 0.60–1.04, Hα tracer
- **KMOS³D** (Wisnioski et al. 2019): 706 galaxies, z = 0.38–2.68, Hα/[O III] tracer

Z1 provides ALPINE survey morpho-kinematic data with per-ring 3DBarolo rotation curves for 8 confirmed rotators and morpho-kinematic classifications for 23 additional galaxies at z~4–6.

**Omega status (corrected August 2026):**

| Corpus | Survey | N (T1) | Tracer | ω status |
|--------|--------|--------|--------|----------|
| HI v7.0 | SPARC | 175 | HI 21cm | ω = +7.13 km/s/kpc (retained) |
| IntZ v1.0 | KROSS | 166 | Hα | ω withdrawn — template-derived; no boundary-ring data |
| Z1 v1.0 | ALPINE | 8 | [CII] | ω recomputation in progress under canonical Eq. 6 |

The z=0 omega result under the Flynn & Cannaliato (2025) prescription is confirmed. The previously reported cross-epoch sign reversal has been withdrawn due to a formula-implementation discrepancy and a data-provenance issue in the high-z values. See [CORRECTIONS.md](CORRECTIONS.md) for details.

---

## Silo 3 — Example Library

Executable Jupyter notebooks organized into six groups. All examples load directly from the corpus JSON/CSV files with no external preprocessing, using only Python 3, numpy, and matplotlib.

| Group | Examples | Description | Launch |
|-------|----------|-------------|--------|
| SPARC / HI Examples | 25 | Rotation curve plotting, baryonic decomposition, omega correction, WALLABY tier-2 analysis | [Colab](https://colab.research.google.com/) |
| Dwarf / Irregular Examples | 25 | Omega-ready galaxies, DDO154/DDO161 cross-analysis, LVHIS/VLA-ANGST comparisons | [Colab](https://colab.research.google.com/) |
| Globular Cluster Examples | 25 | Proper motion queries, N-body mass modeling, APOGEE chemistry, multi-survey cross-matching | [Colab](https://colab.research.google.com/) |
| IntZ Examples | 20 | KROSS/KMOS3D kinematics, survey parameters, RAG queries (omega notebooks suspended — see [CORRECTIONS.md](CORRECTIONS.md)) | [Colab](https://colab.research.google.com/) |
| High-z Examples | 25 | [CII] rotation curves, ALPINE population statistics, kinematic analysis | [Colab](https://colab.research.google.com/) |
| 🔬 84-Galaxy Baryonic Validation | 6 | Reproduce peer-reviewed baryonic validation results across 84 SPARC galaxies (Flynn 2026) | [Colab](https://colab.research.google.com/) |
| High-School Exploration Track | 20 | Friendly introductory notebooks for students | [Colab](https://colab.research.google.com/) |

### 🚀 Quick Start

New here? The QuickStart notebook loads all five corpora and demonstrates the platform's query and analysis capabilities in under 10 minutes — no prior astrophysics knowledge required.

[Open In Colab](https://colab.research.google.com/)

### Running the Examples

```bash
# Clone the repo
git clone https://github.com/eps-research/rag-corpus-series
cd rag-corpus-series

# Install dependencies
pip install -r requirements.txt

# Download all 5 corpora from Zenodo
python download_corpora.py

# Launch JupyterLab
jupyter lab
```

---

## Silo 4 — Papers & Preprints

| Paper | Journal | DOI / ID | Status |
|-------|---------|----------|--------|
| Flynn & Cannaliato (2025) — Omega correction introduced | Frontiers Astron Space Sci | [10.3389/fspas.2025.1680387](https://doi.org/10.3389/fspas.2025.1680387) | Published |
| Flynn (2026) — 84 SPARC baryonic validation | Seeking journal | [10.5281/zenodo.20132805](https://doi.org/10.5281/zenodo.20132805) | Preprint |
| Flynn (2026) — Unified HI Corpus v7.0 data descriptor | Astronomy & Computing | [arXiv:2604.13489](https://arxiv.org/abs/2604.13489) | Under review |
| Flynn (2026) — GC Corpus v1.3.1 data descriptor | PASP | [arXiv:2605.03099](https://arxiv.org/abs/2605.03099) | Submitted |
| Flynn (2026) — Dwarf/Irregular Corpus v1.0 data descriptor | PASP | [arXiv:2605.22163](https://arxiv.org/abs/2605.22163) | Submitted |
| Flynn (2026) — High-z Kinematic Corpus Z1 data descriptor | arXiv | [arXiv:2605.25339](https://arxiv.org/abs/2605.25339) | Preprint |
| Flynn (2026) — IntZ Kinematic Corpus v1.0 data descriptor | arXiv (astro-ph.IM) | [Zenodo:20453189](https://doi.org/10.5281/zenodo.20453189) | Preprint |
| Flynn (2026) — EPS Astro Extractor v1.1.0 (software) | Zenodo | [10.5281/zenodo.20534420](https://doi.org/10.5281/zenodo.20534420) | Published |
| Flynn (2026) — EPS Astro-RAG MCP Server v2.3.0 (software) | Zenodo | [10.5281/zenodo.21154451](https://doi.org/10.5281/zenodo.21154451) | Published |
| Flynn (2026) — FAISS Semantic Search Indexes v1.0 (software) | Zenodo | [10.5281/zenodo.21147895](https://doi.org/10.5281/zenodo.21147895) | Published |
| Flynn (2026) — Cross-epoch omega correction note | Zenodo | [10.5281/zenodo.21383809](https://doi.org/10.5281/zenodo.21383809) | **Corrected Aug 2026** |
| Flynn (2026+) — Cross-epoch omega analysis (revised) | TBD | pending | Pending corrected data |
| Flynn (2026+) — RAMSES simulation Paper 3 | TBD | planned | Planned |
| Flynn (2026+) — Omega correction: implications for gravitational lensing | TBD | planned | Planned |

---

## Silo 5 — LLMs & Tools

The MCP server (Silo 5 Stage 1) makes all five corpora queryable by any LLM today — Claude, Copilot, or any MCP-compatible assistant — with no fine-tuning required. Domain-specific fine-tuned models trained on the EPS corpora are a planned Stage 2 direction.

### RAG Tools

🚀 **Available Now**

| Tool | Description |
|------|-------------|
| EPS Astro-RAG MCP Server v2.3.0 | Cross-platform launcher + REST wrapper for all 5 corpora + semantic search — [Zenodo](https://doi.org/10.5281/zenodo.21154451) |
| EPS Astro Extractor v1.1.0 | Streamlit app for extracting structured data from astronomical databases via local LLM — Windows .bat launcher included — [Zenodo](https://doi.org/10.5281/zenodo.20534420) |
| FAISS Semantic Search Indexes v1.0 | Pre-built vector indexes for all 5 corpora (2,064 objects) using all-MiniLM-L6-v2 — enables natural-language similarity search — [Zenodo](https://doi.org/10.5281/zenodo.21147895) |

---

## Platform Statistics

| Item | Value |
|------|-------|
| Total corpora | 5 |
| Total galaxies / clusters | 2,064 |
| Redshift range | z = 0 to z ~ 2.7 (with z ~ 5 anchor) |
| Zenodo deposits | 10 (5 corpora + platform + extractor v1.1.0 + MCP server + extractor v1.0.0 + FAISS indexes) |
| arXiv papers | 4 published + 2 in prep |
| Jupyter notebooks | 150 |
| License | CC BY 4.0 |

---

## Mission

EPS Research is an independent research organization conducting self-directed, cross-domain astrophysics research without institutional affiliation or external funding. This platform reflects three core commitments:

**Open corpora** — All data products are released under CC BY 4.0 at Zenodo, with full provenance documentation, primary-source verification, and machine-readable schemas.

**Cross-epoch kinematic analysis** — The five corpora together span z = 0 to z ~ 2.7 (with a z ~ 5 anchor), enabling a unified kinematic dataset from local HI rotation curves through intermediate-redshift Hα surveys to ALMA [CII] observations approaching the epoch of reionization.

**Educational outreach** — The High-School Exploration Track makes the platform accessible to students, with friendly notebooks that require no prior astrophysics background.

---

## Citation

For the omega correction framework:

```bibtex
@article{flynn_cannaliato_2025,
  author  = {Flynn, D.C. and Cannaliato, J.},
  title   = {A new empirical fit to galaxy rotation curves},
  journal = {Frontiers in Astronomy and Space Sciences},
  volume  = {12},
  year    = {2025},
  doi     = {10.3389/fspas.2025.1680387}
}
```

---

## Contact

**Platform DOI:** [10.5281/zenodo.20398430](https://doi.org/10.5281/zenodo.20398430)

**David C. Flynn** | EPS Research  
📧 davidflynn@eps-research.com  
🌐 [eps-research.com](https://eps-research.com)  
🔬 ORCID: [0000-0002-2768-6650](https://orcid.org/0000-0002-2768-6650)

---

*EPS Research — Independent astrophysics research, open science, educational outreach.*
