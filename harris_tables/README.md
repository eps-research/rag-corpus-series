# harris_tables/ — Harris (1996, 2010 edition) catalogue snapshot

Fixed-width source tables for the Milky Way globular cluster corpus. Read by
`build_scripts/01_build_harris.py`; not edited by hand.

| file | contents | rows |
|---|---|---|
| `mwgc_p1.dat` | Part I — identifications, positions, distances | 157 |
| `mwgc_p2.dat` | Part II — metallicity and photometry | 157 |
| `mwgc_p3.dat` | Part III — velocities and structural parameters | 157 |
| `SHA256SUMS` | manifest, verified before every build | — |
| `SOURCE.txt` | origin, citation, and the parsing constraint | — |

Source: Harris, W.E. 1996, AJ, 112, 1487 (2010 revision),
<https://physics.mcmaster.ca/~harris/mwgc.dat>

## The checksum contract

`01_build_harris.py` verifies every table against `SHA256SUMS` before parsing and
exits if any digest disagrees. Verify independently at any time:

```bash
cd harris_tables && sha256sum -c SHA256SUMS
```

If a checksum fails, the build has stopped for a reason. Do not regenerate the
manifest to make it pass — establish first why the snapshot changed. Updating the
snapshot deliberately means re-running the manifest **and** re-running the full
acceptance gate, because the corpus is a function of these bytes.

## Why these are files and not a Python literal

Through v1.3.3 these tables lived as a dict literal inside the stage-1 generator.
That coupling is the reason a column-shift defect survived three Zenodo deposits,
a preprint and peer review: no reader could place a raw catalogue row beside the
parsed value it produced without first writing a script to extract the table from
a string literal, and the snapshot could not be checksummed or diffed against the
McMaster source at all.

Externalised, provenance is one command, and the parser can be audited separately
from the data it reads.

## Parsing constraint — the defect this directory exists to prevent

Harris is **strict fixed-width** and leaves a column **blank** for a missing value
rather than writing a placeholder. Whitespace tokenisation therefore deletes the
gap and shifts every field to the right of it one position left, silently and
into a dimensionally plausible slot.

Read every field by its declared character offset (`P1_SPEC` / `P2_SPEC` /
`P3_SPEC` in `build_scripts/01_build_harris.py`). A token that will not cast
raises `OffsetError` rather than degrading to `None`; silent `None` is the
failure mode that let the original defect hide.

Note in particular that Part III is **14 fields, not 13**. The core-collapse
marker occupies columns 54–58; omitting it shifts every field to its right by one
name while leaving all of them numerically castable.

## Provenance of the extraction

`build_scripts/extract_harris_tables.py` lifted these tables verbatim from the
`RAW` dict literal in the original `01_build_harris.py`, as deposited in
`build_scripts_v1.3.2.zip`. Content is byte-identical to that literal apart from
normalised leading/trailing blank lines and a terminating newline. The extractor
is one-time migration and provenance documentation; it is not part of the build
chain and should not need to run again.

## Verification status

Parsed by the current generator and checked field-by-field against the
authoritative offset re-parse: **157 clusters × 36 fields across the three parts,
5,652 values, all exact**. The resulting Harris-derived record fields match
corpus v1.4.0 on all **6,437** compared values, zero differences.
