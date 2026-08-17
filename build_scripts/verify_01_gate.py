#!/usr/bin/env python3
"""
verify_01_gate.py -- acceptance gate for the rewritten 01_build_harris.py.

Two independent gates.

GATE 1 (parse)   Every field of every cluster in all three parts, as parsed by
                 the rewritten generator, must equal harris_reparsed_v14.json
                 -- the authoritative offset re-parse that was round-trip
                 verified against the raw tables, 157/157.

GATE 2 (derive)  For the 157 Harris-covered clusters, every Harris-owned field
                 of the generator's output must equal the reference corpus,
                 exactly. This catches the derived arithmetic -- r_core_kpc,
                 r_half_kpc at K = pi/10800 with 4 dp rounding, inner_galaxy at
                 r_gc < 3.0, and the core-collapse flag decomposition -- which
                 a field-by-field parse comparison cannot reach.

Comparison is exact, not tolerant. 424 of 438 is a failure, not a rounding
issue; the same standard applies here.

Usage:
    # gate 1 only
    python3 verify_01_gate.py --tables harris_tables \
        --reparsed harris_reparsed_v14.json

    # both gates, once v1.4.0 exists
    python3 verify_01_gate.py --tables harris_tables \
        --reparsed harris_reparsed_v14.json \
        --against examples/gc/harris_gc_corpus_v1.4.0.json

    # defect census: point gate 2 at the defective corpus instead
    python3 verify_01_gate.py --tables harris_tables \
        --reparsed harris_reparsed_v14.json \
        --against examples/gc/harris_gc_corpus_v1.3.3.json --census

Exit status is 0 only if every requested gate passes.
"""

import argparse
import importlib.util
import json
import sys
from pathlib import Path

# Harris-owned paths. Everything the rewritten stage 1 is responsible for, and
# nothing else -- gaia_edr3 / baumgardt2023 / apogee_dr17 / provenance and any
# _-prefixed audit scaffolding are out of scope by construction.
PATHS = [
    ("alt_name",),
    ("position", "ra_hms"), ("position", "dec_dms"),
    ("position", "l_deg"), ("position", "b_deg"),
    ("distances", "r_sun_kpc"), ("distances", "r_gc_kpc"),
    ("distances", "x_kpc"), ("distances", "y_kpc"), ("distances", "z_kpc"),
    ("metallicity", "feh"), ("metallicity", "feh_weight"), ("metallicity", "ebv"),
    ("photometry", "v_hb"), ("photometry", "dist_mod"),
    ("photometry", "v_t"), ("photometry", "m_v_t"),
    ("photometry", "spectral_type"), ("photometry", "ellipticity"),
    ("photometry", "colors", "ub"), ("photometry", "colors", "bv"),
    ("photometry", "colors", "vr"), ("photometry", "colors", "vi"),
    ("kinematics", "v_r_kms"), ("kinematics", "v_r_err"),
    ("kinematics", "v_lsr_kms"), ("kinematics", "sig_v_kms"),
    ("kinematics", "sig_v_err"),
    ("structure", "king_concentration"),
    ("structure", "core_collapsed"), ("structure", "core_collapse_uncertain"),
    ("structure", "r_core_arcmin"), ("structure", "r_half_arcmin"),
    ("structure", "r_core_kpc"), ("structure", "r_half_kpc"),
    ("structure", "mu_v_central"), ("structure", "log_rho0"),
    ("dynamics", "log_t_rc_yr"), ("dynamics", "log_t_rh_yr"),
    ("flags", "inner_galaxy"), ("flags", "sgr_stream"),
]


def load_generator(path):
    spec = importlib.util.spec_from_file_location("gen01", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gen01"] = mod
    spec.loader.exec_module(mod)
    return mod


def dig(rec, path):
    cur = rec
    for key in path:
        if not isinstance(cur, dict):
            return ("<missing>",)
        if key not in cur:
            return ("<missing>",)
        cur = cur[key]
    return cur


def same(a, b):
    """Exact equality. bool is kept distinct from numeric, so True != 1.

    int and float are allowed to compare equal (3 == 3.0): JSON round-tripping
    can legitimately change which of the two a whole number comes back as.
    No tolerance is applied to fractional values.
    """
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, str) or isinstance(b, str):
        return isinstance(a, str) and isinstance(b, str) and a == b
    return a == b


def gate1(mod, tables, reparsed_path, verify_manifest):
    print("=== GATE 1  parse vs authoritative re-parse ===")
    ref = json.loads(Path(reparsed_path).read_text(encoding="utf-8"))
    got = mod.load_tables(tables, verify_manifest)

    ok = True
    for block in ("p1", "p2", "p3"):
        r, g = ref[block], got[block]
        if set(r) != set(g):
            print(f"  {block.upper()}: roster differs -- "
                  f"only in reference {sorted(set(r) - set(g))[:5]}, "
                  f"only in generator {sorted(set(g) - set(r))[:5]}")
            ok = False
            continue
        fields = sorted({k for rec in r.values() for k in rec} |
                        {k for rec in g.values() for k in rec})
        bad = []
        for cid in r:
            for f in fields:
                a, b = r[cid].get(f), g[cid].get(f)
                if not same(a, b):
                    bad.append((cid, f, a, b))
        n = len(r) * len(fields)
        if bad:
            ok = False
            print(f"  {block.upper()}: {len(bad)} of {n} field values differ")
            for cid, f, a, b in bad[:8]:
                print(f"      {cid:<12} {f:<22} reference={a!r:>14}  generator={b!r:>14}")
        else:
            print(f"  {block.upper()}: {len(r)} clusters x {len(fields)} fields "
                  f"= {n} values, all exact")
    print("  GATE 1", "PASS" if ok else "FAIL", "\n")
    return ok


def gate2(mod, tables, against, verify_manifest, census):
    label = "defect census vs" if census else "derived fields vs"
    print(f"=== GATE 2  {label} {against} ===")
    doc = json.loads(Path(against).read_text(encoding="utf-8"))
    ref = {c["cluster_id"]: c for c in doc["clusters"]}
    print(f"  reference version: {doc.get('metadata', {}).get('version')}  "
          f"records: {len(ref)}")

    parsed = mod.load_tables(tables, verify_manifest)
    p1, p2, p3 = parsed["p1"], parsed["p2"], parsed["p3"]
    absent = [cid for cid in mod.P1_IDS
              if cid not in p1 or cid not in p2 or cid not in p3]
    if absent:
        print(f"  ERROR: {len(absent)} ids in P1_IDS are missing from the "
              f"parsed tables: {absent[:5]}")
        print("  GATE 2 FAIL\n")
        return False
    built = {cid: mod.build_record(cid, p1[cid], p2[cid], p3[cid])
             for cid in mod.P1_IDS}

    missing = [cid for cid in built if cid not in ref]
    if missing:
        print(f"  !! {len(missing)} Harris clusters absent from reference: "
              f"{missing[:5]}")

    tally, examples, compared = {}, {}, 0
    for cid, new in built.items():
        old = ref.get(cid)
        if old is None:
            continue
        for path in PATHS:
            compared += 1
            a, b = dig(old, path), dig(new, path)
            if not same(a, b):
                key = ".".join(path)
                tally[key] = tally.get(key, 0) + 1
                examples.setdefault(key, []).append((cid, a, b))

    touched = len({cid for path in PATHS for cid, _, _ in
                   examples.get(".".join(path), [])})
    print(f"  compared {compared} values across "
          f"{len(built) - len(missing)} clusters x {len(PATHS)} fields")
    print(f"  records differing: {touched}")

    if not tally:
        print("  no differences\n  GATE 2 PASS\n")
        return True

    print("\n  field                                  differing")
    for key in sorted(tally, key=lambda k: -tally[k]):
        print(f"  {key:<40} {tally[key]:>5}")
    print("\n  examples:")
    for key in sorted(tally, key=lambda k: -tally[key])[:6]:
        for cid, a, b in examples[key][:3]:
            print(f"    {key:<34} {cid:<12} reference={a!r:>13}  generator={b!r:>13}")

    if census:
        print("\n  CENSUS MODE -- differences are the expected defect scale, "
              "not a gate failure.\n")
        return True
    print("\n  GATE 2 FAIL\n")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generator", default="01_build_harris.py")
    ap.add_argument("--tables", default="harris_tables")
    ap.add_argument("--reparsed", default="harris_reparsed_v14.json")
    ap.add_argument("--against", default=None,
                    help="reference corpus for gate 2 (v1.4.0 once it exists)")
    ap.add_argument("--census", action="store_true",
                    help="gate 2 reports differences without failing")
    ap.add_argument("--no-verify-manifest", dest="verify_manifest",
                    action="store_false")
    args = ap.parse_args()

    mod = load_generator(args.generator)
    ok = gate1(mod, args.tables, args.reparsed, args.verify_manifest)
    if args.against:
        ok = gate2(mod, args.tables, args.against,
                   args.verify_manifest, args.census) and ok
    else:
        print("(gate 2 skipped -- pass --against once v1.4.0 exists)\n")

    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
