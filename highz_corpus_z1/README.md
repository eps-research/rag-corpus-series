# High-z Kinematic Corpus Z1

**EPS Research — Flynn, D.C. (2026)**

## Overview

ALMA [CII] 158μm morpho-kinematic data for 31 star-forming main-sequence galaxies at z = 4.26–5.68 from the ALPINE survey (Jones et al. 2021). The high-redshift anchor of the EPS Research RAG Astrophysics Corpus Series.

## Quick Links

| Resource | Link |
|----------|------|
| Zenodo deposit | [10.5281/zenodo.20369286](https://doi.org/10.5281/zenodo.20369286) |
| arXiv preprint | 2605.25339 |
| Journal submission | arXiv (submitted) |

## Coverage

| Property | Value |
|----------|-------|
| Total galaxies | 31 |
| Redshift range | z = 4.26–5.68 |
| Maximum redshift | z = 5.6773 (DC773957) |
| Confirmed rotators (ROT) | 8 |
| Mergers (MER) | 5 |
| Dispersion-dominated (DIS) | 3 |
| Uncertain (UNC) | 15 |
| Quality tier 1 (per-ring RC) | 8 |
| Quality tier 2 (classification only) | 23 |

## Files

| File | Description |
|------|-------------|
| `high_z_kinematic_corpus_Z1.json` | Full nested JSON corpus |
| `high_z_kinematic_corpus_Z1.jsonl` | RAG-ready JSONL |
| `high_z_kinematic_corpus_Z1_flat.csv` | Flat CSV (31 rows) |
| `high_z_kinematic_corpus_Z1_by_galaxy.zip` | Per-galaxy ZIP |
| `rag_examples_hz_Z1.json` | Three worked RAG examples |
| `hz_nb1_rotator_kinematics.ipynb` | Example 1: J0817 rotation curve |
| `hz_nb2_population_diversity.ipynb` | Example 2: Population statistics |
| `hz_nb3_eps_omega_bridge.ipynb` | Example 3: Cross-corpus omega application |
| `README_Z1.md` | Full documentation |

## Key Result

Applying the Flynn & Cannaliato (2025) omega formula to all 8 tier-1 rotators yields negative values (median −13.05 rad/Gyr), contrasting with positive values at z = 0 (SPARC mean +7.06, dwarf median +9.94 rad/Gyr). This sign reversal is consistent with the known evolution from centrally concentrated high-z systems to extended rotating disks at z = 0.

## Quick Start

```python
import json

with open('high_z_kinematic_corpus_Z1.json') as f:
    corpus = json.load(f)

# Get all tier-1 rotators
rotators = [g for g in corpus['galaxies']
            if g.get('is_rotator') and g.get('quality_tier') == 1]

# Compute omega for each
for g in rotators:
    d  = g['data']
    R1, V1 = d[0]['R_kpc'],  d[0]['Vrot_kms']
    R2, V2 = d[-1]['R_kpc'], d[-1]['Vrot_kms']
    omega = (V2/R2 - V1/R1) * (R1/R2)**1.5
    print(f"{g['galaxy']:20s} z={g['redshift']:.4f}  omega={omega:.2f} rad/Gyr")
```

## Important Caveats

1. Maximum redshift is z = 5.6773, not z = 6
2. Only 8/31 galaxies have per-ring rotation curve data
3. 2–3 rings per tier-1 galaxy — boundary conditions poorly constrained
4. No baryonic decomposition available at z~5
5. Beam smearing affects all entries despite 3DBarolo correction
6. ALPINE selection bias — misses true low-mass progenitor population

## Citation

```
Flynn, D.C. (2026). High-z Kinematic Corpus Z1.
Zenodo. DOI: 10.5281/zenodo.20369286

Jones, G.C. et al. (2021). MNRAS, 507, 3540.
DOI: 10.1093/mnras/stab2703
```

---
*Part of the [EPS Research Astro-RAG Platform](../README.md)*
