#!/usr/bin/env python3
"""
01_build_harris.py -- stage 1 of the MW globular cluster corpus build chain.

Parses the three Harris (1996, 2010 edition) catalogue parts into the unified
corpus schema and writes harris_gc_corpus_v1.json + a flat CSV. Stages 02-04
merge Gaia EDR3 (Vasiliev & Baumgardt 2021), Baumgardt et al. 2023 and APOGEE
DR17 on top of this output.

WHAT CHANGED, AND WHY
---------------------
The original stage-1 generator parsed all three parts with `.split()`. Harris
is strict fixed-width and leaves a column BLANK for a missing value rather than
writing a placeholder, so token-based parsing deletes the gap and shifts every
field to the right of it one position left. Consequences in v1.0-v1.3.3:

  * 93 of 157 records carried a King concentration parameter in
    kinematics.sig_v_kms, dimensionally plausible and therefore invisible;
  * 14 more carried a wider shift through the whole distances block;
  * 5 carried shifted photometry where [Fe/H] was blank;
  * 15 carried an ellipticity fabricated from a colour index, because the old
    parse read `tokens[-1]`;
  * 26 carried an alt_name token leaked into ra_hms/dec_dms, because the old
    parse ended the alt_name scan at the first two-digit token -- which is the
    Messier number in "M 79", the catalogue number in "Pismis 26", and the "47"
    in "47 Tuc". Seventeen of those had an impossible RA hour.

Every field is now read by explicit character offset. A token that will not
cast raises OffsetError rather than degrading to None: silent None is the
failure mode that let the original hide for three deposits.

The raw tables are no longer embedded in this file. They live in
harris_tables/*.dat with a SHA-256 manifest, verified before every run, so the
catalogue snapshot can be checksummed and diffed against the McMaster source
independently of the code that reads it. See extract_harris_tables.py.

Usage:
    python3 01_build_harris.py                        # defaults below
    python3 01_build_harris.py --tables harris_tables --out-dir build_out
    python3 01_build_harris.py --no-verify-manifest   # not recommended

Reference: Harris, W.E. 1996, AJ, 112, 1487 (2010 revision)
           https://physics.mcmaster.ca/~harris/mwgc.dat
"""

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Derived-field constants.
#
# K is written as pi/10800 in ONE grouping and used in ONE place. The original
# wrote `arcmin * r_sun * math.pi / (60*180)`, which groups as
# ((a*b)*pi)/10800 rather than (a*b)*(pi/10800). Float multiplication is not
# associative, so the two forms can differ in the last bit before rounding.
# rebuild_gc_corpus_v140_p2.py -- which produces the reference v1.4.0 -- uses
# the K form, so this does too. --report-arith quantifies the difference.
# --------------------------------------------------------------------------
K = math.pi / 10800.0
DP = 4
INNER_GALAXY_KPC = 3.0

# --------------------------------------------------------------------------
# Column offsets. THE single source of truth for this catalogue.
# (field, start, end, kind)  kind: s=string  f=float  i=int  flag=marker column
# P3 is 14 fields, not 13: the core-collapse marker occupies 54:58 and omitting
# it shifts every field to its right by one name.
# --------------------------------------------------------------------------
P1_SPEC = [("cluster_id", 0, 11, "s"), ("alt_name", 11, 24, "s"),
           ("ra_hms", 24, 36, "s"), ("dec_dms", 36, 48, "s"),
           ("l_deg", 48, 57, "f"), ("b_deg", 57, 65, "f"),
           ("r_sun_kpc", 65, 72, "f"), ("r_gc_kpc", 72, 78, "f"),
           ("x_kpc", 78, 84, "f"), ("y_kpc", 84, 90, "f"),
           ("z_kpc", 90, 96, "f")]

P2_SPEC = [("cluster_id", 0, 12, "s"), ("feh", 12, 17, "f"),
           ("feh_weight", 17, 20, "i"), ("ebv", 20, 27, "f"),
           ("v_hb", 27, 33, "f"), ("dist_mod", 33, 39, "f"),
           ("v_t", 39, 45, "f"), ("m_v_t", 45, 52, "f"),
           ("ub", 52, 59, "f"), ("bv", 59, 65, "f"),
           ("vr", 65, 71, "f"), ("vi", 71, 77, "f"),
           ("spectral_type", 77, 83, "s"), ("ellipticity", 83, 89, "f")]

P3_SPEC = [("cluster_id", 0, 12, "s"), ("v_r_kms", 12, 19, "f"),
           ("v_r_err", 19, 25, "f"), ("v_lsr_kms", 25, 33, "f"),
           ("sig_v_kms", 33, 41, "f"), ("sig_v_err", 41, 48, "f"),
           ("king_concentration", 48, 54, "f"),
           ("core_collapse_flag", 54, 58, "flag"),
           ("r_core_arcmin", 58, 64, "f"), ("r_half_arcmin", 64, 70, "f"),
           ("mu_v_central", 70, 78, "f"), ("log_rho0", 78, 85, "f"),
           ("log_t_rc_yr", 85, 92, "f"), ("log_t_rh_yr", 92, 98, "f")]

SPECS = {"p1": P1_SPEC, "p2": P2_SPEC, "p3": P3_SPEC}

# --------------------------------------------------------------------------
# Record order. Carried verbatim from the original generator: the corpus is
# ordered by this list, not by parse order, and v1.3.3 / v1.4.0 alignment
# depends on it. Also used as an integrity check -- the set of cluster_ids
# recovered by offset must equal this set exactly.
# --------------------------------------------------------------------------
P1_IDS = [
    'NGC 104', 'NGC 288', 'NGC 362', 'Whiting 1', 'NGC 1261', 'Pal 1', 'AM 1', 'Eridanus',
    'Pal 2', 'NGC 1851', 'NGC 1904', 'NGC 2298', 'NGC 2419', 'Ko 2', 'Pyxis', 'NGC 2808', 'E 3', 'Pal 3',
    'NGC 3201', 'Pal 4', 'Ko 1', 'NGC 4147', 'NGC 4372', 'Rup 106', 'NGC 4590', 'NGC 4833', 'NGC 5024',
    'NGC 5053', 'NGC 5139', 'NGC 5272', 'NGC 5286', 'AM 4', 'NGC 5466', 'NGC 5634', 'NGC 5694', 'IC 4499',
    'NGC 5824', 'Pal 5', 'NGC 5897', 'NGC 5904', 'NGC 5927', 'NGC 5946', 'BH 176', 'NGC 5986', 'Lynga 7',
    'Pal 14', 'NGC 6093', 'NGC 6121', 'NGC 6101', 'NGC 6144', 'NGC 6139', 'Terzan 3', 'NGC 6171',
    '1636-283', 'NGC 6205', 'NGC 6229', 'NGC 6218', 'FSR 1735', 'NGC 6235', 'NGC 6254', 'NGC 6256',
    'Pal 15', 'NGC 6266', 'NGC 6273', 'NGC 6284', 'NGC 6287', 'NGC 6293', 'NGC 6304', 'NGC 6316',
    'NGC 6341', 'NGC 6325', 'NGC 6333', 'NGC 6342', 'NGC 6356', 'NGC 6355', 'NGC 6352', 'IC 1257',
    'Terzan 2', 'NGC 6366', 'Terzan 4', 'HP 1', 'NGC 6362', 'Liller 1', 'NGC 6380', 'Terzan 1', 'Ton 2',
    'NGC 6388', 'NGC 6402', 'NGC 6401', 'NGC 6397', 'Pal 6', 'NGC 6426', 'Djorg 1', 'Terzan 5', 'NGC 6440',
    'NGC 6441', 'Terzan 6', 'NGC 6453', 'UKS 1', 'NGC 6496', 'Terzan 9', 'Djorg 2', 'NGC 6517', 'Terzan 10',
    'NGC 6522', 'NGC 6535', 'NGC 6528', 'NGC 6539', 'NGC 6540', 'NGC 6544', 'NGC 6541', '2MS-GC01',
    'ESO-SC06', 'NGC 6553', '2MS-GC02', 'NGC 6558', 'IC 1276', 'Terzan 12', 'NGC 6569', 'BH 261',
    'GLIMPSE02', 'NGC 6584', 'NGC 6624', 'NGC 6626', 'NGC 6638', 'NGC 6637', 'NGC 6642', 'NGC 6652',
    'NGC 6656', 'Pal 8', 'NGC 6681', 'GLIMPSE01', 'NGC 6712', 'NGC 6715', 'NGC 6717', 'NGC 6723',
    'NGC 6749', 'NGC 6752', 'NGC 6760', 'NGC 6779', 'Terzan 7', 'Pal 10', 'Arp 2', 'NGC 6809',
    'Terzan 8', 'Pal 11', 'NGC 6838', 'NGC 6864', 'NGC 6934', 'NGC 6981', 'NGC 7006', 'NGC 7078',
    'NGC 7089', 'NGC 7099', 'Pal 12', 'Pal 13', 'NGC 7492',
]

# Sagittarius dSph stream membership. NOTE: this is an editorial assertion
# inherited from the original generator with no citation attached. It is
# parse-independent and therefore unaffected by the column-shift defect, but it
# needs a reference before the next deposit. Flagged, not silently propagated.
SGR = {"NGC 6715", "Terzan 7", "Terzan 8", "Arp 2", "Pal 12", "Whiting 1"}

CSV_FIELDS = ["cluster_id", "alt_name", "ra_hms", "dec_dms", "l_deg", "b_deg",
              "r_sun_kpc", "r_gc_kpc", "x_kpc", "y_kpc", "z_kpc",
              "feh", "feh_weight", "ebv", "v_hb", "dist_mod", "v_t", "m_v_t",
              "spectral_type", "ellipticity", "bv", "vi",
              "v_r_kms", "v_r_err", "sig_v_kms",
              "king_concentration", "core_collapsed", "core_collapse_uncertain",
              "r_core_arcmin", "r_half_arcmin", "r_core_kpc", "r_half_kpc",
              "mu_v_central", "log_rho0", "log_t_rc_yr", "log_t_rh_yr",
              "inner_galaxy", "sgr_stream"]


class OffsetError(Exception):
    """A column span produced a token that will not cast. The map is wrong."""


def num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def cast(tok, kind, field, cid, lineno, block):
    if tok == "":
        return None
    if kind in ("s", "flag"):
        return tok
    try:
        return int(tok) if kind == "i" else float(tok)
    except ValueError:
        raise OffsetError(
            f"{block} line {lineno} ({cid or '?'}): field {field!r} span gave "
            f"{tok!r}, which is not {'an int' if kind == 'i' else 'a float'}. "
            f"The column map is wrong -- fix the offsets, do not coerce.")


def parse_block(text, spec, block):
    """Parse one fixed-width catalogue part into {cluster_id: {field: value}}."""
    width = spec[-1][2]
    out = {}
    for lineno, raw_line in enumerate(text.splitlines(), 1):
        if not raw_line.strip():
            continue
        line = raw_line.rstrip("\n")

        # A row longer than the declared span means a column we are not
        # reading. Under-length is normal: Harris right-trims blank tails.
        if len(line.rstrip()) > width:
            raise OffsetError(
                f"{block} line {lineno}: row is {len(line.rstrip())} chars but "
                f"the column map covers only {width}. There is an unread "
                f"column -- extend the spec rather than ignoring the overflow.")

        cid = line[spec[0][1]:spec[0][2]].strip()
        if not cid:
            raise OffsetError(f"{block} line {lineno}: empty cluster_id span")

        rec = {}
        for name, a, b, kind in spec[1:]:
            rec[name] = cast(line[a:b].strip(), kind, name, cid, lineno, block)
        if cid in out:
            raise OffsetError(f"{block} line {lineno}: duplicate id {cid!r}")
        out[cid] = rec
    return out


def load_tables(tables_dir, verify_manifest=True):
    d = Path(tables_dir)
    if verify_manifest:
        manifest = d / "SHA256SUMS"
        if not manifest.exists():
            sys.exit(f"ERROR: {manifest} missing. Run extract_harris_tables.py, "
                     f"or pass --no-verify-manifest if you accept unverified input.")
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            want, name = line.split(None, 1)
            path = d / name.strip()
            h = hashlib.sha256()
            with open(path, "rb") as fh:
                for chunk in iter(lambda: fh.read(65536), b""):
                    h.update(chunk)
            if h.hexdigest() != want:
                sys.exit(f"ERROR: checksum mismatch for {path}.\n"
                         f"  manifest {want}\n  actual   {h.hexdigest()}\n"
                         f"The catalogue snapshot has changed. Stop and find out why.")
        print(f"manifest  : {len(SPECS)} tables verified against SHA256SUMS")

    parsed = {}
    for block in ("p1", "p2", "p3"):
        path = d / f"mwgc_{block}.dat"
        if not path.exists():
            sys.exit(f"ERROR: {path} not found")
        parsed[block] = parse_block(
            path.read_text(encoding="utf-8"), SPECS[block], block.upper())
    return parsed


# --------------------------------------------------------------------------
# Record assembly
# --------------------------------------------------------------------------

def hms(raw):
    """Harris writes sexagesimal as space-separated; the corpus uses colons."""
    return ":".join(raw.split()) if isinstance(raw, str) and raw.strip() else None


def arcmin_to_kpc(arcmin, r_sun):
    if not (num(arcmin) and num(r_sun)):
        return None
    return round(arcmin * r_sun * K, DP)


def build_record(cid, d1, d2, d3):
    r_sun = d1.get("r_sun_kpc")
    r_gc = d1.get("r_gc_kpc")
    rc_am = d3.get("r_core_arcmin")
    rh_am = d3.get("r_half_arcmin")
    flag = (d3.get("core_collapse_flag") or "").strip()

    return {
        "cluster_id": cid,
        "alt_name": d1.get("alt_name"),
        "position": {"ra_hms": hms(d1.get("ra_hms")),
                     "dec_dms": hms(d1.get("dec_dms")),
                     "l_deg": d1.get("l_deg"), "b_deg": d1.get("b_deg")},
        "distances": {"r_sun_kpc": r_sun, "r_gc_kpc": r_gc,
                      "x_kpc": d1.get("x_kpc"), "y_kpc": d1.get("y_kpc"),
                      "z_kpc": d1.get("z_kpc")},
        "metallicity": {"feh": d2.get("feh"), "feh_weight": d2.get("feh_weight"),
                        "ebv": d2.get("ebv")},
        "photometry": {"v_hb": d2.get("v_hb"), "dist_mod": d2.get("dist_mod"),
                       "v_t": d2.get("v_t"), "m_v_t": d2.get("m_v_t"),
                       "spectral_type": d2.get("spectral_type"),
                       "ellipticity": d2.get("ellipticity"),
                       "colors": {"ub": d2.get("ub"), "bv": d2.get("bv"),
                                  "vr": d2.get("vr"), "vi": d2.get("vi")}},
        "kinematics": {"v_r_kms": d3.get("v_r_kms"), "v_r_err": d3.get("v_r_err"),
                       "v_lsr_kms": d3.get("v_lsr_kms"),
                       "sig_v_kms": d3.get("sig_v_kms"),
                       "sig_v_err": d3.get("sig_v_err")},
        "structure": {"king_concentration": d3.get("king_concentration"),
                      "core_collapsed": flag.startswith("c"),
                      "core_collapse_uncertain": flag == "c:",
                      "r_core_arcmin": rc_am, "r_half_arcmin": rh_am,
                      "r_core_kpc": arcmin_to_kpc(rc_am, r_sun),
                      "r_half_kpc": arcmin_to_kpc(rh_am, r_sun),
                      "mu_v_central": d3.get("mu_v_central"),
                      "log_rho0": d3.get("log_rho0")},
        "dynamics": {"log_t_rc_yr": d3.get("log_t_rc_yr"),
                     "log_t_rh_yr": d3.get("log_t_rh_yr")},
        "flags": {"inner_galaxy": bool(num(r_gc) and r_gc < INNER_GALAXY_KPC),
                  "sgr_stream": cid in SGR},
        "provenance": {"source": "Harris 1996 (2010 edition)",
                       "url": "https://physics.mcmaster.ca/~harris/mwgc.dat",
                       "citation": "Harris, W.E. 1996, AJ, 112, 1487 (2010 revision)"},
    }


def metadata(n):
    return {
        "title": "Milky Way Globular Cluster Corpus v1.0",
        "description": (
            "Harris (1996, 2010 edition) catalog of 157 Milky Way globular "
            "clusters. All three catalog parts merged into a unified schema "
            "optimised for LLM RAG inference."),
        "version": "1.0",
        "n_clusters": n,
        "source": "Harris, W.E. 1996, AJ, 112, 1487 (2010 revision)",
        "url": "https://physics.mcmaster.ca/~harris/mwgc.dat",
        "creator": "D.C. Flynn, EPS Research",
        "orcid": "0000-0002-2768-6650",
        "schema_notes": {
            "parsing": (
                "Harris is strict fixed-width with blank columns for missing "
                "values. All fields are read by declared character offset "
                "(P1_SPEC/P2_SPEC/P3_SPEC in 01_build_harris.py). Whitespace "
                "tokenisation is unsafe on this catalogue: it deletes blank "
                "columns and shifts every subsequent field left."),
            "coordinate_frame": (
                "distances.x_kpc/y_kpc/z_kpc are Harris's own HELIOCENTRIC "
                "Cartesian coordinates, used as published. They are not "
                "Galactocentric and must not be compared directly with "
                "baumgardt2023 X/Y/Z, which place the Sun at x = +R0."),
            "r_half_kpc": "Derived: r_half_arcmin * r_sun_kpc * (pi/10800), rounded to 4 dp",
            "r_core_kpc": "Derived: r_core_arcmin * r_sun_kpc * (pi/10800), rounded to 4 dp",
            "inner_galaxy": "Flag: r_gc_kpc < 3.0 kpc",
            "sgr_stream": (
                "Sgr dSph stream members: NGC 6715, Terzan 7, Terzan 8, Arp 2, "
                "Pal 12, Whiting 1. Editorial assignment inherited from the "
                "v1.0 generator; citation pending."),
            "core_collapsed": "c=confirmed core collapse, c:=probable core collapse (Harris notation)",
            "feh_weight": "Number of independent [Fe/H] measurements averaged",
            "log_t_rc_yr": "log10(core relaxation time / yr)",
            "log_t_rh_yr": "log10(median half-light relaxation time / yr)",
            "mu_v_central": "Central surface brightness (V mag/arcsec^2)",
            "log_rho0": "log10(central luminosity density / Lsun pc^-3)",
        },
    }


def flat_row(c):
    return {
        "cluster_id": c["cluster_id"], "alt_name": c["alt_name"],
        "ra_hms": c["position"]["ra_hms"], "dec_dms": c["position"]["dec_dms"],
        "l_deg": c["position"]["l_deg"], "b_deg": c["position"]["b_deg"],
        "r_sun_kpc": c["distances"]["r_sun_kpc"], "r_gc_kpc": c["distances"]["r_gc_kpc"],
        "x_kpc": c["distances"]["x_kpc"], "y_kpc": c["distances"]["y_kpc"],
        "z_kpc": c["distances"]["z_kpc"],
        "feh": c["metallicity"]["feh"], "feh_weight": c["metallicity"]["feh_weight"],
        "ebv": c["metallicity"]["ebv"], "v_hb": c["photometry"]["v_hb"],
        "dist_mod": c["photometry"]["dist_mod"], "v_t": c["photometry"]["v_t"],
        "m_v_t": c["photometry"]["m_v_t"],
        "spectral_type": c["photometry"]["spectral_type"],
        "ellipticity": c["photometry"]["ellipticity"],
        "bv": c["photometry"]["colors"]["bv"], "vi": c["photometry"]["colors"]["vi"],
        "v_r_kms": c["kinematics"]["v_r_kms"], "v_r_err": c["kinematics"]["v_r_err"],
        "sig_v_kms": c["kinematics"]["sig_v_kms"],
        "king_concentration": c["structure"]["king_concentration"],
        "core_collapsed": c["structure"]["core_collapsed"],
        "core_collapse_uncertain": c["structure"]["core_collapse_uncertain"],
        "r_core_arcmin": c["structure"]["r_core_arcmin"],
        "r_half_arcmin": c["structure"]["r_half_arcmin"],
        "r_core_kpc": c["structure"]["r_core_kpc"],
        "r_half_kpc": c["structure"]["r_half_kpc"],
        "mu_v_central": c["structure"]["mu_v_central"],
        "log_rho0": c["structure"]["log_rho0"],
        "log_t_rc_yr": c["dynamics"]["log_t_rc_yr"],
        "log_t_rh_yr": c["dynamics"]["log_t_rh_yr"],
        "inner_galaxy": c["flags"]["inner_galaxy"],
        "sgr_stream": c["flags"]["sgr_stream"],
    }


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default="harris_tables")
    ap.add_argument("--out-dir", default="build_out")
    ap.add_argument("--no-verify-manifest", dest="verify_manifest",
                    action="store_false")
    ap.add_argument("--report-arith", action="store_true",
                    help="report records where the original expression "
                         "grouping would differ from the K form")
    args = ap.parse_args()

    if len(P1_IDS) != len(set(P1_IDS)):
        sys.exit("ERROR: P1_IDS contains duplicates")

    parsed = load_tables(args.tables, args.verify_manifest)
    p1, p2, p3 = parsed["p1"], parsed["p2"], parsed["p3"]
    print(f"parsed    : P1={len(p1)}  P2={len(p2)}  P3={len(p3)}")

    # Integrity: the offsets must recover exactly the expected roster, in all
    # three parts. The original silently substituted {} for any miss.
    want = set(P1_IDS)
    for block, got in (("P1", set(p1)), ("P2", set(p2)), ("P3", set(p3))):
        if got != want:
            missing, extra = sorted(want - got), sorted(got - want)
            sys.exit(f"ERROR: {block} roster mismatch\n"
                     f"  missing from {block}: {missing}\n"
                     f"  not in P1_IDS    : {extra}")
    print(f"roster    : all three parts match P1_IDS ({len(want)} clusters)")

    clusters = [build_record(cid, p1[cid], p2[cid], p3[cid]) for cid in P1_IDS]

    if args.report_arith:
        diffs = []
        for cid in P1_IDS:
            rs = p1[cid]["r_sun_kpc"]
            for f in ("r_core_arcmin", "r_half_arcmin"):
                am = p3[cid][f]
                if not (num(am) and num(rs)):
                    continue
                a = round(am * rs * K, DP)
                b = round(am * rs * math.pi / (60 * 180), DP)
                if a != b:
                    diffs.append((cid, f, a, b))
        print(f"arith     : K-form vs original grouping differ on "
              f"{len(diffs)} derived radii {diffs[:5]}")

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    corpus = {"metadata": metadata(len(clusters)), "clusters": clusters}

    json_path = out / "harris_gc_corpus_v1.json"
    json_path.write_text(json.dumps(corpus, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")

    csv_path = out / "harris_gc_corpus_v1_flat.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        for c in clusters:
            w.writerow(flat_row(c))

    # ---- spot checks, retained from the original -------------------------
    g = clusters[0]
    assert g["cluster_id"] == "NGC 104"
    print(f"\n--- NGC 104 (47 Tuc) spot check ---")
    for label, val in (("alt_name", g["alt_name"]),
                       ("ra_hms", g["position"]["ra_hms"]),
                       ("dec_dms", g["position"]["dec_dms"]),
                       ("feh", g["metallicity"]["feh"]),
                       ("ebv", g["metallicity"]["ebv"]),
                       ("m_v_t", g["photometry"]["m_v_t"]),
                       ("ellipticity", g["photometry"]["ellipticity"]),
                       ("sig_v_kms", g["kinematics"]["sig_v_kms"]),
                       ("king_c", g["structure"]["king_concentration"]),
                       ("core_coll", g["structure"]["core_collapsed"]),
                       ("r_half_kpc", g["structure"]["r_half_kpc"]),
                       ("log_rho0", g["structure"]["log_rho0"]),
                       ("log_t_rh", g["dynamics"]["log_t_rh_yr"])):
        print(f"  {label:<12} {val!r}")

    cc = [c["cluster_id"] for c in clusters if c["structure"]["core_collapsed"]]
    fehs = [c["metallicity"]["feh"] for c in clusters
            if c["metallicity"]["feh"] is not None]
    sig = [c["kinematics"]["sig_v_kms"] for c in clusters
           if num(c["kinematics"]["sig_v_kms"])]
    print(f"\ncore-collapsed        : {len(cc)}  {cc[:6]}...")
    print(f"[Fe/H] range          : {min(fehs):.2f} to {max(fehs):.2f}  (n={len(fehs)})")
    print(f"sig_v range           : {min(sig):.2f} to {max(sig):.2f}  (n={len(sig)})")
    print(f"alt_name == 'M'       : {sum(1 for c in clusters if c['alt_name'] == 'M')}")
    print(f"RA hour > 23          : "
          f"{sum(1 for c in clusters if (c['position']['ra_hms'] or '').split(':')[0].isdigit() and int(c['position']['ra_hms'].split(':')[0]) > 23)}")
    print(f"inner galaxy (<3 kpc) : {sum(1 for c in clusters if c['flags']['inner_galaxy'])}")
    print(f"Sgr stream            : "
          f"{[c['cluster_id'] for c in clusters if c['flags']['sgr_stream']]}")
    print(f"\nJSON: {json_path}  ({json_path.stat().st_size / 1024:.1f} KB)")
    print(f"CSV : {csv_path}  ({csv_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
