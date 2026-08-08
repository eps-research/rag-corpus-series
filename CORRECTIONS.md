# Corrections Log

## 4 August 2026 — Cross-Epoch Omega Formula Correction

**Severity:** Result-changing  
**Affected result:** The reported cross-epoch omega sign reversal (+7.13 → −9.09 → −13.05)  
**Status:** Sign reversal **withdrawn**; z=0 SPARC result **unaffected**

### What happened

An external formula audit (conducted by Dennis Mungai using the Kimi model, 2 August 2026) identified two errors in the cross-epoch omega analysis:

**1. Operator-precedence parenthesization error.**  
The canonical omega equation (Flynn & Cannaliato 2025, Eq. 6) is:

```
ω = V₂/R₂ − (V₁/R₁) · (R₁/R₂)^1.5          [Formula B — correct]
```

The IntZ and Z1 corpus-generation code implemented:

```
ω = (V₂/R₂ − V₁/R₁) · (R₁/R₂)^1.5          [Formula A — incorrect]
```

These are not algebraically equivalent. Formula A applies the (R₁/R₂)^1.5 scaling to the entire difference; Formula B applies it only to the inner term. For typical rotation curves, Formula B produces positive ω while Formula A can produce negative ω from the same inputs.

The z=0 SPARC pipeline used Formula B (correct). The IntZ and Z1 pipelines used Formula A (incorrect). The Version 1.0 preprint compared correctly computed z=0 values against incorrectly computed z>0 values, producing the spurious sign reversal.

A 43-file operator-precedence patch was applied on 12 July 2026 (`fix: Eq.6 operator-precedence correction (2026-07-12) — 43 files patched`), but the corrected formula was **not propagated** into the stored corpus data products (JSON, CSV, JSONL) in `intz_corpus_v1/` and `highz_corpus_z1/`, nor into the derived figures, notebooks, or manuscript statistics.

**2. KROSS template-derivation problem (independent of parenthesization).**  
The 166 KROSS Tier-1 omega values were not computed from independently measured rotation-curve boundary points. Each value was derived from a fixed power-law template:

- R₁ = 0.3 · R_half
- V₁ = 0.6577 · V_c
- R₂ = R_half
- V₂ = V_c

This produces ω ∝ V_c / R_half with a constant proportionality factor (exponent SD ~10⁻⁴ across all 166 galaxies) and null uncertainty on every record. The Version 1.0 manuscript stated that IntZ used "the innermost and outermost tabulated ring radii" — this was incorrect.

### Corrected results

Under uniform application of Formula B:

| Sample | N | Previous ω | Corrected ω | Status |
|--------|---|-----------|-------------|--------|
| SPARC (z=0, HI) | 175 | +7.13 | +7.13 | **Unchanged** |
| KROSS (z~0.9, Hα) | 166 | −9.09 | null | **Withdrawn** — template-derived, no boundary-ring data |
| ALPINE Z1 (z~5, [CII]) | 8 | −13.05 | +12.621 (median, all 8 positive) | **Complete** — Zenodo 10.5281/zenodo.21834678 |
| Cross-epoch sign reversal | — | Claimed | Does not exist | **Withdrawn** |

### What was corrected

**Repository (this commit):**
- `intz_corpus_v1/` — KROSS omega set to null; legacy values preserved in deprecated fields
- `highz_corpus_z1/` — Z1 omega recomputed using canonical Formula B
- `README.md` — Sign-reversal claims, cross-epoch table, and "reproduce sign reversal" language removed
- `QuickStart.ipynb` — Sign-reversal reproduction section removed or relabeled
- Omega-specific notebooks (nb5, nb11–nb20) — Corrected or marked as suspended
- Five PNG figures — Withdrawn (intz_nb11, nb14, nb15, nb16, nb18)
- `CORRECTIONS.md` — This file added

**Zenodo:**
- Record 21383809 (cross-epoch preprint) — Superseded by correction note (Version 2.0)
- Record 20453189 (IntZ corpus) — Corrected release with omega withdrawal
- Record 21327061 (Z1 corpus) — Corrected release with recomputed omega

### What is NOT affected

- The canonical omega equation (Flynn & Cannaliato 2025, Eq. 6)
- The z=0 SPARC omega result (+7.13 km/s/kpc, 175 galaxies, 100% positive)
- The 84-galaxy baryonic validation (93% success rate)
- All underlying survey data (SPARC rotation curves, KROSS/KMOS³D source parameters, ALPINE per-ring 3DBarolo measurements)
- The HI v7.0, Dwarf v1.0, and GC v1.3.2 corpora
- The MCP server, REST wrapper, and FAISS infrastructure (architecture intact; served data corrected)
- ~130 non-omega notebooks

### Prevention measures

1. Named-term decomposition standardized across all notebooks and corpus generators (outer_term/inner_term form). A centralized `omega_eps()` function is planned but not yet implemented.
2. Regression tests:
   - M33 anchor test: outer_term=(119.6/37.3); inner_term=(22.73/0.24)*((0.24/37.3)**1.5); omega_kms_kpc=outer_term-inner_term must equal 5.093 ± 0.01
   - Wrong-parenthesization detection test: verifies Formula A ≠ Formula B
3. CI check for disallowed formula patterns (`(V2/R2 - V1/R1) * (R1/R2)**1.5`).

### Attribution

The formula discrepancy was identified by Dennis Mungai via an audit conducted with the Kimi model (Moonshot AI). The audit reproduced the z=0 SPARC values, identified the parenthesization mismatch in the z>0 implementations, and discovered the KROSS template-derivation issue. This finding led directly to the present correction.

### Units clarification

ω in rad Gyr⁻¹ ≈ 1.0227 × ω in km s⁻¹ kpc⁻¹. The Version 1.0 manuscript used rad Gyr⁻¹ throughout but the table header in the platform README incorrectly stated "rads/sec" and the conclusion stated "km/sec." This correction standardizes on km s⁻¹ kpc⁻¹ as the computational unit with explicit conversion where rad Gyr⁻¹ is used.

---

## August 7, 2026 — Remediation Complete

**Z1 omega recomputation:** All 8 tier-1 rotators recomputed under canonical
Eq.6. All values positive (median +12.621 rad/Gyr, mean +18.099 rad/Gyr).
Sign reversal confirmed as formula artifact. Corrected corpus published at
Zenodo 10.5281/zenodo.21834678.

**IntZ omega null-out:** All 166 KROSS omega values set to null in
intz_corpus_v1b.json, intz_corpus_v1b_flat.csv, and intz_corpus_v1b.jsonl.
Legacy values preserved in legacy_omega_value field. Corrected corpus
published at Zenodo 10.5281/zenodo.21841382.
