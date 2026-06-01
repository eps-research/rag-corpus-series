# EPS Research Astro-RAG Platform
![Hits](https://hits.sh/github.com/eps-research/rag-corpus-series.svg)

**EPS Research | Laurel, MD | [eps-research.com](https://eps-research.com) | ORCID: [0000-0002-2768-6650](https://orcid.org/0000-0002-2768-6650)**

A unified platform of open astrophysics corpora, cross-epoch kinematic analysis tools, LLM-assisted scientific workflows, and educational resources — spanning Milky Way globular clusters to the epoch approaching cosmic reionization.

> ### 🚀 Open in Google Colab — runs live in your browser, no setup required
>
> | Notebook | Topic | Launch |
> |----------|-------|--------|
> **A unified open-science astrophysics platform combining five machine-readable corpora, 140 reproducible notebooks, and cross-epoch kinematic tools spanning z = 0 to z ~ 6.**

---

## 📄 Cite This Platform

If you use this platform, please cite:

```
Flynn, D.C. (2026). EPS Research Astro-RAG Platform. Zenodo: https://doi.org/10.5281/zenodo.20398430
```

---

> | **QuickStart** | Load all 5 corpora, reproduce omega sign reversal in 10 min | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eps-research/rag-corpus-series/blob/main/QuickStart.ipynb) |
> | **Three-Epoch Arc** | z=0 → z∼0.9 → z∼5 omega evolution ⭐ | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eps-research/rag-corpus-series/blob/main/examples/intz/intz_nb14_three_epoch_arc.ipynb) |
> | **Sign Reversal Test** | Statistical proof of z=0 vs z∼0.9 sign flip ⭐ | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eps-research/rag-corpus-series/blob/main/examples/intz/intz_nb15_sign_reversal.ipynb) |
> | **End-to-End Pipeline** | Full cross-epoch z=0→z∼0.9→z∼5 workflow ⭐ | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eps-research/rag-corpus-series/blob/main/examples/intz/intz_nb20_end_to_end_workflow.ipynb) |

> 💡 **Notebook Viewing:** If GitHub's notebook preview shows an error, 
> view any notebook via [nbviewer](https://nbviewer.org/github/eps-research/rag-corpus-series/tree/main/examples/) 
> or clone the repo and run locally with JupyterLab. All 140 notebooks 
> execute correctly (verified 140/140 pass rate).

🚀 **New here?** Start with [**QuickStart.ipynb** — Open in Colab](https://colab.research.google.com/github/eps-research/rag-corpus-series/blob/main/QuickStart.ipynb) — load all five corpora and reproduce the core omega sign reversal result in 10 minutes.

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
| [Unified HI Rotation Curve Corpus v7.0](./hi_corpus_v7/) | 438 galaxies | HI 21cm | [10.5281/zenodo.19563417](https://doi.org/10.5281/zenodo.19563417) | [2604.13489](https://arxiv.org/abs/2604.13489) |
| [Dwarf/Irregular HI Corpus v1.0](./dwarf_corpus_v1/) | 129 galaxies | HI 21cm | [10.5281/zenodo.20320362](https://doi.org/10.5281/zenodo.20320362) | [2605.22163](https://arxiv.org/abs/2605.22163) |
| [Milky Way Globular Cluster Corpus v1.3.1](./gc_corpus_v1/) | 174 clusters | Multi-survey | [10.5281/zenodo.19907766](https://doi.org/10.5281/zenodo.19907766) | [2605.03099](https://arxiv.org/abs/2605.03099) |

All three corpora share a common design philosophy: structured JSON + flat CSV + RAG-ready JSONL, with explicit quality tiers, verified kinematic parameters, and self-describing schemas for LLM ingestion.

---

## Silo 2 — z ~ 0.4–6 Data: Intermediate & High-z RAG Corpora

Two corpora spanning the intermediate and high-redshift universe, bridging local kinematic surveys to the epoch approaching cosmic reionization.

| Corpus | N | z range | Tracer | Zenodo | arXiv |
|--------|---|---------|--------|--------|-------|
| [IntZ Kinematic Corpus v1.0](./intz_corpus_v1/) | 1,292 galaxies | z = 0.38–2.68 | Hα / [O III] | [10.5281/zenodo.20453189](https://doi.org/10.5281/zenodo.20453189) | in prep |
| [High-z Kinematic Corpus Z1](./highz_corpus_z1/) | 31 galaxies | z = 4.26–5.68 | ALMA [CII] 158μm | [10.5281/zenodo.20369286](https://doi.org/10.5281/zenodo.20369286) | [2605.25339](https://arxiv.org/abs/2605.25339) |

**IntZ\_v1** combines two major IFU surveys into a unified schema:
- **KROSS** (Harrison et al. 2017): 586 galaxies, z = 0.60–1.04, Hα tracer
- **KMOS³D** (Wisnioski et al. 2019): 706 galaxies, z = 0.38–2.68, Hα/[O III] tracer

166 Tier-1 KROSS galaxies have spatially resolved, beam-smear-corrected kinematics with omega corrections applied. 1,126 Tier-2 galaxies have integrated kinematics only.

**Z1** provides ALPINE survey morpho-kinematic data with per-ring 3DBarolo rotation curves for 8 confirmed rotators and morpho-kinematic classifications for 23 additional galaxies at z~4–6.

**Cross-epoch omega result:**

| Corpus | Survey | N (T1) | Tracer | Median ω |
|--------|--------|--------|--------|----------|
| HI v7.0 | SPARC | 84 | HI 21cm | +7.06 rad/Gyr |
| IntZ v1.0 | KROSS | 166 | Hα | −9.087 rad/Gyr |
| Z1 v1.0 | ALPINE | 8 | [CII] | −13.05 rad/Gyr |

The sign difference across epochs is an empirical finding under the Flynn & Cannaliato (2025) omega prescription. These samples use different kinematic tracers (HI, Hα, [CII]) probing different physical radii; physical interpretation is deferred to Flynn & Cannaliato (in preparation).

---

## Silo 3 — Example Library

Executable Jupyter notebooks organized into six groups. All examples load directly from the corpus JSON/CSV files with no external preprocessing, using only Python 3, numpy, and matplotlib.

| Group | Examples | Description |
|-------|----------|-------------|
| [SPARC / HI Examples](./examples/hi/) [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eps-research/rag-corpus-series/blob/main/examples/hi/ex25_end_to_end_omega_workflow.ipynb) [![nbviewer](https://img.shields.io/badge/render-nbviewer-orange)](https://nbviewer.org/github/eps-research/rag-corpus-series/tree/main/examples/hi/) | 25 | Rotation curve plotting, baryonic decomposition, omega correction, WALLABY tier-2 analysis |
| [Dwarf / Irregular Examples](./examples/dwarfs/) [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eps-research/rag-corpus-series/blob/main/examples/dwarfs/dw25_end_to_end_dwarf_workflow.ipynb) [![nbviewer](https://img.shields.io/badge/render-nbviewer-orange)](https://nbviewer.org/github/eps-research/rag-corpus-series/tree/main/examples/dwarfs/) | 25 | Omega-ready galaxies, DDO154/DDO161 cross-analysis, LVHIS/VLA-ANGST comparisons |
| [Globular Cluster Examples](./examples/gc/) [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eps-research/rag-corpus-series/blob/main/examples/gc/gc25_end_to_end_gc_query.ipynb) [![nbviewer](https://img.shields.io/badge/render-nbviewer-orange)](https://nbviewer.org/github/eps-research/rag-corpus-series/tree/main/examples/gc/) | 25 | Proper motion queries, N-body mass modeling, APOGEE chemistry, multi-survey cross-matching |
| [IntZ Examples](./examples/intz/) [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eps-research/rag-corpus-series/blob/main/examples/intz/intz_nb20_end_to_end_workflow.ipynb) [![nbviewer](https://img.shields.io/badge/render-nbviewer-orange)](https://nbviewer.org/github/eps-research/rag-corpus-series/tree/main/examples/intz/) | 20 | KROSS/KMOS3D kinematics, omega distributions, cross-epoch comparisons, RAG queries |
| [High-z Examples](./examples/highz/) [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eps-research/rag-corpus-series/blob/main/examples/highz/hz_nb25_end_to_end_workflow.ipynb) [![nbviewer](https://img.shields.io/badge/render-nbviewer-orange)](https://nbviewer.org/github/eps-research/rag-corpus-series/tree/main/examples/highz/) | 25 | [CII] rotation curves, ALPINE population statistics, cross-corpus omega bridge |
| [**🔬 Paper 2 Validation Track**](./examples/paper2/) [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eps-research/rag-corpus-series/blob/main/examples/paper2/p2_nb5_cross_epoch_arc.ipynb) [![nbviewer](https://img.shields.io/badge/render-nbviewer-orange)](https://nbviewer.org/github/eps-research/rag-corpus-series/tree/main/examples/paper2/) | 6 | **Reproduce peer-reviewed results exactly** from Flynn (2026), Physics of the Dark Universe: Table 2, 93% success rate, omega vs MOND, outer gap diagnostic, three-epoch arc |
| [High-School Exploration Track](./examples/highschool/) [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eps-research/rag-corpus-series/blob/main/examples/highschool/hs_b_10_capstone.ipynb) [![nbviewer](https://img.shields.io/badge/render-nbviewer-orange)](https://nbviewer.org/github/eps-research/rag-corpus-series/tree/main/examples/highschool/) | 20 | Friendly introductory notebooks for students: what is a rotation curve? what is a galaxy? |

### 🚀 Quick Start

New here? The QuickStart notebook loads all five corpora and reproduces the core omega sign reversal result in under 10 minutes — no prior astrophysics knowledge required.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eps-research/rag-corpus-series/blob/main/QuickStart.ipynb)

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

Navigate to the relevant examples folder and open any `.ipynb` file. Each notebook is self-contained and loads data from the corpus files downloaded by `download_corpora.py`.

---

## Silo 4 — Papers & Preprints

The EPS Research publication arc underlying this platform.

| Paper | Journal | DOI / ID | Status |
|-------|---------|----------|--------|
| Flynn & Cannaliato (2025) — Omega correction introduced | Frontiers Astron Space Sci | [10.3389/fspas.2025.1680387](https://doi.org/10.3389/fspas.2025.1680387) | Published |
| Flynn (2026) — 84 SPARC baryonic validation | Seeking journal | [10.5281/zenodo.20132805](https://doi.org/10.5281/zenodo.20132805) | Preprint |
| Flynn (2026) — Unified HI Corpus v7.0 data descriptor | Astronomy & Computing | [arXiv:2604.13489](https://arxiv.org/abs/2604.13489) | Under review |
| Flynn (2026) — GC Corpus v1.3.1 data descriptor | PASP | [arXiv:2605.03099](https://arxiv.org/abs/2605.03099) | Submitted |
| Flynn (2026) — Dwarf/Irregular Corpus v1.0 data descriptor | PASP | [arXiv:2605.22163](https://arxiv.org/abs/2605.22163) | Submitted |
| Flynn (2026) — High-z Kinematic Corpus Z1 data descriptor | arXiv | [arXiv:2605.25339](https://arxiv.org/abs/2605.25339) | Published |
| Flynn (2026) — IntZ Kinematic Corpus v1.0 data descriptor | arXiv (astro-ph.IM) | [Zenodo:20453189](https://zenodo.org/records/20453189) — arXiv in prep | In preparation |
| Flynn (2026) — EPS Astro Extractor v1.0.0 (software) | Zenodo | [10.5281/zenodo.20486198](https://doi.org/10.5281/zenodo.20486198) | Published |
| Flynn (2026+) — Cross-epoch omega evolution (z=0 to z~6) | TBD | planned | Planned |
| Flynn (2026+) — RAMSES simulation Paper 3 | TBD | planned | Planned |
| Flynn (2026+) — Omega correction: implications for gravitational lensing | TBD | planned | Planned |

---

## Silo 5 — LLMs & Tools

Fine-tuned models and RAG utilities. Four-model team spanning laptop to research cluster. Full details in `llms/README.md`.

| Model | Size | Target | Hardware | Cloud Options | Role |
|-------|------|--------|----------|---------------|------|
| Flagship | ~72B | Researchers | Node1+Node2 (192GB) | Salad Cloud (coming soon) | Top-tier research grade |
| Desktop | ~31B | Advanced users | RTX 5090 (32GB) | Salad Cloud (coming soon) | Local inference |
| Laptop | ~7B | HS students | CPU/laptop GPU | Google Colab (coming soon) | In-school use |
| Vision Expert | ~72B | Researchers | Node1 (96GB) | Salad Cloud (coming soon) | Figure reading |

**Inference snippet:** Coming with model release. Fine-tuned adapters will be published to HuggingFace at `eps-research/` upon completion.

### RAG Tools

**🚀 Available Now**

| Tool | Description |
|------|-------------|
| EPS Astro Extractor | Streamlit app for extracting structured data from astronomical databases via local LLM — [Zenodo](https://doi.org/10.5281/zenodo.20486198) |

**🔧 Coming Soon**

| Tool | Description |
|------|-------------|
| FAISS indexes | Pre-built vector indexes for all five corpora |
| RAG query scripts | Python scripts for corpus retrieval |
| Schema validator | Cross-corpus schema validation utilities |

---

## Platform Statistics

| Item | Value |
|------|-------|
| Total corpora | 5 |
| Total galaxies / clusters | **2,064** |
| Redshift range | z = 0 to z ~ 2.7 (with z ~ 5 anchor) |
| Zenodo deposits | 7 (5 corpora + platform + extractor) |
| arXiv papers | 4 published + 2 in prep |
| Jupyter notebooks | 140 (120 research + 20 IntZ) |
| License | CC BY 4.0 |

---

## Mission

EPS Research is an independent research organization conducting self-directed, cross-domain astrophysics research without institutional affiliation or external funding. This platform reflects three core commitments:

**Open corpora** — All data products are released under CC BY 4.0 at Zenodo, with full provenance documentation, primary-source verification, and machine-readable schemas.

**Cross-epoch kinematic analysis** — The five corpora together span z = 0 to z ~ 2.7 (with a z ~ 5 anchor), enabling the first unified kinematic dataset from local HI rotation curves through intermediate-redshift Hα surveys to ALMA [CII] observations approaching the epoch of reionization. The omega kinematic correction, introduced by Flynn & Cannaliato (2025), provides the unifying scientific framework across all five corpora and cosmic epochs.

**Educational outreach** — The High-School Exploration Track makes the platform accessible to students, with friendly notebooks that require no prior astrophysics background.

---

## Future Expansion

**Planned RAG Corpora:**

| Corpus | Description | Timeline |
|--------|-------------|----------|
| High-z Corpus Z2 | REBELS + CRISTAL [CII] data at z ~ 6–8 | 2027 |
| GC Corpus v2.0 | Extended globular cluster parameters | 2027 |
| Unified HI v8.0 | Updated SPARC + WALLABY DR3 | 2027 |

**Planned Research Papers:**

| Paper | Description | Timeline |
|-------|-------------|----------|
| Cross-epoch omega evolution | z = 0 to z ~ 6 kinematic analysis | 2026 |
| RAMSES Paper 3 | z = 6 → z = 0 omega evolution simulations | August 2026 |
| Gravitational lensing | Omega spin as a new source of spacetime distortion | 2027 |

**Planned LLM Adapters:**

| Model | Description | Timeline |
|-------|-------------|----------|
| Flagship 72B | Qwen2.5-72B fine-tuned on all five EPS corpora | 2026 |
| Desktop 31B | Gemma 4 31B fine-tuned on all five EPS corpora | 2026 |
| Laptop 7B | Qwen2.5-7B fine-tuned, optimized for students | 2026 |
| Vision Expert 72B | Qwen2-VL-72B for scientific figure reading | 2027 |

---

## Citation

If you use any EPS Research corpus, please cite the relevant Zenodo record and the associated paper. The full citation list is in each corpus subdirectory README.

For the omega correction framework:

```
Flynn, D.C. & Cannaliato, J. (2025). A new empirical fit to galaxy rotation curves.
Frontiers in Astronomy and Space Sciences, 12.
DOI: 10.3389/fspas.2025.1680387
```

---

## Contact

**Platform DOI:** 10.5281/zenodo.20398430

David C. Flynn | EPS Research  
📧 davidflynn@eps-research.com  
🌐 eps-research.com  
🔬 ORCID: 0000-0002-2768-6650

*EPS Research — Independent astrophysics research, open science, educational outreach.*
