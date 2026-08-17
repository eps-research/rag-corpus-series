# Harris Catalogue Snapshot

This directory contains the fixed-width Harris Milky Way globular-cluster
catalogue tables used by the Stage-1 generator for the corrected GC corpus
v1.4.0.

## Files

- `mwgc_p1.dat` — Harris catalogue Part I, 157 rows
- `mwgc_p2.dat` — Harris catalogue Part II, 157 rows
- `mwgc_p3.dat` — Harris catalogue Part III, 157 rows
- `SHA256SUMS` — integrity manifest for the three catalogue tables
- `SOURCE.txt` — source and provenance information

The files are retained as an immutable input snapshot so the corpus can be
rebuilt from the exact source bytes used during remediation.

## Integrity contract

Before parsing, the Stage-1 build process verifies the source files against
`SHA256SUMS`. A checksum mismatch is a build failure.

Manual verification:

    cd harris_tables
    sha256sum -c SHA256SUMS

## Parsing contract

`build_scripts/01_build_harris.py` parses the catalogue using declared
fixed-width character offsets. Blank fixed-width fields remain missing values.

The previous generator used whitespace tokenization (`split()`) on these
fixed-width tables. Missing values therefore collapsed columns and shifted
subsequent values into incorrect fields.

Supporting tools:

- `build_scripts/01_build_harris.py`
- `build_scripts/extract_harris_tables.py`
- `build_scripts/verify_01_gate.py`
- `build_scripts/test_synthetic.py`

## Validation status

- 5,652 parsed Harris values compared: 0 differences
- 6,437 Harris-derived corpus field values compared: 0 differences

The arithmetic-grouping diagnostic is recorded in
`audit/gc_defect_census_v133.txt`.

## Scope

The Harris catalogue contributes source fields to 157 clusters. The released
GC corpus contains 174 records total. The remaining 17 non-Harris records are
outside this Stage-1 parser gate and require separate validation.

See `SOURCE.txt` for source provenance and
`audit/gc_defect_census_v133.txt` for the defect census.
