#!/usr/bin/env python3
"""
EPS Research Astro-RAG Platform — Corpus Downloader

Downloads or validates the five EPS Research corpus silos using one
canonical repository location per corpus.

Canonical locations:
  HI     examples/hi/rotation_curve_corpus_v7.json
  Dwarf  examples/dwarfs/dwarf_irregular_corpus_v1.json
  GC     examples/gc/harris_gc_corpus_v1.4.0.json/.jsonl
  IntZ   examples/intz/intz_corpus_v1b.json/.jsonl
  Z1     examples/highz/high_z_kinematic_corpus_Z1.json

The corrected GC v1.4.0 corpus is bundled with the repository. It is not
downloaded from the obsolete v1.3.x Zenodo records. A Zenodo URL can be
added after the v1.4.0 deposit exists.

Usage:
    python download_corpora.py
    python download_corpora.py --corpus hi
    python download_corpora.py --corpus gc
    python download_corpora.py --force

Flynn, D.C. (2026) | github.com/eps-research/rag-corpus-series
"""

import argparse
import os
import sys
import urllib.request


CORPORA = {
    "hi": {
        "name": "Unified HI Rotation Curve Corpus v7.1",
        "doi": "10.5281/zenodo.19563417",
        "files": [
            (
                "https://zenodo.org/records/19563417/files/rotation_curve_corpus_v7.json",
                "rotation_curve_corpus_v7.json",
            ),
            (
                "https://zenodo.org/records/19563417/files/rotation_curve_corpus_v7.1_flat.csv",
                "rotation_curve_corpus_v7.1_flat.csv",
            ),
        ],
        "dest": "examples/hi",
        "bundled": False,
    },

    "dwarfs": {
        "name": "Dwarf/Irregular HI Corpus v1.0",
        "doi": "10.5281/zenodo.20320362",
        "files": [
            (
                "https://zenodo.org/records/20320362/files/dwarf_irregular_corpus_v1.json",
                "dwarf_irregular_corpus_v1.json",
            ),
            (
                "https://zenodo.org/records/20320362/files/dwarf_irregular_corpus_v1_flat.csv",
                "dwarf_irregular_corpus_v1_flat.csv",
            ),
        ],
        "dest": "examples/dwarfs",
        "bundled": False,
    },

    "gc": {
        "name": "Milky Way Globular Cluster Corpus v1.4.0",
        "doi": None,
        "files": [
            (None, "harris_gc_corpus_v1.4.0.json"),
            (None, "harris_gc_corpus_v1.4.0.jsonl"),
        ],
        "dest": "examples/gc",
        "bundled": True,
    },

    "intz": {
        "name": "EPS Research Intermediate-z Kinematic Corpus v1.0b",
        "doi": "10.5281/zenodo.21841382",
        "files": [
            (
                "https://zenodo.org/records/21841382/files/intz_corpus_v1b.json",
                "intz_corpus_v1b.json",
            ),
            (
                "https://zenodo.org/records/21841382/files/intz_corpus_v1b_flat.csv",
                "intz_corpus_v1b_flat.csv",
            ),
            (
                "https://zenodo.org/records/21841382/files/intz_corpus_v1b.jsonl",
                "intz_corpus_v1b.jsonl",
            ),
        ],
        "dest": "examples/intz",
        "bundled": False,
    },

    "highz": {
        "name": "High-z Kinematic Corpus Z1",
        "doi": "10.5281/zenodo.21834678",
        "files": [
            (
                "https://zenodo.org/records/21834678/files/high_z_kinematic_corpus_Z1.json",
                "high_z_kinematic_corpus_Z1.json",
            ),
        ],
        "dest": "examples/highz",
        "bundled": False,
    },
}


def download_file(url, dest_path, force=False):
    if os.path.exists(dest_path) and not force:
        print(f"  Already exists: {dest_path} (use --force to overwrite)")
        return True

    if os.path.exists(dest_path) and force:
        print(f"  Overwriting: {dest_path}")

    print(f"  Downloading {os.path.basename(dest_path)}...")

    try:
        urllib.request.urlretrieve(url, dest_path)
        size = os.path.getsize(dest_path) / 1024 / 1024
        print(f"  Done: {dest_path} ({size:.1f} MB)")
        return True
    except Exception as exc:
        print(f"  FAILED: {exc}")
        return False


def validate_bundled_corpus(key):
    corpus = CORPORA[key]

    print(f"\n{corpus['name']}")
    print("Source: repository-bundled corrected corpus")

    missing = []

    for _, filename in corpus["files"]:
        path = os.path.join(corpus["dest"], filename)

        if os.path.isfile(path):
            size = os.path.getsize(path) / 1024 / 1024
            print(f"  Present: {path} ({size:.1f} MB)")
        else:
            print(f"  MISSING: {path}")
            missing.append(path)

    if missing:
        print(
            "  ERROR: corrected GC v1.4.0 is expected to be present "
            "in the repository."
        )
        return False

    print("  Bundled corpus validation: PASS")
    return True


def download_corpus(key, force=False):
    corpus = CORPORA[key]

    if corpus.get("bundled"):
        return validate_bundled_corpus(key)

    print(f"\n{corpus['name']}")
    print(f"DOI: {corpus['doi']}")

    os.makedirs(corpus["dest"], exist_ok=True)

    ok = True

    for url, filename in corpus["files"]:
        dest = os.path.join(corpus["dest"], filename)

        if not download_file(url, dest, force=force):
            ok = False

    return ok


def main():
    parser = argparse.ArgumentParser(
        description="Download or validate the five EPS Research corpora"
    )

    parser.add_argument(
        "--corpus",
        choices=list(CORPORA.keys()) + ["all"],
        default="all",
        help="Which corpus to download or validate",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing downloadable corpus files",
    )

    # Retained for backward CLI compatibility. Root corpus copies are no
    # longer created; QuickStart now uses canonical examples/... paths.
    parser.add_argument(
        "--quickstart",
        action="store_true",
        help=argparse.SUPPRESS,
    )

    args = parser.parse_args()

    print("EPS Research Astro-RAG Platform — Corpus Downloader")
    print("=" * 55)
    print("Canonical-path mode: one authoritative repository path per corpus")

    keys = list(CORPORA) if args.corpus == "all" else [args.corpus]

    success = True

    for key in keys:
        if not download_corpus(key, force=args.force):
            success = False

    if args.quickstart:
        print(
            "\nNOTE: --quickstart no longer creates root corpus copies. "
            "QuickStart.ipynb reads canonical examples/... paths directly."
        )

    if success:
        print("\nDone. Canonical corpus availability: PASS")
        return 0

    print("\nOne or more corpus operations failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
