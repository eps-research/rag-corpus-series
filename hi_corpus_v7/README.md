# Unified HI Rotation Curve Corpus v7.3

**EPS Research — Flynn, D.C. (2026)**

## Overview

A unified corpus of 7,804 observed, spatially resolved HI rotation curve points across 438 galaxies from four surveys: SPARC (175), THINGS (34), LITTLE THINGS (26) and WALLABY DR2 (203).

Designed for kinematic analysis and LLM-based RAG pipelines. All radii in kpc, all velocities in km/s. Two-tier quality system: Tier 1 (SPARC, THINGS, LITTLE THINGS) and Tier 2 (WALLABY DR2, published WKAPP kinematic models).

**v7.3 is a corrective release.** It supersedes all earlier versions, including v7.1 (10.5281/zenodo.21768240), the version cited by Flynn (2027). See CORRECTIONS.md in the Zenodo record for every change.

## Quick Links

| Resource | Link |
|----------|------|
| Zenodo deposit (v7.3) | [10.5281/zenodo.23442703](https://doi.org/10.5281/zenodo.23442703) |
| Data descriptor | Flynn (2027), *Astronomy and Computing* 58, 101179, [10.1016/j.ascom.2026.101179](https://doi.org/10.1016/j.ascom.2026.101179) |
| arXiv preprint | [arXiv:2604.13489](https://arxiv.org/abs/2604.13489) |

## Coverage

| Survey | Galaxies | Data Points | Tier |
|--------|----------|-------------|------|
| SPARC | 175 | 3,391 | 1 |
| THINGS | 34 (19 with curves) | 2,110 | 1 |
| LITTLE THINGS | 26 | 877 | 1 |
| WALLABY DR2 | 203 | 1,426 | 2 |
| **Total** | **438** | **7,804** | |

## Files (Zenodo record)

| File | Description |
|------|-------------|
| `rotation_curve_corpus_v7.json` | Master JSON, authoritative (~2.3 MB) |
| `rotation_curve_corpus_v7.jsonl` | One galaxy per line |
| `rotation_curve_corpus_v7.1_flat.csv` | Catalogue table, 438 rows × 29 columns |
| `rotation_curve_corpus_v7_by_galaxy.zip` | Per-galaxy JSON archive |
| `READMEv7.md`, `CORRECTIONS.md` | Documentation and corrections log |
| `wallaby_dr2_ingest_v73.py` | WALLABY DR2 ingest script |
| `make_figures_v73.py` | Figure script |

## Quick Start

```python
import json

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

# DDO161 rotation curve
g = next(g for g in corpus['galaxies'] if g['galaxy'] == 'DDO161')
data = g['data']
R    = [p['Rad']  for p in data]
Vobs = [p['Vobs'] for p in data]
```

WALLABY rows use `Rad`, `Vrot` and `e_Vrot`; SPARC rows use `Rad`, `Vobs` and `errV`.

## Citation

```
Flynn, D.C. (2026). Unified Galaxy Rotation Curve Corpus (v7.3).
Zenodo. DOI: 10.5281/zenodo.23442703

Flynn, D.C. (2027). Astronomy and Computing, 58, 101179.
DOI: 10.1016/j.ascom.2026.101179
```

---
*Part of the [EPS Research Astro-RAG Platform](../README.md)*
