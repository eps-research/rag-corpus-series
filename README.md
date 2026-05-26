# EPS Research Astro-RAG Platform

**EPS Research** | Laurel, MD | [eps-research.com](https://eps-research.com) | ORCID: [0000-0002-2768-6650](https://orcid.org/0000-0002-2768-6650)

A unified platform of open astrophysics corpora, cross-epoch kinematic analysis tools, LLM-assisted scientific workflows, and educational resources — spanning Milky Way globular clusters to the epoch approaching cosmic reionization.

---

## Platform Architecture

```
EPS Research Astro-RAG Platform
│
├── Silo 1 — z = 0 Data         Local Universe RAG Corpora
├── Silo 2 — z ~ 6 Data         Early Universe RAG Corpus
├── Silo 3 — Example Library    Notebooks + High-School Track
├── Silo 4 — Papers & Preprints Published Research Arc
└── Silo 5 — LLMs & Tools       Fine-tuned Models + RAG Utilities
```

---

## Silo 1 — z = 0 Data: Local Universe RAG Corpora

Three unified, machine-readable corpora of the local universe, designed for both traditional kinematic analysis and LLM retrieval-augmented generation (RAG) pipelines.

| Corpus | N | Tracer | Zenodo | arXiv |
|--------|---|--------|--------|-------|
| [Unified HI Rotation Curve Corpus v7.0](./hi_corpus_v7/) | 438 galaxies | HI 21cm | [10.5281/zenodo.19563417](https://doi.org/10.5281/zenodo.19563417) | [2604.13489](https://arxiv.org/abs/2604.13489) |
| [Dwarf/Irregular HI Corpus v1.0](./dwarf_corpus_v1/) | 129 galaxies | HI 21cm | [10.5281/zenodo.20320362](https://doi.org/10.5281/zenodo.20320362) | [2605.22163](https://arxiv.org/abs/2605.22163) |
| [Milky Way Globular Cluster Corpus v1.3.1](./gc_corpus_v1/) | 174 clusters | Multi-survey | [10.5281/zenodo.19907765](https://doi.org/10.5281/zenodo.19907765) | [2605.03099](https://arxiv.org/abs/2605.03099) |

All three corpora share a common design philosophy: structured JSON + flat CSV + RAG-ready JSONL + per-object ZIP, with explicit quality tiers, verified kinematic parameters, and self-describing schemas for LLM ingestion.

---

## Silo 2 — z ~ 6 Data: Early Universe RAG Corpus

The high-redshift anchor of the platform, bridging local kinematic surveys to the epoch approaching cosmic reionization.

| Corpus | N | Tracer | Zenodo | arXiv |
|--------|---|--------|--------|-------|
| [High-z Kinematic Corpus Z1](./highz_corpus_z1/) | 31 galaxies, z = 4.26–5.68 | ALMA [CII] 158μm | [10.5281/zenodo.20369285](https://doi.org/10.5281/zenodo.20369285) | [2605.25339](https://arxiv.org/abs/2605.25339) |

Z1 is the fourth and most recent corpus in the series, providing ALPINE survey morpho-kinematic data with per-ring 3DBarolo rotation curves for 8 confirmed rotators and morpho-kinematic classifications for 23 additional galaxies.

**Cross-epoch result:** All 8 tier-1 Z1 rotators show negative omega values (median −13.05 rad/Gyr) under the Flynn & Cannaliato (2025) kinematic correction, contrasting with positive values at z = 0 (SPARC mean +7.06 rad/Gyr). This sign reversal across ~9 Gyr motivates future RAMSES cosmological simulations from z = 6 initial conditions.

---

## Silo 3 — Example Library

Executable Jupyter notebooks organized into five groups. All examples load directly from the corpus JSON/CSV files with no external preprocessing, using only Python 3, numpy, and matplotlib.

| Group | Examples | Description |
|-------|----------|-------------|
| [SPARC / HI Examples](./examples/hi/) | ~25 | Rotation curve plotting, baryonic decomposition, omega correction, WALLABY tier-2 analysis |
| [Dwarf / Irregular Examples](./examples/dwarfs/) | ~25 | Omega-ready galaxies, DDO154/DDO161 cross-analysis, LVHIS/VLA-ANGST comparisons |
| [Globular Cluster Examples](./examples/gc/) | ~25 | Proper motion queries, N-body mass modeling, APOGEE chemistry, multi-survey cross-matching |
| [High-z Examples](./examples/highz/) | 25 | [CII] rotation curves, ALPINE population statistics, cross-corpus omega bridge |
| [High-School Exploration Track](./examples/highschool/) | 20 | Friendly introductory notebooks for students: what is a rotation curve? what is a galaxy? |

### Running the Examples

```bash
# Clone the repo
git clone https://github.com/eps-research/rag-corpus-series
cd rag-corpus-series

# Install dependencies
pip install numpy matplotlib jupyter

# Launch JupyterLab
jupyter lab
```

Navigate to the relevant examples folder and open any `.ipynb` file. Each notebook is self-contained and loads data from the Zenodo corpus files. Download the corpus JSON from the relevant Zenodo record and place it in the same directory as the notebook.

---

## Silo 4 — Papers & Preprints

The EPS Research publication arc underlying this platform.

| Paper | Journal | DOI / ID | Status |
|-------|---------|----------|--------|
| Flynn & Cannaliato (2025) — Omega correction introduced | Frontiers Astron Space Sci | [10.3389/fspas.2025.1680387](https://doi.org/10.3389/fspas.2025.1680387) | Published |
| Flynn (2026) — 84 SPARC baryonic validation | Seeking journal | [10.5281/zenodo.20132805](https://doi.org/10.5281/zenodo.20132805) | Letter to Open J. Astrophysics |
| Flynn (2026) — Unified HI Corpus v7.0 data descriptor | Astronomy & Computing | [arXiv:2604.13489](https://arxiv.org/abs/2604.13489) | Under review |
| Flynn (2026) — GC Corpus v1.3.1 data descriptor | PASP | [arXiv:2605.03099](https://arxiv.org/abs/2605.03099) | Submitted |
| Flynn (2026) — Dwarf/Irregular Corpus v1.0 data descriptor | PASP | [arXiv:2605.22163](https://arxiv.org/abs/2605.22163) | Submitted |
| Flynn (2026) — High-z Kinematic Corpus Z1 data descriptor | arXiv | [arXiv:2605.25339](https://arxiv.org/abs/2605.25339) | Published |
| Flynn (2026+) — Cross-epoch omega evolution (z=0 to z~6) | TBD | planned | Planned |
| Flynn (2026+) — RAMSES simulation Paper 3 | TBD | planned | Planned |
| Flynn (2026+) — Omega correction and gravitational lensing: spin as a new source of spacetime distortion | TBD | planned | Planned |

---

## Silo 5 — LLMs & Tools

Fine-tuned models and RAG utilities. Four-model team spanning laptop to research cluster.
Full details in [llms/README.md](./llms/).

| Model | Size | Target | Hardware | Cloud | Role |
|-------|------|--------|----------|-------|------|
| Flagship | ~72B | Researchers | Node1+Node2 (192GB) | Salad Cloud | Top-tier research grade |
| Desktop | ~31B | Advanced users | RTX 5090 (32GB) | Colab Pro | Local inference |
| Laptop | ~7B | HS students | CPU/laptop GPU | [Colab Free](./examples/highschool/) | In-school use |
| Vision Expert | ~72B | Researchers | Node1 (96GB) | Salad Cloud | Figure reading |

**Quick inference snippet:**

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base = AutoModelForCausalLM.from_pretrained("google/gemma-4-31b")
model = PeftModel.from_pretrained(base, "eps-research/gemma4-astro-rag")
tokenizer = AutoTokenizer.from_pretrained("google/gemma-4-31b")

query = "Plot the rotation curve of DDO161 and compute its omega value."
inputs = tokenizer(query, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=512)
print(tokenizer.decode(outputs[0]))
```

### RAG Tools

| Tool | Description |
|------|-------------|
| [FAISS indexes](./tools/faiss/) | Pre-built vector indexes for all four corpora |
| [RAG query scripts](./tools/rag/) | Python scripts for corpus retrieval |
| [Schema validator](./tools/validators/) | Cross-corpus schema validation utilities |

---

## Mission

EPS Research is an independent research organization conducting self-directed, cross-domain astrophysics research without institutional affiliation or external funding. This platform reflects three core commitments:

**Open corpora** — All data products are released under CC BY 4.0 at Zenodo, with full provenance documentation, primary-source verification, and machine-readable schemas.

**Cross-epoch kinematic analysis** — The four corpora together span z = 0 to z ~ 6, enabling the first unified kinematic dataset from local HI rotation curves to ALMA [CII] observations approaching the epoch of reionization.

**Educational outreach** — The High-School Exploration Track makes the platform accessible to students, with friendly notebooks that require no prior astrophysics background.

---

## Future Expansion

This platform is designed to grow.

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
| Flagship 72B | Qwen2.5-72B fine-tuned on all four EPS corpora | 2026 |
| Desktop 31B | Gemma 4 31B fine-tuned on all four EPS corpora | 2026 |
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

**David C. Flynn** | EPS Research  
📧 davidflynn@eps-research.com  
🌐 [eps-research.com](https://eps-research.com)  
🔬 ORCID: [0000-0002-2768-6650](https://orcid.org/0000-0002-2768-6650)

---

*EPS Research — Independent astrophysics research, open science, educational outreach.*
