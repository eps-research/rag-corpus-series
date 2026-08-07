# EPS Research Intermediate-z Kinematic Corpus v1.0 (IntZ_v1)

**KROSS + KMOS³D Galaxy Kinematics at z~0.4–2.7**  
EPS Research | David C. Flynn (ORCID: 0000-0002-2768-6650)  
Part of the [EPS Research RAG Corpus Series](https://github.com/eps-research/rag-corpus-series)  
Zenodo DOI: [10.5281/zenodo.20453189](https://doi.org/10.5281/zenodo.20453189)

---

> **⚠️ Correction Notice (August 2026):** The omega (ω) values previously reported in this corpus have been **withdrawn**. An external audit identified two independent problems with the KROSS omega field: (1) a formula-implementation discrepancy — the values were computed with a parenthesized variant that does not match Equation 6 of Flynn & Cannaliato (2025); and (2) a data-provenance issue — the KROSS boundary points were template-derived from fixed rescalings of Vc and R_half, not independently measured inner and outer rotation-curve rings. As a result, the KROSS omega values are **not eligible** for cross-epoch comparison, and the previously reported cross-epoch sign reversal has been withdrawn. All underlying observed KROSS/KMOS³D quantities (redshift, Vc, R_half, stellar mass, dispersion, etc.) are unaffected. See [CORRECTIONS.md](https://github.com/eps-research/rag-corpus-series/blob/main/CORRECTIONS.md) for full details.

---

## Overview

The IntZ corpus is a machine-readable kinematic dataset of 1,292
star-forming galaxies at intermediate redshift (z = 0.382–2.675),
combining two major IFU/slit spectroscopy surveys:

| Survey   | N galaxies | z range    | Tracer | Tier |
|----------|-----------|------------|--------|------|
| KROSS    | 586       | 0.60–1.04  | Hα     | T1+T2|
| KMOS³D   | 706       | 0.38–2.68  | Hα/[OIII] | T2 |
| **Total**| **1,292** | **0.38–2.68** | | |

The corpus provides observed kinematic parameters (circular velocity,
dispersion, V/σ, stellar mass, morphology) for the full sample. The
derived omega field is currently withdrawn pending ingestion of measured
rotation-curve boundary points (see correction notice above and Omega
Status below).

---

## Files

| File | Description | Size |
|------|-------------|------|
| `intz_corpus_v1b.json` | Full corpus, nested schema | 4.1 MB |
| `intz_corpus_v1b.jsonl` | One galaxy per line, RAG-ready | 3.2 MB |
| `intz_corpus_v1b_flat.csv` | Flattened table, 1,292 rows | ~279 KB |
| `intz_corpus_v1b_overview.png` | Six-panel summary figure | — |

> **Note:** The currently deposited data files still contain the withdrawn
> `omega_value_rad_gyr` field. Corrected data products, in which this field
> is set to `null` with explicit deprecation metadata, are being regenerated
> and will be published as a new Zenodo version. Until then, do not use the
> `omega_value_rad_gyr` values for any analysis.

---

## Schema

Each galaxy record contains the following top-level blocks:

```json
{
  "identifiers":        {...},   // survey ID, RA, Dec
  "redshift":           {...},   // z_spec, z_source
  "cosmology_derived":  {...},   // D_L, D_A, lookback time
  "photometry":         {...},   // magnitudes
  "stellar_properties": {...},   // M*, SFR, method
  "morphology":         {...},   // R_half, b/a, inclination, PA
  "kinematics":         {...},   // Vc, sigma0, v/sigma, flags
  "angular_momentum":   {...},
  "toomre":             {...},
  "agn_diagnostics":    {...},
  "baryonic":           {...},
  "omega":              {...},   // WITHDRAWN — see Omega Status
  "metadata":           {...},   // survey, tier, reference, version
  "rag_summary":        "..."    // human-readable one-line summary
}
```

### Key kinematic fields

| Field | Description | Units |
|-------|-------------|-------|
| `Vc_kms` | Circular velocity (beam-smear corrected, Tier-1) | km/s |
| `sigma0_kms` | Intrinsic velocity dispersion (Tier-1) | km/s |
| `v_over_sigma` | Kinematic ratio V/σ | — |
| `beam_smear_corrected` | True=corrected (KROSS T1); False=integrated LW (KMOS3D) | bool |
| `omega_value_rad_gyr` | **WITHDRAWN** — see Omega Status | rad/Gyr |
| `omega_available` | **WITHDRAWN** — currently not computable | bool |
| `omega_quality` | **WITHDRAWN** | string |

### Tier definitions

- **Tier 1:** Spatially resolved kinematics with beam-smear correction.
  Vc and σ₀ are individually measured.
  *(166 KROSS galaxies)*

- **Tier 2:** Integrated 1D kinematics only. sigma represents integrated
  line width, **not** beam-corrected intrinsic σ₀.
  *(1,126 galaxies: all KMOS³D + unresolved KROSS)*

> ⚠️ **Important:** Do not mix Tier-1 sigma0 and Tier-2 sigma values in
> the same statistical analysis. They measure different quantities.
> The `beam_smear_corrected` flag distinguishes them.

### Missing values

All missing or unreliable numeric values are encoded as `null`.
**No −999.0 sentinels are used in v1b.** (684 sentinels were replaced
during QC; see v1b fix log in `corpus_metadata` block.)

---

## Omega Status (corrected August 2026)

The omega field in this corpus has been **withdrawn**. Two independent
problems were identified by external audit:

1. **Formula-implementation discrepancy.** The stored values were computed
   using a parenthesized variant `ω = (V₂/R₂ − V₁/R₁) × (R₁/R₂)^1.5`, which
   does **not** match the canonical Equation 6 of Flynn & Cannaliato (2025):

   ```
   ω = V₂/R₂ − (V₁/R₁) × (R₁/R₂)^1.5
   ```

   The parenthesization difference changes the sign of the result for
   typical rotation-curve shapes.

2. **Template-derived boundary points.** More fundamentally, the KROSS
   omega values were **not** computed from independently measured inner and
   outer rotation-curve rings. Instead the boundary points were constructed
   from fixed rescalings of the integrated circular velocity Vc and
   half-light radius R_half:

   ```
   R₁ = 0.3 · R_half     V₁ = 0.6577 · Vc
   R₂ = R_half           V₂ = Vc
   ```

   This makes the quantity a template proxy driven by (Vc, R_half), not an
   independently observed two-boundary kinematic measurement. It is
   therefore **not suitable** for like-for-like cross-epoch comparison with
   corpora (e.g. SPARC, Z1) that use measured rotation-curve boundary points.

**Current status:** `omega_value_rad_gyr` is withdrawn. Corrected data
products will encode it as `null` with explicit deprecation metadata:

```json
{
  "omega_eps": null,
  "omega_status": "not_computable_from_current_corpus",
  "omega_reason": "No independently tabulated inner and outer rotation-curve points",
  "legacy_omega": -9.0866,
  "legacy_omega_status": "withdrawn_formula_and_template_derived",
  "formula_version": null
}
```

**To restore KROSS omega scientifically** requires ingesting spatially
resolved KROSS rotation-curve data sufficient to establish independently
observed (R₁, V₁) and (R₂, V₂) with uncertainties. Only then can a standard
Equation 6 omega be computed for this corpus.

---

## Canonical Examples

### KID-141 — Massive KROSS Rotator
```
Name:    C-zcos_z1_633
Survey:  KROSS, Tier 1
z_spec:  0.9822 (lookback 6.13 Gyr)
log M*:  10.48,  SFR: 8.29 Msun/yr
Vc:      256.97 km/s
R_half:  3.05 kpc
omega:   withdrawn (see Omega Status)
```
Massive main-sequence disk at z~1. Representative of the high-Vc
Tier-1 KROSS population.

### GS4_33971 — KMOS³D Cosmic Noon Starburst
```
Name:    GS4_33971 (GOODS-S field)
Survey:  KMOS³D, Tier 2
z_spec:  2.6754 (lookback ~11.3 Gyr)
log M*:  10.83,  SFR: 187.6 Msun/yr
sigma:   53.6 km/s (integrated line width)
omega:   not available
```
Massive, turbulent starburst at cosmic noon. Representative of the
Tier-2 integrated-kinematics population.

---

## Citation

```
Flynn, D.C. (2026). EPS Research Intermediate-z Kinematic Corpus v1.0 (IntZ_v1).
Zenodo. DOI: 10.5281/zenodo.20453189

Harrison, C.M. et al. (2017). MNRAS, 467, 1965. [KROSS]
Wisnioski, E. et al. (2019). ApJ, 886, 124. [KMOS3D]

Omega framework:
Flynn, D.C. & Cannaliato, J. (2025). Frontiers in Astronomy and Space Sciences, 12.
DOI: 10.3389/fspas.2025.1680387
```

---
*Part of the [EPS Research Astro-RAG Platform](https://github.com/eps-research/rag-corpus-series)*
