# Dwarf/Irregular HI Rotation Curve Corpus v1.0

**EPS Research — Flynn, D.C. (2026)**

## Overview

HI rotation curve data for 129 dwarf and irregular galaxies from four Local Volume surveys: LVHIS (33), VLA-ANGST (29), LITTLE THINGS (26), and WALLABY DR2 dwarfs (41).

The dark-matter-dominated dwarf regime provides a clean test of the omega kinematic correction — baryonic physics is simpler, mass-to-light ratios are better constrained, and the correction signal is strong.

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

All 24 omega-ready LITTLE THINGS galaxies yield **positive** omega values under the canonical Equation 6 of Flynn & Cannaliato (2025), computed from independently measured innermost and outermost rotation-curve rings. Median omega = +9.94 rad/Gyr (SPARC mean: +7.06 rad/Gyr), consistent with the z=0 result and with the expectation that dark-matter-dominated systems with rising outer rotation curves produce larger positive omega values.

> **Note (August 2026):** These dwarf omega values are computed from measured boundary rings using the canonical Equation 6 and are unaffected by the formula-implementation and data-provenance issues that led to the withdrawal of the intermediate- and high-redshift omega values. See [CORRECTIONS.md](../CORRECTIONS.md) for platform-wide context. This corpus is a z=0 (local universe) dataset and is not part of the withdrawn cross-epoch comparison.

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

## Omega Formula

Omega is computed using the canonical Equation 6 of Flynn & Cannaliato (2025):

```
ω = V₂/R₂ − (V₁/R₁) × (R₁/R₂)^1.5     [rad/Gyr]
V_adj = V_obs − R × ω
```

where (R₁, V₁) and (R₂, V₂) are the innermost and outermost **independently measured** reliable rotation-curve points. Note that the `(R₁/R₂)^1.5` factor multiplies only the `V₁/R₁` term, not the full difference.

## Quick Start

```python
import json

with open('dwarf_irregular_corpus_v1.json') as f:
    corpus = json.load(f)

# Get all omega-ready galaxies
omega_ready = [g for g in corpus['galaxies']
               if g.get('omega_ready') and g.get('quality_tier') == 1]
print(f"Omega-ready: {len(omega_ready)} galaxies")

# Compute omega from measured boundary rings (canonical Eq. 6)
for g in omega_ready:
    d = g['data']
    R1, V1 = d[0]['Rad'],  d[0]['Vobs']
    R2, V2 = d[-1]['Rad'], d[-1]['Vobs']
    omega = V2/R2 - (V1/R1) * (R1/R2)**1.5
    print(f"{g['galaxy']:12s} omega={omega:+.2f} rad/Gyr")
```

## Citation

```
Flynn, D.C. (2026). Dwarf/Irregular Galaxy HI Rotation Curve Corpus v1.0.
Zenodo. DOI: 10.5281/zenodo.20320362
arXiv: 2605.22163

Flynn, D.C. & Cannaliato, J. (2025). Frontiers in Astronomy and Space Sciences, 12.
DOI: 10.3389/fspas.2025.1680387
```

---
*Part of the [EPS Research Astro-RAG Platform](../README.md)*
