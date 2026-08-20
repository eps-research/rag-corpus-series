# HANDOFF — FAIR² submission repair, session state as of 2026-08-20 (session 3)

**Owner:** David Flynn, EPS Research (ORCID 0000-0002-2768-6650)
**Target:** FAIR² Data Article, *Frontiers in Astronomy and Space Sciences*
**Repo:** `eps-research/rag-corpus-series` @ `~/Documents/Astrophysics/rag-corpus-series`
**Branch:** `fair2-gc-v140-repair`
**Manuscript:** `fair2_platform_paper_v9.tex`, 844 lines, bibliography fully inline

**Supersedes** `HANDOFF_2026-08-17_session2.md` in full, and through it
`HANDOFF_2026-08-17_session_state.md`. Corrections are in §1 and are not
optional: the session-2 document states a record arithmetic that is wrong, and
the original document sends Sol to two commits that do not contain what it says
they contain.

**Workstream B is CLOSED.** The deposited build chain now regenerates the
deposited corpus end to end — 174 records, zero numeric differences across every
block. That claim has never previously been true.

---

## 1. Corrections to the prior handoff

**1.1 §8.1 Z1 attribution is wrong.** The prior handoff states that commits
`9fd278f` and `67ae85e` "both touch a Z1 omega correction." Neither touches the
Z1 corpus at all:

- `9fd278f` — regenerates `examples/highz/fig_hz_nb3_eps_omega_bridge.png` (1 file, binary)
- `67ae85e` — `download_corpora.py` + `examples/highz/build_hz_examples_04_25.py` (2 files, 7 lines)

`git log --all -- '*high_z_kinematic_corpus_Z1*'` returns only `a4d12b4`,
`78d895a`, `83c9005`. The omega correction was an **uncommitted working-tree
edit** with no commit behind it until this session.

**1.2 B's acceptance criterion was restated and is now met.** "Byte-identical
regeneration of v1.4.0" was unmeetable — `01_build_harris.py` emits 157 clusters
with Harris blocks only; the 17 extra records and the gaia/baumgardt/apogee
blocks come from stages 02–04. The criterion became: reproduce the
Harris-derived fields of v1.4.0 exactly, for all 157 Harris-covered clusters.
**Met, 6437/6437 values, zero differences.**

**1.3 "P2 shift: 5 records" was scoped too narrowly.** That count covered only
the blank-`feh` manifestation. The census shows the colour block shifting far
more widely: `vr` 20, `vi` 17, `ub` 10, `bv` 9. Use census numbers in the
manuscript, not the earlier scoping.

**1.4 The 157 + 12 + 5 arithmetic in session 2 §7 was wrong.** Stage 03 appends
**nothing**. Its five named clusters — Gran 2, Gran 3, Gran 5, Patchick 126,
VVV-CL160 — are absent from the parsed orbit and structure tables under those
exact names, so `if not o and not s: continue` skips all five. Verified from a
live run: no "Appended new cluster" line is emitted and the record count is
unchanged from v1.1 to v1.2. The correct arithmetic is **157 Harris + 17
Vasiliev-only = 174**, all 17 entering at stage 02.

**1.5 The deposited build scripts could never have produced the deposited
corpus.** `ID_MAP` in `02_merge_vasiliev.py` was missing two entries,
`"NGC 1904 (M 79)"` and `"BH 261 (ESO 456-78)"`. Without them those two V21 rows
fail to resolve, fall through to `v21_only`, and are appended as *new* clusters
alongside the Harris records of the same objects — producing 176 records with
duplicate NGC 1904 and BH 261, and null Gaia blocks on the Harris originals.
`ID_MAP` already contains 46 entries following exactly this pattern, including
`"NGC 6171 (M 107)"` twice, so the omission is transcription loss rather than
design. Whatever generated v1.3.x had a more complete map than what shipped in
`build_scripts_v1.3.2.zip`. **Same class as the Messier-name repair: an artifact
in the deposit that no deposited code accounts for.** Fixed in commit `b808474`.

**1.6 A is complete.** `examples/gc/harris_gc_corpus_v1.4.0.json` /`.jsonl`
exist, alongside `gc_v133_prior_audit.json` and `gc_v140_change_manifest.json` —
the sidecar decision went in as recommended. **All still untracked.** E is
unblocked.

---

## 2. Workstream B — COMPLETE

Stage 1 at `689c900`, stages 02-04 at `b808474`.

### 2.1 What shipped (stage 1)

| path | role |
|---|---|
| `build_scripts/01_build_harris.py` | rewritten generator, offset-parsed |
| `build_scripts/extract_harris_tables.py` | one-time migration; provenance record |
| `build_scripts/verify_01_gate.py` | independent two-gate acceptance test |
| `build_scripts/test_synthetic.py` | fixture test, no real data required |
| `harris_tables/mwgc_p{1,2,3}.dat` | catalogue snapshot, 157 rows each |
| `harris_tables/SHA256SUMS` | verified before every build |
| `harris_tables/SOURCE.txt` | origin, citation, parsing constraint |
| `audit/gc_defect_census_v133.txt` | the defect census (see §3) |

**`build_scripts/` did not previously exist in the repo.** `ls -d build_scripts*
scripts` returned nothing. The pipeline the paper cites as its reproducibility
artifact existed only inside `build_scripts_v1.3.2.zip` on Zenodo. That absence
is why four sessions audited outputs while the cause stayed invisible.

**Still missing:** `harris_tables/README.md` — drafted this session, never
downloaded, never committed. Recreate or re-request.

### 2.2 Gate results (stage 1)

```
GATE 1  parse vs harris_reparsed_v14.json
  P1: 157 × 10 = 1570 values, all exact
  P2: 157 × 13 = 2041 values, all exact
  P3: 157 × 13 = 2041 values, all exact          → 5652 total, PASS

GATE 2  derived fields vs harris_gc_corpus_v1.4.0.json
  6437 values across 157 clusters × 41 fields
  records differing: 0                            → PASS
```

Gate 2 was verified to *fail* on injected defects before being trusted. The
synthetic fixture also confirms `OffsetError` fires on a widened span and on the
historical flag-as-numeric error, and that a tampered `.dat` is refused.

`--report-arith`: **0** derived radii differ between `(a·b·π)/10800` and
`(a·b)·(π/10800)`. The float-grouping concern is measured, not assumed.

### 2.3 Design decisions taken (stage 1)

- **Tables externalised, not embedded.** The generator refuses to run if
  `SHA256SUMS` fails. Rationale: with the tables inside a Python string literal
  the snapshot could not be checksummed or diffed against McMaster, and no
  reader could place a raw row beside the value it produced. That opacity is why
  the defect survived three deposits.
- **`OffsetError` on cast failure**, never silent `None`.
- **Overflow guard**: a row longer than the declared span raises rather than
  silently ignoring an unread column.
- **Roster guard**: the set of ids recovered by offset must equal `P1_IDS` in all
  three parts. The original substituted `{}` for any miss.
- **`K` form adopted** to match `rebuild_gc_corpus_v140_p2.py`, which defines
  v1.4.0.
- **Stage 1 still stamps `version: "1.0"`** and writes `harris_gc_corpus_v1.json`.
  Stage 02 overwrites the version field unconditionally, so 01's stamp never
  reaches the final product; each stage stays diffable against its historical
  counterpart. **The terminal stamp must become 1.4.0 at stage 04.**

### 2.4 Stages 02-04 — COMPLETE, committed `b808474`

De-sandboxed **mechanically**, not rewritten. An elided read of the source hides
the `metadata["description"]` and `schema_notes` subscript assignments (02 lines
423-431, 03 lines 593-604, 04 lines 190-198 and 206-215); a from-scratch rewrite
would have silently dropped ~40 lines of metadata prose. `desandbox_merge_scripts.py`
instead transforms the originals in place, so everything not explicitly targeted
passes through by construction.

What it does: extracts each `RAW_*` to `catalogs/*.tsv` under a SHA-256 manifest,
replaces the assignment with a verifying loader, and rewrites every
`/mnt/user-data/outputs/NAME` literal to `OUT + 'NAME'` driven by `--dir`.
Declared column geometry is enforced, replacing guards that dropped short rows in
silence. Merge logic untouched.

| table | rows | columns |
|---|---|---|
| `vasiliev2021_table_a1.tsv` | 170 | 12 |
| `baumgardt2023_orbits.tsv` | 154 | 32 |
| `baumgardt2023_structure.tsv` | 154 | 34, 35 (ragged) |
| `schiavon2024_table1.tsv` | 72 | 11 |

**The silent-drop question is closed by measurement.** Zero rows dropped across
all four tables; zero ID collisions. All four are parsed with `line.split('\t')`,
which *preserves* empty columns — `'a\t\tb'.split('\t')` gives `['a','','b')`
where bare `.split()` gives `['a','b']`. **Stages 02-04 therefore do not carry the
column-shift defect of stage 01, as a structural guarantee rather than an
inference about placeholder conventions.**

`baumgardt2023_structure` is legitimately ragged: indices 32-34 (`a_rot_kms`,
`a_rot_err`, `p_rot_pct`) are rotation measurements present only where enough
radial velocities exist. Field alignment verified intact in every shape. This is
the documented tail-null limitation firing on genuine partial coverage rather
than a shift — the §4 caveat, with a worked instance.

### 2.5 End-to-end verification

```
chain: 174   v1.4.0: 174
only in chain : []          only in v1.4.0: []
non-Harris field differences: none
```

Zero numeric disagreements across all 174 records and every block. The four
residual differences are annotation and one derivation:

| path | n | nature |
|---|---|---|
| `distances.frame` | 26 | v1.3.3 audit annotation |
| `distances.frame_note` | 26 | v1.3.3 audit annotation |
| `distances.provenance_note` | 14 | v1.3.3 audit annotation |
| `position.l_deg` / `b_deg` | 17 | derivable, see §2.6 |

The 26 carrying frame annotations are **the same 26** the census flags for
`ra_hms` — the rebuild wrote frame notes onto precisely the records the
undocumented Messier repair had touched. Third independent confirmation that
this set is real and consistently identifiable.

### 2.6 l_deg / b_deg for the 17 Vasiliev-only records — resolved

v1.4.0 carries galactic coordinates for these; the chain leaves them `None`.
Tested against a standard IAU 1958 equatorial-to-galactic transform of
Vasiliev's own `ra_deg`/`dec_deg`:

```
BH 140     computed 303.171  -4.306   v1.4.0 303.171  -4.307   |Δ| < 0.001
Crater     computed 274.807  47.848   v1.4.0 274.809  47.848   |Δ| < 0.002
FSR 1758   computed 349.217  -3.292   v1.4.0 349.217  -3.292   |Δ| < 0.001
```

Residuals are rounding. **The values are correct and derivable** — they were
simply computed by code outside the deposit. Not a data-integrity problem; three
missing lines. Recommend adding the transform to stage 02, which closes the last
functional gap and makes those 17 records self-consistent (they currently hold
RA/Dec in `gaia_edr3` and nulls in `position`).

### 2.7 Open items in B — small, all deliberate edits

1. **Add the l/b transform to stage 02** (§2.6).
2. **The three annotation fields are now false.** `distances.provenance_note` on
   14 records states those distances are Baumgardt-sourced, "NOT Harris 1996."
   Under the corrected chain they *are* Harris — the values reproduce exactly
   from the offset parse. `frame_note` on 26 says values were "regenerated in
   v1.3.3." Both describe repairs the corrected pipeline no longer performs.
   Options: strip (clean, loses the audit trail), rewrite in the past tense
   (recommended — the information is valuable, the tense is wrong), or leave and
   explain in §4. **David's call.**
3. **04 still stamps version `"1.3"`.** Terminal stamp; must become `1.4.0` by
   deliberate edit.
4. **Tighten `baumgardt2023_structure` to 34..35.** The 32-column row was an
   artifact of `.strip()` removing trailing tabs from the last catalogue row, not
   a property of the data.

### 2.8 Four oddities documented, deliberately not fixed

Changing any of these changes output and would break the reproduce-v1.4.0 gate.
They belong in §4 as observations:

- `03` line 515 merges orbits and structure via `{**EMPTY_B, **o, **s}`. Both
  carry `r_sun_kpc`, `r_gc_kpc` and their errors, so structure silently wins
  wherever they disagree, with no note that a precedence rule exists.
- `inner_galaxy` has two provenances: `01` computes it from Harris `r_gc_kpc`,
  `03` line 558 from Baumgardt's. Same field, different source depending on which
  stage created the record. Both carry the `r_gc == 0.0 → False` truthiness bug.
- `02` line 378 sets `sgr_stream` from `{"NGC 2419", "Ko 1"}` — a different set
  from `01`'s six members, and since both are Harris clusters the expression is
  always `False`. Dead code encoding a contested claim.
- `02` line 344 assigns `c["gaia_edr3"] = None` then immediately overwrites it,
  commented `# not None — explicit null block is cleaner`.

## 3. The defect census — `audit/gc_defect_census_v133.txt`

Mechanically produced: 6437 comparisons between the raw catalogue and shipped
v1.3.3, no human assertion anywhere in it. **This is the attachment for the PASP
correction and the evidence base for §4.**

**127 records differ** — the same 127 the rebuild dry run reported, from an
implementation sharing no code with it. Two independent routes to the same set.

```
structure.r_core_kpc            114     distances.r_sun_kpc              22
structure.r_half_kpc            113     photometry.colors.vr             20
structure.r_core_arcmin          94     photometry.colors.vi             17
kinematics.sig_v_kms             93     photometry.ellipticity           15
structure.king_concentration     93     kinematics.v_r_kms               14
structure.r_half_arcmin          93     kinematics.v_r_err               14
dynamics.log_t_rh_yr             93     kinematics.v_lsr_kms             13
kinematics.sig_v_err             86     photometry.colors.ub             10
structure.mu_v_central           81     photometry.colors.bv              9
structure.log_rho0               81     flags.inner_galaxy                7
dynamics.log_t_rc_yr             81     photometry.v_hb / dist_mod / v_t  5
distances.x_kpc                  27     alt_name / feh / ebv / m_v_t      3
position.ra_hms                  26     position.l_deg                    2
distances.y_kpc                  26     metallicity.feh_weight            1
position.dec_dms                 25     position.b_deg                    1
distances.r_gc_kpc               24
distances.z_kpc                  24
```

### 3.1 Three findings new this session

**(a) The derived radii are the largest category — and exceed their own
parents.** `r_core_kpc` at 114 against `r_core_arcmin` at 94. Roughly twenty
records have a *correct* arcmin value and a *wrong* kpc value. NGC 104 is the
worked example:

```
r_core_arcmin = 0.36  (correct in v1.3.3)
r_half_arcmin = 3.17  (correct in v1.3.3)
old parse read r_sun_kpc = 305.89   ← the galactic longitude

0.36 × 305.89 × π/10800 = 0.0320    ← v1.3.3 ships 0.032
3.17 × 305.89 × π/10800 = 0.2821    ← v1.3.3 ships 0.2821
```

The distance patch repaired `r_sun_kpc` and never recomputed the two fields that
consume it. 47 Tuc's half-light radius shipped **68× too large** (0.2821 kpc
against the correct 0.0041 kpc = 4.1 pc), with every input visible in the record
reading correctly. This is method lesson 3 with arithmetic proof attached and is
a far better §4 paragraph than the abstract statement.

**(b) `flags.inner_galaxy` is wrong on 7 records, and it is a queryable
boolean.** NGC 104 is flagged `True` because its corrupted `r_gc_kpc` was −44.89
and −44.89 < 3.0. NGC 6266 and NGC 6273 — genuine bulge clusters — are flagged
`False`. The corpus both admits a halo cluster to the inner-galaxy set on a
negative distance and excludes real members. **arXiv:2605.03099 §3.5 makes a
commitment about this specific field**, so it belongs in the PASP note
explicitly, not folded into a general "structure fields affected" statement.
Note also: no negative `r_gc_kpc` survive in v1.3.3 — the patch fixed the
distance and left the flag.

**(c) An undocumented Messier-name repair.** `alt_name` differs on only 3
records while `ra_hms` differs on 26. v1.3.3 contains 29 alt_names beginning
"M" and **zero** bare `'M'` — so `'M 79'` is intact while `ra_hms` still reads
`'79:05:24'`. Something repaired the truncated names and never touched the
coordinates they leaked into. **No script in the deposited chain does this.**
The three survivors say why it missed them: `'47 Tuc'` (consumed entirely →
`None`), `'Pismis'`, `'Terzan'` — the three non-Messier cases. The repair was
Messier-shaped, so it fixed 26 symptoms and left the mechanism running.
**Provenance gap: an unattributed edit to a corpus the paper cites.** Method
lesson 4, second occurrence.

---

## 4. Workstream C — Z1 resolved, committed `ed8fade`

### 4.1 What the divergence actually was

Both copies now hash identically (`d62249a781e1`), but **by symlink, not by
merge**: `high_z_kinematic_corpus_Z1.json` at repo root is a symlink into
`examples/highz/`, created 02:42 today when `download_corpora.py` ran. The
edited downloader replaces the copy with a link for `highz` only.

The real change against HEAD: **`omega` on 8 of 31 galaxies, `null` →
populated**. No ids added or removed, no other field touched.

```
CG32 13.776   DC396844 2.899   DC494057 11.467   DC552206 26.059
DC881725 1.544   HZ9 40.707   J0817 39.240   VC5110377875 9.098   (rad/Gyr)
```

All `boundary_ring` quality, all `Flynn_Cannaliato_2025_Eq6`, all dated
2026-08-07, each carrying a `correction_note`. **Additions, not revisions** — no
previously published value is displaced.

`metadata.corrections` and `last_updated` were added this session; previously the
correction was discoverable only by walking all 31 records, meaning the FAISS
index and MCP server would return eight omega values the corpus metadata did not
acknowledge. `.json` and `.jsonl` verified equivalent.

### 4.2 Still open for Sol

**The symlink will not survive deposit.** Zenodo zips and Windows extraction
both break symlinks; a reader gets a dangling link or an empty file. It also
means `download_corpora.py` mutates a *tracked* file at runtime, so anyone who
runs it sees the root Z1 as modified — the churn that produced the divergence in
the first place. Needs either one real file with the root path removed and
notebooks repointed, or a copy plus a byte-equality assertion in the loader.

Unchanged from the prior handoff: notebooks pin v1.3.2; `v7_sparc` index
resolves 424 of 438; intz index carries 706 bare row-number IDs; MCP route merge.

---

## 5. `.gitignore` and repository hygiene

The blanket `*.json` / `*.jsonl` rule is now negated under `examples/`, plus
`*.bak`, `*.bak[0-9]`, `*.orig` excluded. Committed with `ed8fade`.

**Do not bulk-add the untracked set.** It currently contains:

- `harris_gc_corpus_v1.3.3.json.bak`, `.bak2`, `.jsonl.bak` — patch scaffolding,
  now gitignored
- `dwarf_irregular_corpus_v1.json` duplicated into `examples/gc/`, `hi/`,
  `highz/`, `intz/`, `highschool/`
- `rotation_curve_corpus_v7.json` duplicated into `examples/dwarfs/`, `gc/`,
  `highz/`, `intz/`
- `harris_gc_corpus_v1.3.2.*` in `examples/gc/` and `examples/highschool/`
- `rotmod_data/`, `sparc_figures_output/`, `sparc_v8_figures.py`
- `json,math` — a shell typo, removed

**Must be tracked before deposit:** `examples/gc/harris_gc_corpus_v1.4.0.json`,
`.jsonl`, `gc_v133_prior_audit.json`, `gc_v140_change_manifest.json`.

Decide the duplicate-corpus policy before adding anything — committing that set
as-is makes the sprawl permanent.

---

## 6. E — publication record. Now the critical path.

Unchanged from the prior handoff, **plus one new item with teeth**:

**6.1 `download_corpora.py` fetches v1.3.1.** Lines 42–46 and 78:

```python
'name': 'Milky Way Globular Cluster Corpus v1.3.1',
'doi':  '10.5281/zenodo.19907766',
('https://zenodo.org/records/19907766/files/harris_gc_corpus_v1.3.1.jsonl', ...)
('gc', 'harris_gc_corpus_v1.3.1.jsonl', '.')
```

This is the golden path a reviewer follows, and it hands them **the most
defective generation in the series** — v1.3.1 predates both l/b patches and the
distance repair. Meanwhile v1.4.0 sits corrected and untracked in `examples/gc/`.
The entry is also inconsistent with its own target: record 21093446 describes
itself as v1.3.1 throughout while shipping v1.3.2 files.

The `intz` and `highz` entries both carry inline comments naming their correction
and date. The GC entry carries none. **Blocked on the v1.4.0 deposit, but it must
change in the same pass** — otherwise the corrected corpus is unreachable by the
documented route.

**6.2 The DOI decision (still open).** Recommendation: **concept DOI
`10.5281/zenodo.19907765`** in both manuscript and fetcher. A concept DOI
resolves to the latest version, so a reader running the script after the next
correction gets the corrected corpus rather than a pin to whatever was current at
press time — pinning to a version DOI is precisely how the fetcher ended up three
generations behind. Counter-argument: two readers a year apart may get different
bytes. Resolution: cite the concept DOI for retrieval, record the version DOI
plus a checksum in corpus metadata, so what you *got* is verifiable even though
what you *fetch* moves forward — the same contract `harris_tables/SHA256SUMS`
establishes for the source catalogue. **40 references across 33 files hang on
this; David's call.**

Remaining E items unchanged: replacement arXiv version + note to editor (referees
do not yet have v2, so this is not an erratum); correct Zenodo 21093446's
self-description; deposit v1.4.0 with the corrected build chain and
`harris_tables/` attached.

---

## 7. F — manuscript v10. Additions to the prior edit list.

The prior handoff's §9 list still applies. Add:

- **The derived-radius finding (§3.1a)** — NGC 104 worked example, 68× error,
  correct inputs. Best available demonstration of build-time derivative
  inheritance.
- **`flags.inner_galaxy`, 7 records** — name it explicitly against the
  arXiv §3.5 commitment.
- **The undocumented Messier repair (§3.1c)** — a provenance gap the submission
  should acknowledge rather than paper over.
- **Census counts replace earlier scoped counts** for the P2 colour block.
- **`harris_tables/` + `SHA256SUMS`** — the concrete answer to the reviewer's
  §7 provenance challenge. Apply the same treatment to the SPARC/CWRU row.
- **`flags.sgr_stream` is an uncited editorial assertion** — six hardcoded
  members, no reference in script or metadata. Parse-independent, so not
  defective, but it needs a citation before deposit. Flagged in the rewritten
  generator's `schema_notes`.
- **Sagittarius II knowingly omitted** (03_merge_baumgardt line 534) — belongs in
  the coverage statement.
- **The 17 non-Harris records** all enter at stage 02 from Vasiliev. Stage 03
  appends nothing (§1.4). **157 + 17 = 174.** Now covered by the end-to-end
  verification in §2.5, not an open gap.
- **The build chain never reproduced the corpus** until this session (§1.5). The
  §4 reproducibility claim was, until commit `b808474`, false as written.
- **Stages 02-04 are shift-free by construction**, not by luck — `split('\t')`
  preserves empty columns. Worth one sentence, since §4 otherwise leaves the
  reader wondering whether the other three stages were ever checked.

---

## 8. Method lessons — additions

The prior handoff's seven stand. Add:

8. **A lookup that returns nothing will be read as a result.** This session I
   keyed 31 Z1 records on `id`/`name` — neither field exists; the corpus uses
   `galaxy` — so all 31 collapsed to a single `None` key and I reported "one
   record, one field changed" from a dict of size one. The truth was eight
   records. Same class as the `.split()` defect: a silent degradation producing a
   plausible-looking answer. This is why the corrected parser raises
   `OffsetError` instead of returning `None`, and why the corrected comparison
   asserts key uniqueness before comparing.
9. **Two independent implementations agreeing is evidence; one artifact agreeing
   with itself is not.** The census (157 records, offset parse) and the rebuild
   dry run (174 records, different code path) both reported 127 modified. That is
   worth more than four documents agreeing because they all read one stale Zenodo
   record.
10. **Ask what the repaired field feeds, then check whether anyone recomputed
    it.** `r_sun_kpc` was repaired; `r_core_kpc`, `r_half_kpc` and
    `inner_galaxy` consume it and were not. Twice now — the same omission in the
    distance patch and the Messier-name repair.

---

## 9. Open decisions

1. **DOI: concept `19907765` vs new v1.4.0 version DOI.** §6.2. Blocks the
   manuscript, the fetcher, and 40 references in 33 files.
2. **Duplicate-corpus policy** before anything untracked is added. §5.
3. **Z1 root path for deposit** — symlink cannot ship. §4.2. Sol's, since
   QuickStart is his.
4. **Stage version stamps** — keep the historical 1.0/1.1/1.2 ladder with the
   terminal stamp corrected at 04, or make every stage honest. Currently the
   former; one-line change in four files if you prefer the latter.
5. **Extension** — reply from Joshua Stocco still pending.

---

## 10. Immediate next actions

| # | action | owner | blocks |
|---|---|---|---|
| 1 | l/b transform in 02; annotation-tense decision; 04 stamp; column range | Claude | deposit |
| 2 | Deposit v1.4.0 + build chain + `harris_tables/` + `catalogs/` | David | F, PASP |
| 3 | Update `download_corpora.py` in the same pass as the deposit | David | reviewer path |
| 4 | PASP correction with `gc_defect_census_v133.txt` attached | David | **deadline** |
| 5 | Correct §8.1 in Sol's brief before he starts C | David | C |
| 6 | Manuscript v10 | Claude | after 2 |

---

## 11. Commits, full session

```
689c900  Corrected stage-1 Harris generator, catalogue snapshot, defect census
ed8fade  Z1: omega corrections in metadata; enable corpus tracking
13ec352  Session-2 handoff and harris_tables README
b808474  De-sandbox merge stages 02-04; full chain reproduces v1.4.0
d69d5f8  Track corpus v1.4.0 and audit sidecars
```

Branch `fair2-gc-v140-repair`, pushed to `origin`.
