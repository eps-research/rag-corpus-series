# EPS Research Papers & Preprints

**EPS Research — Flynn, D.C.**

The full publication arc underlying the EPS Research Astro-RAG Platform.

---

## Paper 1 — Omega Correction Introduced

**Flynn, D.C. & Cannaliato, J. (2025)**  
*A New Empirical Fit to Galaxy Rotation Curves*  
Frontiers in Astronomy and Space Sciences, Volume 12  
DOI: [10.3389/fspas.2025.1680387](https://doi.org/10.3389/fspas.2025.1680387)  
arXiv: [2601.00522](https://arxiv.org/abs/2601.00522)

**Status:** Published December 2025  
**Metrics:** 4,400+ views, 256 downloads (May 2026)

### Summary

Introduces the omega (ω) kinematic correction term derived from observed stellar motion and anchored to Keplerian baselines:

```
V_adj = V_obs - R * omega
omega = (V2/R2 - V1/R1) * (R1/R2)^(3/2)   [rad/Gyr]
```

Derived from two boundary points (innermost and outermost measured rotation curve points). Validated across SPARC data. Consistently outperforms MOND and CDM halo models in RMSE and R² metrics without parametric tuning.

**Key results:**
- Empirical correction derived from boundary kinematics only
- Reproducible, minimally dependent on mass modeling
- Does not alter Newtonian dynamics or invoke dark matter distributions
- Mean omega = 7.06 ± 3.26 rad/Gyr across 84 SPARC Q=1 galaxies

---

## Paper 2 — Baryonic Validation Across 84 SPARC Galaxies

**Flynn, D.C. (2026)**  
*Baryonic Validation of the Omega Kinematic Correction Across 84 SPARC Galaxies*  
Submitted to New Astronomy (NEWAST-D-26-00207)  
Preprint: Zenodo [10.5281/zenodo.20132805](https://doi.org/10.5281/zenodo.20132805)

**Status:** Under review

### Summary

Full baryonic validation of the omega correction applied to 84 SPARC Q=1 disk galaxies using sign-preserving quadrature for gas, disk, and bulge components, and per-galaxy mass-to-light ratio optimization under the Maximum Disk constraint.

**Key results:**

| Metric | Value |
|--------|-------|
| Mean RMSE (omega vs V_bary) | 25.45 ± 1.57 km/s |
| Mean RMSE (Keplerian baseline) | 74.20 km/s |
| Mean RMSE (MOND vs V_bary same target) | 60.57 km/s |
| Galaxies improved | 53/84 |
| Regressions | 0/84 |
| Outer gaps negative | 84/84 |
| omega beats MOND same-target | 82/84 |

**Data and code:** [Zenodo 10.5281/zenodo.19798527](https://doi.org/10.5281/zenodo.19798527)

---

## Paper 3 — Unified HI Corpus v7.0 Data Descriptor

**Flynn, D.C. (2026)**  
*A Unified HI Rotation Curve Corpus for Computational Astrophysics: 438 Galaxies from SPARC, THINGS, LITTLE THINGS, and WALLABY DR2*  
Submitted to Astronomy & Computing (ASCOM-D-26-00129)  
arXiv: [2604.13489](https://arxiv.org/abs/2604.13489)

**Status:** Under review

---

## Paper 4 — Dwarf/Irregular Corpus v1.0 Data Descriptor

**Flynn, D.C. (2026)**  
*A Unified HI Rotation Curve Database for 129 Local Volume Dwarf and Irregular Galaxies*  
arXiv: [2605.22163](https://arxiv.org/abs/2605.22163)

**Status:** Submitted to PASP

---

## Paper 5 — GC Corpus v1.3.1 Data Descriptor

**Flynn, D.C. (2026)**  
*A Multi-Survey Machine-Readable Corpus of Milky Way Globular Cluster Parameters*  
arXiv: [2605.03099](https://arxiv.org/abs/2605.03099)

**Status:** Submitted to PASP

---

## Paper 6 — High-z Kinematic Corpus Z1 Data Descriptor

**Flynn, D.C. (2026)**  
*A Unified [CII] Morpho-Kinematic Corpus for 31 Star-Forming Galaxies at z = 4.26-5.68: The High-z Kinematic Corpus Z1*  
arXiv: [2605.25339](https://arxiv.org/abs/2605.25339)

**Status:** Published on arXiv

---

## Paper 7 — IntZ Kinematic Corpus v1.0 Data Descriptor ⭐ NEW

**Flynn, D.C. (2026)**  
*The EPS Research Intermediate-z Kinematic Corpus v1.0 (IntZ_v1): 1,292 Star-Forming Galaxies at z~0.4–2.7 from KROSS and KMOS³D for Cross-Epoch Kinematic Analysis and RAG Pipelines*  
Zenodo: [10.5281/zenodo.20453189](https://zenodo.org/records/20453189)  
arXiv: **submission in preparation** (target: astro-ph.IM)

**Status:** Zenodo published 2026-05-30 | arXiv submission in preparation

### Summary

Machine-readable kinematic corpus of 1,292 star-forming galaxies at z = 0.382–2.675, combining KROSS (Harrison et al. 2017; 586 galaxies) and KMOS³D (Wisnioski et al. 2019; 706 galaxies). Provides the intermediate-redshift anchor of the EPS cross-epoch omega arc.

**Key results:**

| Metric | Value |
|--------|-------|
| Total galaxies | 1,292 |
| Tier-1 (resolved, beam-corrected) | 166 (KROSS) |
| Tier-2 (integrated kinematics) | 1,126 |
| Omega median (Tier-1) | −9.087 ± 8.940 rad/Gyr |
| Omega sign | 100% negative |
| z range | 0.382–2.675 |

**Cross-epoch arc with this corpus:**

| Epoch | Survey | N (T1) | Median ω |
|-------|--------|--------|----------|
| z = 0 | SPARC | 84 | +7.06 rad/Gyr |
| z ~ 0.9 | KROSS (IntZ) | 166 | −9.087 rad/Gyr |
| z ~ 5 | ALPINE (Z1) | 8 | −13.05 rad/Gyr |

Note: These samples use different kinematic tracers (HI, Hα, [CII]). Physical interpretation deferred to Flynn & Cannaliato (in preparation).

**Note on MOSDEF:** Price et al. 2020 (ApJ 894, 91) was evaluated for inclusion. The individual galaxy kinematic catalog is not publicly archived. Data request recommended to S. H. Price.

---

## Planned Papers

| Paper | Target | Description |
|-------|--------|-------------|
| Paper 8 | A&A or ApJ | Cross-epoch omega evolution: z=0 to z~6 |
| Paper 9 | ApJ | RAMSES cosmological simulations z=6 → z=0 |
| Paper 10 | PASP | Z2 corpus: REBELS + CRISTAL at z~6-8 |

---

## Research Arc Summary

```
Paper 1 (2025) — omega correction introduced, Frontiers ✓ PUBLISHED
Paper 2 (2026) — 84 SPARC baryonic validation, New Astronomy — UNDER REVIEW
Paper 3 (2026) — v7 unified HI corpus 438 galaxies, A&C — UNDER REVIEW
Paper 4 (2026) — dwarf corpus 129 galaxies, PASP — SUBMITTED
Paper 5 (2026) — GC corpus 174 clusters, PASP — SUBMITTED
Paper 6 (2026) — high-z Z1 corpus 31 galaxies, arXiv — PUBLISHED
Paper 7 (2026) — IntZ corpus 1,292 galaxies, Zenodo — PUBLISHED | arXiv IN PREP
Paper 8 (2027) — cross-epoch omega evolution — PLANNED
Paper 9 (2027) — RAMSES Paper 3 — PLANNED
```

---

## Planned Paper — Omega Correction and Gravitational Lensing

**Flynn, D.C. (planned)**  
*Omega Kinematic Correction as a New Source of Spacetime Distortion: Implications for Gravitational Lensing*

Einstein's general relativity accounts for spacetime curvature from mass-energy.
The EPS omega correction introduces a spin-derived kinematic term — a second,
independent source of effective spacetime distortion beyond Einsteinian mass concentration.
This paper will explore the observational predictions for gravitational lensing
that differ from pure GR: modified Einstein ring radii, altered shear profiles,
and testable deviations in strong lensing systems.

**Status:** Planned

---
*Part of the [EPS Research Astro-RAG Platform](../README.md)*
