# Dwarf/Irregular HI Rotation Curve Corpus v1.0

**EPS Research — Flynn, D.C. (2026)**

## Overview

HI rotation curve data for 129 dwarf and irregular galaxies from four Local Volume surveys: LVHIS (33), VLA-ANGST (29), LITTLE THINGS (26), and WALLABY DR2 dwarfs (41).

The dark-matter-dominated dwarf regime provides the cleanest test of the omega kinematic correction — baryonic physics is simpler, mass-to-light ratios are better constrained, and the correction signal is strongest.

## Quick Links

| Resource | Link |
|----------|------|
| Zenodo deposit | [10.5281/zenodo.20320362](https://doi.org/10.5281/zenodo.20320362) |
| arXiv preprint | [arXiv:2605.22163](https://arxiv.org/abs/2605.22163) |
| Journal submission | PASP (pending) |

## Coverage

| Survey | Galaxies | Tier | Notes |
|--------|----------|------|-------|
| LVHIS | 33 | 1/2 | Local Volume HI Survey |
| VLA-ANGST | 29 | 1/2 | VLA ACS Nearby Galaxy Survey Treasury |
| LITTLE THINGS | 26 | 1 | Full tilted-ring rotation curves |
| WALLABY DR2 dwarfs | 41 | 2 | Filtered from v7.0 |
| **Total** | **129** | | |

## Key Finding

All 24 omega-ready LITTLE THINGS galaxies show negative outer gaps, consistent with the Flynn & Cannaliato (2025) omega correction across the full SPARC sample. Median omega = 9.94 rad/Gyr (SPARC mean: 7.06 rad/Gyr), confirming the kinematic regularity persists into the dark-matter-dominated dwarf regime.

## Files

| File | Description |
|------|-------------|
| `dwarf_irregular_corpus_v1.json` | Full corpus JSON |
| `dwarf_irregular_corpus_v1.jsonl` | RAG-ready JSONL |
| `dwarf_irregular_corpus_v1_flat.csv` | Flat CSV (32 columns) |
| `dwarf_irregular_corpus_v1_by_galaxy.zip` | Per-galaxy ZIP |
| `rag_examples_v1.json` | Three worked RAG examples |
| `omega_results_dwarfs.csv` | Per-galaxy omega results (24 galaxies) |
| `fig_ddo154_omega.png` | DDO 154 four-curve rotation curve |
| `compute_omega_dwarfs.py` | Omega computation script |
| `README.md` | Full documentation |

## Quick Start

```python
import json

with open('dwarf_irregular_corpus_v1.json') as f:
    corpus = json.load(f)

# Get all omega-ready galaxies
omega_ready = [g for g in corpus['galaxies']
               if g.get('omega_ready') and g.get('quality_tier') == 1]
print(f"Omega-ready: {len(omega_ready)} galaxies")
```

## Citation

```
Flynn, D.C. (2026). Dwarf/Irregular Galaxy HI Rotation Curve Corpus v1.0.
Zenodo. DOI: 10.5281/zenodo.20320362
arXiv: 2605.22163
```

---
*Part of the [EPS Research Astro-RAG Platform](../README.md)*
