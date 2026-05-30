# IntZ Kinematic Corpus v1.0

**EPS Research — Flynn, D.C. (2026)**

## Overview

KROSS + KMOS³D integrated kinematics for 1,292 star-forming galaxies at
z = 0.38–2.68. The intermediate-redshift anchor of the EPS Research RAG
Astrophysics Corpus Series, providing the z~0.9 epoch of the cross-epoch
omega evolution arc.

## Quick Links

| Resource | Link |
|----------|------|
| Zenodo deposit | [10.5281/zenodo.20453189](https://doi.org/10.5281/zenodo.20453189) |
| arXiv preprint | in preparation (astro-ph.IM) |
| Journal submission | arXiv (in preparation) |

## Coverage

| Property | Value |
|----------|-------|
| Total galaxies | 1,292 |
| Redshift range | z = 0.382–2.675 |
| Median redshift | z = 0.922 |
| Tier-1 (resolved kinematics) | 166 (KROSS) |
| Tier-2 (integrated kinematics) | 1,126 |
| Surveys | KROSS + KMOS³D |

## Surveys

| Survey | N | z range | Tracer | Reference |
|--------|---|---------|--------|-----------|
| KROSS | 586 | 0.60–1.04 | Hα | Harrison et al. 2017, MNRAS 467 1965 |
| KMOS³D | 706 | 0.38–2.68 | Hα/[O III] | Wisnioski et al. 2019, ApJ 886 124 |

## Omega Results (Tier-1, N=166)

| Statistic | Value |
|-----------|-------|
| Median ω | −9.087 rad/Gyr |
| Stdev ω | 8.940 rad/Gyr |
| Sign | 100% negative |
| Outliers (>3σ flagged) | 4 galaxies |

**Cross-epoch arc (Flynn & Cannaliato 2025):**

| Corpus | Survey | N (T1) | Tracer | Median ω |
|--------|--------|--------|--------|----------|
| HI v7.0 | SPARC | 84 | HI 21cm | +7.06 rad/Gyr |
| IntZ v1.0 | KROSS | 166 | Hα | −9.087 rad/Gyr |
| Z1 v1.0 | ALPINE | 8 | [CII] | −13.05 rad/Gyr |

> ⚠️ These samples use different kinematic tracers probing different physical
> radii. The sign difference is an empirical finding; physical interpretation
> is deferred to Flynn & Cannaliato (in preparation).

## Three Canonical Examples

| Galaxy | Survey | z | Vc (km/s) | ω (rad/Gyr) | Notes |
|--------|--------|---|-----------|-------------|-------|
| KID-141 (C-zcos_z1_633) | KROSS T1 | 0.9822 | 256.97 | −16.507 | Massive rotator |
| GS4_33971 | KMOS³D T2 | 2.6754 | — | N/A | Cosmic noon starburst |
| KID-522 (S-zvipe_z1_827) | KROSS T1 | 0.8237 | 186.09 | −33.827 | Compact disk |

## Files (Zenodo)

| File | Description | Size |
|------|-------------|------|
| `intz_corpus_v1b.json` | Full corpus, nested schema | 4.1 MB |
| `intz_corpus_v1b.jsonl` | One galaxy per line, RAG-ready | 3.2 MB |
| `intz_corpus_v1b_flat.csv` | Flattened table, 1,292 rows | 252 KB |
| `intz_corpus_v1b_overview.png` | Six-panel summary figure | 284 KB |
| `README_intz_corpus_v1b.md` | Full documentation | 8 KB |

## Quick Load

```python
import json

# Load from Zenodo download
with open('intz_corpus_v1b.json') as f:
    data = json.load(f)
galaxies = data['galaxies']

# Tier-1 omega values
omega = [g['omega']['omega_value_rad_gyr']
         for g in galaxies
         if g['omega']['omega_available']]
print(f"N={len(omega)}, median={sorted(omega)[len(omega)//2]:.3f} rad/Gyr")
```

## Excluded Survey

**MOSDEF** (Price et al. 2020, ApJ 894, 91) — individual galaxy kinematic
catalog not publicly archived. Data request recommended to S. H. Price.

## Example Notebooks

20 verified Jupyter notebooks in [`examples/intz/`](../examples/intz/):

| Range | Notebooks | Topics |
|-------|-----------|--------|
| nb1–nb10 | Standard | Load, redshift dist, kinematics, main sequence, omega dist, examples, sigma, size-mass, CSV queries, RAG demo |
| nb11–nb20 | EPS Science | Omega vs z/mass/Vc, three-epoch arc ⭐, sign reversal test ⭐, SPARC bridge ⭐, disk assembly, Z1 bridge ⭐, outliers, end-to-end ⭐ |

## References

- Harrison et al. 2017, MNRAS 467, 1965 (KROSS)
- Johnson et al. 2018, MNRAS 474, 5076 (KROSS)
- Wisnioski et al. 2019, ApJ 886, 124 (KMOS³D)
- Lelli et al. 2016, AJ 152, 157 (SPARC, z=0 comparison)
- Le Fèvre et al. 2020, A&A 643, A1 (ALPINE, z~5 comparison)
- Price et al. 2020, ApJ 894, 91 (MOSDEF, excluded)
- Flynn & Cannaliato 2025, Frontiers Astron Space Sci 12 (omega method)
- Planck Collaboration 2020, A&A 641, A6 (cosmology)

## Citation

```
Flynn, D. C. (2026). EPS Research Intermediate-z Kinematic Corpus v1.0
(IntZ_v1): KROSS + KMOS3D Galaxy Kinematics at z~0.4-2.7.
Zenodo. https://doi.org/10.5281/zenodo.20453189
```

---
*Part of the [EPS Research Astro-RAG Platform](../README.md)*
