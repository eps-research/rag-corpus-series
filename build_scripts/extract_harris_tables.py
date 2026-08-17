#!/usr/bin/env python3
"""
extract_harris_tables.py -- one-time migration.

Lifts the three Harris (1996, 2010 edition) catalogue parts out of the RAW dict
literal embedded in the original 01_build_harris.py and writes them as plain
fixed-width .dat files with a SHA-256 manifest.

Rationale: with the tables embedded in the generator, the catalogue snapshot
could not be checksummed, diffed against the McMaster source, or inspected
without first writing a script to dig it back out of a Python string literal.
That opacity is why a column-shift defect survived three Zenodo deposits.
Once externalised, provenance is one `sha256sum -c` away.

This script is provenance documentation for the deposit. It is NOT part of the
build chain and should not need to be run again.

Usage:
    python3 extract_harris_tables.py \
        --src ~/Downloads/build_scripts_v1.3.2/01_build_harris.py \
        --out harris_tables

Writes:  harris_tables/mwgc_p1.dat
         harris_tables/mwgc_p2.dat
         harris_tables/mwgc_p3.dat
         harris_tables/SHA256SUMS
         harris_tables/SOURCE.txt
"""

import argparse
import ast
import hashlib
import sys
from pathlib import Path

EXPECT_ROWS = 157

SOURCE_TXT = """\
Harris, W.E. 1996, AJ, 112, 1487 -- 2010 edition
https://physics.mcmaster.ca/~harris/mwgc.dat

mwgc_p1.dat  Part I   identifications, positions, distances   (157 rows)
mwgc_p2.dat  Part II  metallicity and photometry              (157 rows)
mwgc_p3.dat  Part III velocities and structural parameters    (157 rows)

Strict fixed-width, right-aligned numerics, blank columns for missing values.
Column offsets are declared in 01_build_harris.py (P1_SPEC / P2_SPEC / P3_SPEC)
and must not be inferred by whitespace splitting: Harris leaves a column blank
rather than writing a placeholder, so any token-based parse silently shifts
every field to the right of a blank one position left.

These files were extracted verbatim from the RAW dict literal embedded in the
original 01_build_harris.py (deposited as build_scripts_v1.3.2.zip) by
extract_harris_tables.py. Content is byte-identical to that literal apart from
normalisation of leading/trailing blank lines and a terminating newline.
"""


def extract_raw(src):
    """Return the {p1,p2,p3} dict from the source, or exit."""
    tree = ast.parse(Path(src).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            try:
                d = ast.literal_eval(node.value)
            except Exception:
                continue
            if isinstance(d, dict) and {"p1", "p2", "p3"} <= set(d):
                return d
    sys.exit("ERROR: no dict literal with keys p1/p2/p3 found in " + str(src))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True,
                    help="original 01_build_harris.py containing the RAW dict")
    ap.add_argument("--out", default="harris_tables")
    args = ap.parse_args()

    raw = extract_raw(args.src)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    sums = []
    for key in ("p1", "p2", "p3"):
        text = raw[key].strip("\n") + "\n"
        lines = [ln for ln in text.splitlines() if ln.strip()]
        if len(lines) != EXPECT_ROWS:
            sys.exit(f"ERROR: {key} has {len(lines)} non-blank rows, "
                     f"expected {EXPECT_ROWS}")

        path = out / f"mwgc_{key}.dat"
        path.write_text(text, encoding="utf-8")

        # read back and prove byte-equality with what we intended to write
        back = path.read_text(encoding="utf-8")
        if back != text:
            sys.exit(f"ERROR: {path} did not round-trip")
        if [ln for ln in back.splitlines() if ln.strip()] != lines:
            sys.exit(f"ERROR: {path} row content changed on round-trip")

        digest = sha256(path)
        sums.append((digest, path.name))
        width = max(len(ln.rstrip()) for ln in lines)
        print(f"{path}  rows={len(lines)}  max_width={width}  sha256={digest[:16]}...")

    (out / "SHA256SUMS").write_text(
        "".join(f"{d}  {n}\n" for d, n in sums), encoding="utf-8")
    (out / "SOURCE.txt").write_text(SOURCE_TXT, encoding="utf-8")

    print(f"\nWrote {out}/SHA256SUMS and {out}/SOURCE.txt")
    print(f"Verify any time with:  cd {out} && sha256sum -c SHA256SUMS")


if __name__ == "__main__":
    main()
