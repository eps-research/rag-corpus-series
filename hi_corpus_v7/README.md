# Unified HI Rotation Curve Corpus v7.0

**EPS Research — Flynn, D.C. (2026)**

## Overview

A unified corpus of 8,963 spatially resolved HI rotation curve measurements across 438 galaxies from four major surveys: SPARC (175), THINGS (34), LITTLE THINGS (26), and WALLABY DR2 (203).

Designed for traditional kinematic analysis and LLM-based RAG pipelines. All radii in kpc, all velocities in km/s. Two-tier quality system: Tier 1 (hand-curated) and Tier 2 (automated WALLABY pipeline).

## Quick Links

| Resource | Link |
|----------|------|
| Zenodo deposit | [10.5281/zenodo.19563417](https://doi.org/10.5281/zenodo.19563417) |
| arXiv preprint | [arXiv:2604.13489](https://arxiv.org/abs/2604.13489) |
| Journal submission | Astronomy & Computing (ASCOM-D-26-00129) |

## Coverage

| Survey | Galaxies | Data Points | Tier |
|--------|----------|-------------|------|
| SPARC | 175 | 3,391 | 1 |
| THINGS | 34 (19 w/data) | 2,110 | 1 |
| LITTLE THINGS | 26 | 1,716 | 1 |
| WALLABY DR2 | 203 | 1,746 | 2 |
| **Total** | **438** | **8,963** | |

## Files

| File | Description |
|------|-------------|
| `rotation_curve_corpus_v7.json` | Master JSON (~2.0 MB) |
| `rotation_curve_corpus_v7_flat.csv` | Flat CSV (438 rows, 29 columns) |
| `rotation_curve_corpus_v7_by_galaxy.zip` | Per-galaxy JSON archive |
| `READMEv7.md` | Full documentation |
| `wallaby_ingest.py` | WALLABY ingestion script |
| `make_figures_v7.py` | Figure generation script |

## Quick Start

```python
import json

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

# Get DDO161 rotation curve
g = next(g for g in corpus['galaxies'] if g['galaxy'] == 'DDO161')
data = g['data']
R    = [p['Rad']  for p in data]
Vobs = [p['Vobs'] for p in data]
```

## Citation

```
Flynn, D.C. (2026). Unified Galaxy HI Rotation Curve Corpus v7.0.
Zenodo. DOI: 10.5281/zenodo.19563417

Flynn, D.C. & Cannaliato, J. (2025). Frontiers in Astronomy and Space Sciences, 12.
DOI: 10.3389/fspas.2025.1680387
```

---
*Part of the [EPS Research Astro-RAG Platform](../README.md)*
