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
   - M33 anchor test: R1,V1=0.24,37.3; R2,V2=22.73,119.6; outer_term=(V2/R2); inner_term=(V1/R1)*((R1/R2)**1.5); omega_kms_kpc=outer_term-inner_term must equal 5.093 ± 0.01
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

---

## 2 October 2026 — LITTLE THINGS model rows in HI v7.x and Dwarf v1.0; dwarf ω v1.1

**Severity:** Data-provenance (per-ring); no change to any published headline result
**Affected:** HI Corpus v7.0/v7.1 (25 of 26 LITTLE THINGS galaxies); Dwarf/Irregular Corpus v1.0
(24 omega-ready galaxies, inherited via v7 transfer); omega_results_dwarfs.csv v1.0

### What happened

LITTLE THINGS rotation curves were ingested from Oh et al. (2015), VizieR J/AJ/149/180/rotdmbar
(1,716 rows = 877 `Data` + 839 `Model`). The `Type` column was dropped, so the 839
pseudo-isothermal model rows were stored as `Vobs` after the observed rows. The model rows were
also rescaled with the Data R0.3/V0.3 rather than their own scale factors.

### Effect on dwarf ω

`compute_omega_dwarfs.py` v1.0 sorted the combined rows by radius, so the outer boundary point
could come from the model curve (17 of 24 galaxies changed, −20% to +24%). Separately, v1.0
divided by 1.022 instead of multiplying by 1.0227 (rad/Gyr values ~4.4% low), retained the
withdrawn outer-gap diagnostic, and compared against SPARC 7.06 mislabelled as rad/Gyr
(7.06 is km/s/kpc = 7.22 rad/Gyr).

### Correction

`omega_results_dwarfs` v1.1 uses observed (`Type == 'Data'`) rows only, canonical Eq. 6 in
named-term form, and the correct conversion (× 1.0227). Outer-gap and SPARC-comparison columns
are removed. All 24 values are positive. Per-galaxy eligibility values only; no population
statistic is reported.

### Verification

Independent recompute from VizieR `Data` rows
(`audits/2026-10-02_little_things/lt_provenance_and_dwarf_omega_check.ipynb`, run in JupyterLab
on Node1, 2 October 2026):
- VizieR `Data` rows match the v7.1 first block in 26/26 galaxies
- DDO 154 at Rmax = 7.32 kpc: second block 49.23 km/s vs catalogue Viso(Rmax) 49.2 (model);
  first block 47.86 vs observed V(Rmax) 47.8
- Dwarf ω: 24/24 positive; max |Δω| vs v1.1 = 5×10⁻⁵ km/s/kpc
- Inputs: HI v7.1 JSON (Zenodo 21768240) sha256
  `a9d668ea9649be5473f161157ab20436177ba98abfa2c9fdb9ad1069bee81327`;
  Dwarf v1.0 JSON (Zenodo 20320362) sha256
  `452fba4108d29a21e5246b5446a7910bfcf085dc2371f770ec9db5702a944429`

### Not affected

SPARC (175 galaxies, no duplicate radii), THINGS, WALLABY, the SPARC N = 84 benchmark
(+7.06 km/s/kpc), Z1, IntZ.

### Status (updated 18 October 2026)

- **HI: done.** HI v7.3 is published at Zenodo 10.5281/zenodo.23442703 with observed rows only
  (LITTLE THINGS 877 points; corpus total 7,804), and this repository is re-pinned to it.
- **Dwarf: still pending.** A Dwarf v1 Zenodo version carrying a `curve_type` (Data/Model) field
  has not yet been published. The repository uses the observed-only v1.1 table (dw24).
- `check_omega_formula.py` to flag division by any conversion constant: pending.

---

## 18 October 2026 — Notebook repository re-pinned to HI v7.3; audit findings and known open items

### What changed

- HI notebooks, generators, QuickStart and documentation use HI Corpus v7.3 (Zenodo
  10.5281/zenodo.23442703): 438 entries, 7,804 observed points. The bundled copies match the
  published files byte for byte.
- One baryonic-velocity helper implements Eq. 1 (sign applied to the gas term only) in every HI
  notebook that needs V_bar.
- Published omega values are labelled in their native units: DDO161 4.69 km/s/kpc
  (= 4.80 rad/Gyr); SPARC N = 84 mean 7.06 ± 3.26 km/s/kpc (= 7.22 ± 3.33 rad/Gyr).
- Fixes from the independent audits (Sol 6.1, 18–19 October 2026): the IntZ bridge uses SPARC
  only (175 entries); ex06 bins include all 423 curves; p2_nb2 prints a computed verdict; p2_nb5 is
  labelled a static illustration; hz_nb3 converts its z = 0 anchors and drops the withheld dwarf
  median; the IntZ corpus metadata no longer reports withdrawn omega statistics as current; dw24
  uses the observed-only dwarf omega v1.1 table; the dw21 RMSE diagnostic is withdrawn; dw07 selects
  VLA-ANGST correctly; the High-Z notebooks build their flat CSV from the JSON when it is absent.

### Known open items (not resolved by this release)

1. **Paper 2 notebooks (`examples/paper2`) are frozen pending the author's audit.** p2_nb2: the
   published headline (78/84 improved, 0 regressions) is not reproduced from the embedded table
   (56/84, 1 regression). p2_nb5: the mass-quartile values are static and their provenance is
   unverified. The published outer gap (−51.4 ± 25.0 km/s) is not reproduced by any convention
   tested; p2_nb4 and hs_b_05 keep a ÷ 1.0227 step pending that audit. p2_nb6 fails with a
   NameError. p2_nb1–nb4 still label published omega as rad/Gyr. None of these notebooks should be
   cited as reproducing Paper 2.
2. **The HI FAISS retrieval text is historical.** `faiss/v7_sparc_texts.json` (and its copy under
   `build_scripts/faiss_legacy_texts/`) still carries superseded wording: the "thermal pressure"
   explanation of negative SPARC gas velocities (175 entries) and older WALLABY statements on
   uncertainties, distances (H0 = 75) and geometry. Mentions of 3DBarolo in the WALLABY text are not
   themselves wrong: the WKAPP models combine FAT and 3DBarolo fits (Deg et al. 2022). Commit 9734a42
   repaired the index identities and the GC, IntZ and Z1 texts, not the HI scientific text. A
   rebuild from the v7.3 records will follow as a separate release.
3. **IntZ omega is withdrawn.** The repository's `corpus_metadata` reports no current omega result;
   the former statistics are kept under `omega_legacy_withdrawn`. The Zenodo deposit
   (10.5281/zenodo.21841382) still carries the old summary metadata and 166 `rag_summary` strings
   stating the old omega values, so the repository and deposited texts differ.
4. **Dwarf omega v1.1 is per-galaxy eligibility output, not population validation.** The corrected
   dwarf v1.1 workflows report per-galaxy eligibility values only and withhold population summaries.
   Historical comparisons remain in High-Z nb1 (markdown), nb8 and nb25, including uncorrected
   local-reference units and, in nb1 and nb25, the old dwarf median. Those comparisons are not
   validated current results and must not be cited as such; their correction is pending. The hz_nb3
   comparison was corrected in this release. Its DDO154 anchor (Flynn 2026, arXiv:2605.22163v1,
   Figure 1) is omitted because the reported rad/Gyr value uses a legacy conversion and has not been
   revalidated; the value itself has a documented source.
5. **GC v1.4.0:** the build reproduces from the committed scripts and its arithmetic and census were
   checked; this is not an independent re-audit of every source measurement.
6. **The MCP server's live deployment** has not yet been updated or tested against this release.
