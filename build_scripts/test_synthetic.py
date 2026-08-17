#!/usr/bin/env python3
"""Synthetic exercise of 01_build_harris.py -- no real Harris data required."""
import importlib.util, json, math, sys, hashlib
from pathlib import Path

spec = importlib.util.spec_from_file_location("g", "01_build_harris.py")
g = importlib.util.module_from_spec(spec); sys.modules["g"] = g
spec.loader.exec_module(g)


def lay(specs, values):
    """Right-align numerics / left-align strings into the declared spans."""
    width = specs[-1][2]
    buf = [" "] * width
    for (name, a, b, kind), v in zip(specs, values):
        if v is None:
            continue
        s = str(v)
        assert len(s) <= b - a, f"{name}: {s!r} wider than span {b-a}"
        start = a if kind in ("s", "flag") else b - len(s)
        buf[start:start + len(s)] = list(s)
    return "".join(buf).rstrip()


ids = ["NGC 104", "Pal 13", "Ton 2"]

p1_rows = [
    lay(g.P1_SPEC, ["NGC 104", "47 Tuc", "00 24 05.67", "-72 04 52.6",
                    "305.89", "-44.89", "4.5", "7.4", "1.9", "-2.6", "-3.1"]),
    # no alt_name at all -- the blank that broke the token parser
    lay(g.P1_SPEC, ["Pal 13", None, "23 06 44.4", "+12 46 19",
                    "87.10", "-42.70", "26.0", "26.9", "14.2", "13.9", "-17.5"]),
    # multi-token alt_name whose second token is two digits: the P1 shift case
    lay(g.P1_SPEC, ["Ton 2", "Pismis 26", "17 36 10.5", "-38 33 12",
                    "350.80", "-3.42", "8.2", "1.4", "1.1", "-0.2", "-0.5"]),
]
p2_rows = [
    lay(g.P2_SPEC, ["NGC 104", "-0.72", "34", "0.04", "14.06", "13.37",
                    "3.95", "-9.42", "0.36", "0.88", "0.58", "1.13", "G4", "0.09"]),
    # blank feh AND blank weight AND blank ellipticity/spectral type
    lay(g.P2_SPEC, ["Pal 13", None, None, "0.05", "18.10", "17.23",
                    "13.80", "-3.74", "0.14", "0.70", None, None, None, None]),
    lay(g.P2_SPEC, ["Ton 2", "-0.70", "3", "1.24", "None".replace("None", "17.10"),
                    "16.15", "12.24", "-6.14", "0.99", "1.53", None, None, None, None]),
]
p3_rows = [
    lay(g.P3_SPEC, ["NGC 104", "-18.0", "0.1", "-26.7", "11.0", "0.3",
                    "2.07", None, "0.36", "3.17", "14.44", "4.88", "7.84", "9.55"]),
    # blank v_r AND blank sig_v -- the wide P3 shift case; core-collapse flag set
    lay(g.P3_SPEC, ["Pal 13", "25.2", "0.4", "16.2", "0.4", "0.3",
                    "0.66", "c:", "0.48", "0.66", "24.30", "-0.20", "8.36", "8.35"]),
    lay(g.P3_SPEC, ["Ton 2", "-184.4", "4.0", "-178.2", None, None,
                    "1.30", "c", "0.55", "1.03", "20.20", "2.10", "8.20", "8.90"]),
]

tables = Path("t"); tables.mkdir(exist_ok=True)
for name, rows in (("p1", p1_rows), ("p2", p2_rows), ("p3", p3_rows)):
    (tables / f"mwgc_{name}.dat").write_text("\n".join(rows) + "\n")
sums = "".join(
    f"{hashlib.sha256((tables / f'mwgc_{n}.dat').read_bytes()).hexdigest()}  mwgc_{n}.dat\n"
    for n in ("p1", "p2", "p3"))
(tables / "SHA256SUMS").write_text(sums)

g.P1_IDS = ids
g.SGR = {"Pal 13"}

parsed = g.load_tables("t", verify_manifest=True)
recs = {c: g.build_record(c, parsed["p1"][c], parsed["p2"][c], parsed["p3"][c])
        for c in ids}

print("\n--- blanks preserved as None, not shifted ---")
print("Pal 13 feh          :", recs["Pal 13"]["metallicity"]["feh"])
print("Pal 13 feh_weight   :", recs["Pal 13"]["metallicity"]["feh_weight"])
print("Pal 13 ellipticity  :", recs["Pal 13"]["photometry"]["ellipticity"])
print("Ton 2  sig_v_kms    :", recs["Ton 2"]["kinematics"]["sig_v_kms"])
print("Ton 2  king_c       :", recs["Ton 2"]["structure"]["king_concentration"])
assert recs["Pal 13"]["metallicity"]["feh"] is None
assert recs["Pal 13"]["photometry"]["ellipticity"] is None
assert recs["Ton 2"]["kinematics"]["sig_v_kms"] is None
assert recs["Ton 2"]["structure"]["king_concentration"] == 1.30, "king c leaked"

print("\n--- alt_name / coordinates not cross-contaminated ---")
for c in ids:
    print(f"{c:<9} alt={recs[c]['alt_name']!r:<12} "
          f"ra={recs[c]['position']['ra_hms']!r:<14} "
          f"dec={recs[c]['position']['dec_dms']!r}")
assert recs["NGC 104"]["alt_name"] == "47 Tuc"
assert recs["NGC 104"]["position"]["ra_hms"] == "00:24:05.67"
assert recs["Ton 2"]["alt_name"] == "Pismis 26"
assert recs["Ton 2"]["position"]["ra_hms"] == "17:36:10.5"
assert recs["Pal 13"]["alt_name"] is None

print("\n--- core-collapse flag decomposition ---")
for c in ids:
    s = recs[c]["structure"]
    print(f"{c:<9} collapsed={s['core_collapsed']!r:<6} uncertain={s['core_collapse_uncertain']!r}")
assert (recs["NGC 104"]["structure"]["core_collapsed"],
        recs["NGC 104"]["structure"]["core_collapse_uncertain"]) == (False, False)
assert (recs["Pal 13"]["structure"]["core_collapsed"],
        recs["Pal 13"]["structure"]["core_collapse_uncertain"]) == (True, True)
assert (recs["Ton 2"]["structure"]["core_collapsed"],
        recs["Ton 2"]["structure"]["core_collapse_uncertain"]) == (True, False)

print("\n--- derived radii match the rebuild's arithmetic exactly ---")
K = math.pi / 10800.0
for c in ids:
    s, rs = recs[c]["structure"], recs[c]["distances"]["r_sun_kpc"]
    want_c = round(s["r_core_arcmin"] * rs * K, 4)
    want_h = round(s["r_half_arcmin"] * rs * K, 4)
    print(f"{c:<9} r_core_kpc={s['r_core_kpc']} r_half_kpc={s['r_half_kpc']}")
    assert s["r_core_kpc"] == want_c and s["r_half_kpc"] == want_h

print("\n--- inner_galaxy from r_gc < 3.0 ---")
for c in ids:
    print(f"{c:<9} r_gc={recs[c]['distances']['r_gc_kpc']:<6} "
          f"inner={recs[c]['flags']['inner_galaxy']}")
assert recs["Ton 2"]["flags"]["inner_galaxy"] is True
assert recs["NGC 104"]["flags"]["inner_galaxy"] is False

print("\n--- OffsetError fires instead of degrading to None ---")
# (a) a span widened across the next column, so it swallows two values
bad = g.P2_SPEC[:]
bad[1] = ("feh", 12, 19, "f")
try:
    g.parse_block("\n".join(p2_rows) + "\n", bad, "P2-wide-span")
    print("  !! no error raised -- guard is not working")
    sys.exit(1)
except g.OffsetError as e:
    print("  (a)", str(e)[:120], "...")

# (b) the historical 13-field P3 error: the core-collapse marker column read
#     as a number instead of a flag
bad = g.P3_SPEC[:]
bad[7] = ("core_collapse_flag", 54, 58, "f")
try:
    g.parse_block("\n".join(p3_rows) + "\n", bad, "P3-flag-as-float")
    print("  !! no error raised -- guard is not working")
    sys.exit(1)
except g.OffsetError as e:
    print("  (b)", str(e)[:120], "...")

print("\n--- overflow guard: an unread trailing column is refused ---")
try:
    g.parse_block(p1_rows[0] + "   99.9\n", g.P1_SPEC, "P1-wide")
    print("  !! no error raised")
    sys.exit(1)
except g.OffsetError as e:
    print("  OffsetError:", str(e)[:110], "...")

print("\n--- checksum guard: a tampered table is refused ---")
p = tables / "mwgc_p1.dat"
orig = p.read_text()
p.write_text(orig.replace("4.5", "4.6", 1))
try:
    g.load_tables("t", verify_manifest=True)
    print("  !! tampered table accepted")
    sys.exit(1)
except SystemExit as e:
    print("  refused:", str(e).splitlines()[0])
finally:
    p.write_text(orig)

print("\nALL SYNTHETIC CHECKS PASSED")
