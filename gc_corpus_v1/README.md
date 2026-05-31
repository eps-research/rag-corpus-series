# Milky Way Globular Cluster Corpus v1.3.1

**EPS Research — Flynn, D.C. (2026)**

## Overview

A unified, machine-readable corpus of fundamental parameters for 174 Milky Way globular clusters assembled from four independent published survey catalogs: Harris (1996, 2010 ed.), Vasiliev & Baumgardt (2021) Gaia EDR3, Baumgardt et al. (2023) N-body dynamics, and Schiavon et al. (2024) APOGEE DR17 chemistry.

## Quick Links

| Resource | Link |
|----------|------|
| Zenodo deposit | [10.5281/zenodo.19907766](https://doi.org/10.5281/zenodo.19907766) |
| arXiv preprint | [arXiv:2605.03099](https://arxiv.org/abs/2605.03099) |
| Journal submission | PASP (pending) |

## Coverage

| Source | Clusters | Data Points | Description |
|--------|----------|-------------|-------------|
| Harris (1996, 2010 ed.) | 157/174 | ~6,375 | Photometry, structure, kinematics |
| Vasiliev & Baumgardt (2021) | 170/174 | ~1,870 | Gaia EDR3 proper motions |
| Baumgardt et al. (2023) | 154/174 | ~8,821 | N-body dynamical parameters |
| Schiavon et al. (2024) APOGEE DR17 | 72/174 | ~372 | Mean chemical abundances |
| **Total** | **174** | **17,438** | |

## Files

| File | Description |
|------|-------------|
| `harris_gc_corpus_v1.3.1.json` | Full nested JSON (868 KB) |
| `harris_gc_corpus_v1.3.1.jsonl` | RAG-ready JSONL (623 KB) |
| `harris_gc_corpus_v1.3.1_flat.csv` | Flat CSV (82 columns) |
| `README.md` | Full documentation |

## Quick Start

```python
import json

clusters = []
with open('harris_gc_corpus_v1.3.1.jsonl') as f:
    for line in f:
        clusters.append(json.loads(line))

# Get NGC 104 (47 Tuc)
ngc104 = next(c for c in clusters if c['cluster_id'] == 'NGC 104')
print(f"Mass: {ngc104['baumgardt2023']['mass_msun']:,.0f} Msun")
print(f"[Fe/H]: {ngc104['metallicity']['feh']}")

# All clusters with APOGEE chemistry
with_chem = [c for c in clusters
             if c.get('apogee_dr17') and
             c['apogee_dr17'].get('feh_apogee') is not None]
print(f"Clusters with APOGEE [Fe/H]: {len(with_chem)}")
```

## Version History

| Version | Clusters | Change |
|---------|----------|--------|
| v1.0 | 157 | Harris (1996, 2010 ed.) base |
| v1.1 | 174 | + Vasiliev & Baumgardt (2021) Gaia EDR3 |
| v1.2 | 174 | + Baumgardt et al. (2023) N-body |
| v1.3 | 174 | + Schiavon et al. (2024) APOGEE DR17 |
| **v1.3.1** | **174** | **Bug fixes: position parser, metallicity, CSV column** |

## Citation

```
Flynn, D.C. (2026). Milky Way Globular Cluster Corpus v1.3.1.
Zenodo. DOI: 10.5281/zenodo.19907766
arXiv: 2605.03099
```

---
*Part of the [EPS Research Astro-RAG Platform](../README.md)*
