"""
Merge Vasiliev & Baumgardt (2021) Gaia EDR3 proper motions + parallaxes
into the Harris GC corpus v1.0 → produce v1.1.

Data-type standards (matching SPARC RAG corpus):
  - All numeric values: native Python float or int (never str)
  - Missing / unmeasured: None  (→ JSON null)
  - Booleans: native Python bool
  - No unit conversion without schema documentation
  - Errors stored as separate float fields, not as strings like "5.252 ± 0.021"
  - New clusters (in V21 but not Harris): appended with harris fields = None

New fields added to every cluster record under key "gaia_edr3":
  {
    "ra_deg":           float | None,   # from V21 (more precise than HMS)
    "dec_deg":          float | None,
    "mu_alpha_mas_yr":  float | None,   # proper motion in RA*cos(dec)
    "mu_alpha_err":     float | None,
    "mu_delta_mas_yr":  float | None,
    "mu_delta_err":     float | None,
    "corr_mu":          float | None,   # PM correlation coefficient
    "parallax_mas":     float | None,   # Gaia parallax (zero-point corrected)
    "parallax_err":     float | None,
    "plummer_r0_arcmin":float | None,   # Plummer scale radius used in fit
    "n_members_gaia":   int   | None,   # member stars with good astrometry
    "source":           str             # citation key
  }

Clusters in V21 not in Harris 157 are appended as new records
with harris fields null and gaia_edr3 populated.
"""

import json, re

# ---------------------------------------------------------------------------
# Injected by desandbox_merge_scripts.py. Everything below this block is the
# original script, unmodified except for path literals and RAW_* assignments.
# ---------------------------------------------------------------------------
import argparse as _argparse, hashlib as _hashlib, sys as _sys
from pathlib import Path as _Path

_ap = _argparse.ArgumentParser(description=__doc__)
_ap.add_argument("--dir", default="build_out",
                 help="working directory: stage inputs are read from here and "
                      "outputs written here")
_ap.add_argument("--catalogs", default="catalogs",
                 help="directory holding the checksummed source tables")
_ap.add_argument("--no-verify-manifest", dest="verify_manifest",
                 action="store_false")
_ARGS = _ap.parse_args()

DIR = _Path(_ARGS.dir)
DIR.mkdir(parents=True, exist_ok=True)
OUT = str(DIR) + "/"
_CAT = _Path(_ARGS.catalogs)


def _sha256(path):
    h = _hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_table(stem, ncols_min, ncols_max):
    """Read a checksummed .tsv and assert its column geometry before use."""
    path = _CAT / (stem + ".tsv")
    if not path.exists():
        _sys.exit("ERROR: %s not found. Run desandbox_merge_scripts.py first."
                  % path)

    if _ARGS.verify_manifest:
        manifest = _CAT / "SHA256SUMS"
        if not manifest.exists():
            _sys.exit("ERROR: %s missing. Pass --no-verify-manifest only if "
                      "you accept unverified input." % manifest)
        want = None
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if line.strip().endswith(path.name):
                want = line.split(None, 1)[0]
        if want is None:
            _sys.exit("ERROR: %s has no entry in %s" % (path.name, manifest))
        got = _sha256(path)
        if got != want:
            _sys.exit("ERROR: checksum mismatch for %s\n  manifest %s\n"
                      "  actual   %s\nThe catalogue snapshot has changed. "
                      "Stop and find out why." % (path, want, got))

    text = path.read_text(encoding="utf-8")
    rows = [l for l in text.splitlines() if l.strip()]
    bad = [(i, len(l.split("\t"))) for i, l in enumerate(rows, 1)
           if not (ncols_min <= len(l.split("\t")) <= ncols_max)]
    if bad:
        _sys.exit("ERROR: %s -- %d row(s) outside the declared column range "
                  "%d..%d, e.g. line %d has %d columns.\nThe table geometry "
                  "changed; do not widen the range to make this pass."
                  % (path.name, len(bad), ncols_min, ncols_max,
                     bad[0][0], bad[0][1]))
    print("catalog   : %-26s %3d rows, %d..%d cols, verified"
          % (path.name, len(rows), ncols_min, ncols_max))
    return text
# ---------------------------------------------------------------------------



# ── STANDARDISED ID MAP: V21 name → Harris cluster_id ───────────────────────
# Many V21 names use alternate designations; map to Harris primary IDs
ID_MAP = {
    "NGC 104 (47 Tuc)":    "NGC 104",
    "47 Tuc":              "NGC 104",
    "E 1 (AM 1)":          "AM 1",
    "E 3 (ESO 37-1)":      "E 3",
    "NGC 4590 (M 68)":     "NGC 4590",
    "NGC 5024 (M 53)":     "NGC 5024",
    "NGC 5139 (omega Cen)":"NGC 5139",
    "NGC 5272 (M 3)":      "NGC 5272",
    "NGC 5904 (M 5)":      "NGC 5904",
    "NGC 6093 (M 80)":     "NGC 6093",
    "NGC 6121 (M 4)":      "NGC 6121",
    "NGC 6171 (M 107)":    "NGC 6171",
    "ESO 452-11 (1636-283)":"1636-283",
    "NGC 6205 (M 13)":     "NGC 6205",
    "NGC 1904 (M 79)":     "NGC 1904",
    "BH 261 (ESO 456-78)": "BH 261",
    "NGC 6218 (M 12)":     "NGC 6218",
    "NGC 6254 (M 10)":     "NGC 6254",
    "NGC 6266 (M 62)":     "NGC 6266",
    "NGC 6273 (M 19)":     "NGC 6273",
    "NGC 6333 (M 9)":      "NGC 6333",
    "NGC 6341 (M 92)":     "NGC 6341",
    "NGC 6380 (Ton 1)":    "NGC 6380",
    "NGC 6402 (M 14)":     "NGC 6402",
    "NGC 6441":            "NGC 6441",
    "NGC 6540 (Djorg 3)":  "NGC 6540",
    "NGC 6541":            "NGC 6541",
    "ESO 280-06":          "ESO-SC06",
    "Pal 7 (IC 1276)":     "IC 1276",
    "Terzan 2 (HP 3)":     "Terzan 2",
    "Terzan 4 (HP 4)":     "Terzan 4",
    "BH 229 (HP 1)":       "HP 1",
    "Terzan 1 (HP 2)":     "Terzan 1",
    "Terzan 5 (Terzan 11)":"Terzan 5",
    "Terzan 6 (HP 5)":     "Terzan 6",
    "Ton 2 (Pismis 26)":   "Ton 2",
    "NGC 6626 (M 28)":     "NGC 6626",
    "NGC 6637 (M 69)":     "NGC 6637",
    "NGC 6656 (M 22)":     "NGC 6656",
    "NGC 6681 (M 70)":     "NGC 6681",
    "NGC 6715 (M 54)":     "NGC 6715",
    "NGC 6717 (Pal 9)":    "NGC 6717",
    "NGC 6779 (M 56)":     "NGC 6779",
    "NGC 6809 (M 55)":     "NGC 6809",
    "NGC 6838 (M 71)":     "NGC 6838",
    "NGC 6864 (M 75)":     "NGC 6864",
    "NGC 6981 (M 72)":     "NGC 6981",
    "NGC 7078 (M 15)":     "NGC 7078",
    "NGC 7089 (M 2)":      "NGC 7089",
    "NGC 7099 (M 30)":     "NGC 7099",
    "BH 184 (Lynga 7)":    "Lynga 7",
    "Djorg 2 (ESO 456-38)":"Djorg 2",
    "Crater (Laevens 1)":  "Crater",
    "Pal 14 (Arp 1)":      "Pal 14",
    "NGC 6171 (M 107)":    "NGC 6171",
    "Ryu 059 (RLGC 1)":    "Ryu 059",
    "Ryu 879 (RLGC 2)":    "Ryu 879",
}

# ── RAW TABLE A1 ─────────────────────────────────────────────────────────────
# Pasted from PDF; Unicode minus signs normalised to ASCII below
RAW_V21 = _load_table("vasiliev2021_table_a1", 12, 12)

# ── PARSE ─────────────────────────────────────────────────────────────────────
def fv(s):
    s = str(s).strip()
    if not s or s in ('', '-'): return None
    try: return float(s)
    except: return None

v21 = {}
for line in RAW_V21.strip().splitlines():
    parts = line.split('\t')
    if len(parts) < 12: continue
    name = parts[0].strip()
    # Resolve to Harris ID
    harris_id = ID_MAP.get(name, name)
    v21[harris_id] = {
        "v21_name":           name,
        "ra_deg":             fv(parts[1]),
        "dec_deg":            fv(parts[2]),
        "mu_alpha_mas_yr":    fv(parts[3]),
        "mu_alpha_err":       fv(parts[4]),
        "mu_delta_mas_yr":    fv(parts[5]),
        "mu_delta_err":       fv(parts[6]),
        "corr_mu":            fv(parts[7]),
        "parallax_mas":       fv(parts[8]),
        "parallax_err":       fv(parts[9]),
        "plummer_r0_arcmin":  fv(parts[10]),
        "n_members_gaia":     int(float(parts[11])) if parts[11].strip().lstrip('-').isdigit() or '.' in parts[11] else None,
    }

print(f"V21 entries parsed: {len(v21)}")

# ── LOAD EXISTING CORPUS ──────────────────────────────────────────────────────
with open(OUT + "harris_gc_corpus_v1.json") as f:
    corpus = json.load(f)

harris_ids = {c["cluster_id"] for c in corpus["clusters"]}
print(f"Harris clusters: {len(harris_ids)}")

# ── IDENTIFY V21-ONLY CLUSTERS ────────────────────────────────────────────────
v21_only = {k: v for k, v in v21.items() if k not in harris_ids}
print(f"V21-only (new) clusters: {len(v21_only)}: {sorted(v21_only.keys())}")
matched = {k for k in v21 if k in harris_ids}
print(f"Matched to Harris: {len(matched)}")
unmatched_v21 = {k for k in v21 if k not in harris_ids and k not in {v['v21_name'] for v in v21.values()}}

PROV_V21 = {
    "source":   "Vasiliev & Baumgardt 2021",
    "doi":      "10.1093/mnras/stab1475",
    "bibcode":  "2021MNRAS.505.5978V",
    "table":    "Table A1",
    "instrument":"Gaia EDR3",
    "notes":    "PM and parallax include spatially correlated systematic errors. Systematic floor: sigma_parallax~0.011 mas, sigma_mu~0.026 mas/yr per component."
}

# ── MERGE: add gaia_edr3 block to each existing Harris cluster ────────────────
n_matched = 0
for c in corpus["clusters"]:
    cid = c["cluster_id"]
    if cid in v21:
        d = v21[cid]
        c["gaia_edr3"] = {
            "ra_deg":            d["ra_deg"],
            "dec_deg":           d["dec_deg"],
            "mu_alpha_mas_yr":   d["mu_alpha_mas_yr"],
            "mu_alpha_err":      d["mu_alpha_err"],
            "mu_delta_mas_yr":   d["mu_delta_mas_yr"],
            "mu_delta_err":      d["mu_delta_err"],
            "corr_mu":           d["corr_mu"],
            "parallax_mas":      d["parallax_mas"],
            "parallax_err":      d["parallax_err"],
            "plummer_r0_arcmin": d["plummer_r0_arcmin"],
            "n_members_gaia":    d["n_members_gaia"],
            "provenance":        PROV_V21,
        }
        n_matched += 1
    else:
        c["gaia_edr3"] = None  # not None — explicit null block is cleaner
        c["gaia_edr3"] = {
            "ra_deg": None, "dec_deg": None,
            "mu_alpha_mas_yr": None, "mu_alpha_err": None,
            "mu_delta_mas_yr": None, "mu_delta_err": None,
            "corr_mu": None, "parallax_mas": None, "parallax_err": None,
            "plummer_r0_arcmin": None, "n_members_gaia": None,
            "provenance": None,
        }

print(f"Harris clusters with Gaia data: {n_matched}")

# ── APPEND V21-ONLY NEW CLUSTERS ──────────────────────────────────────────────
import math
new_clusters = []
for cid, d in sorted(v21_only.items()):
    rec = {
        "cluster_id": cid,
        "alt_name":   None,
        "position":   {"ra_hms": None, "dec_dms": None, "l_deg": None, "b_deg": None},
        "distances":  {"r_sun_kpc": None, "r_gc_kpc": None,
                       "x_kpc": None, "y_kpc": None, "z_kpc": None},
        "metallicity":{"feh": None, "feh_weight": None, "ebv": None},
        "photometry": {"v_hb": None, "dist_mod": None, "v_t": None, "m_v_t": None,
                       "spectral_type": None, "ellipticity": None,
                       "colors": {"ub": None, "bv": None, "vr": None, "vi": None}},
        "kinematics": {"v_r_kms": None, "v_r_err": None, "v_lsr_kms": None,
                       "sig_v_kms": None, "sig_v_err": None},
        "structure":  {"king_concentration": None, "core_collapsed": False,
                       "core_collapse_uncertain": False,
                       "r_core_arcmin": None, "r_half_arcmin": None,
                       "r_core_kpc": None, "r_half_kpc": None,
                       "mu_v_central": None, "log_rho0": None},
        "dynamics":   {"log_t_rc_yr": None, "log_t_rh_yr": None},
        "flags":      {"inner_galaxy": False, "sgr_stream": cid in {"NGC 2419", "Ko 1"}},
        "gaia_edr3":  {
            "ra_deg":            d["ra_deg"],
            "dec_deg":           d["dec_deg"],
            "mu_alpha_mas_yr":   d["mu_alpha_mas_yr"],
            "mu_alpha_err":      d["mu_alpha_err"],
            "mu_delta_mas_yr":   d["mu_delta_mas_yr"],
            "mu_delta_err":      d["mu_delta_err"],
            "corr_mu":           d["corr_mu"],
            "parallax_mas":      d["parallax_mas"],
            "parallax_err":      d["parallax_err"],
            "plummer_r0_arcmin": d["plummer_r0_arcmin"],
            "n_members_gaia":    d["n_members_gaia"],
            "provenance":        PROV_V21,
        },
        "provenance": {
            "source":   "Vasiliev & Baumgardt 2021 (not in Harris 1996 2010 ed.)",
            "url":      "https://doi.org/10.1093/mnras/stab1475",
            "citation": "Vasiliev & Baumgardt 2021, MNRAS 505, 5978"
        }
    }
    new_clusters.append(rec)

corpus["clusters"].extend(new_clusters)
print(f"New clusters appended: {len(new_clusters)}")
total = len(corpus["clusters"])

# ── UPDATE METADATA ───────────────────────────────────────────────────────────
corpus["metadata"]["version"] = "1.1"
corpus["metadata"]["n_clusters"] = total
corpus["metadata"]["title"] = "Milky Way Globular Cluster Corpus v1.1"
corpus["metadata"]["description"] = (
    "Harris (1996, 2010 edition) catalog of 157 Milky Way globular clusters "
    "merged with Vasiliev & Baumgardt (2021) Gaia EDR3 proper motions and parallaxes "
    "for 170 clusters. Version 1.1 adds a gaia_edr3 block to every cluster record "
    "and appends 13 clusters present in V21 but not in the Harris (2010) catalog."
)
corpus["metadata"]["n_harris"] = 157
corpus["metadata"]["n_v21_only"] = len(new_clusters)
corpus["metadata"]["sources"] = [
    {"label": "harris1996_2010", "citation": "Harris, W.E. 1996, AJ, 112, 1487 (2010 revision)",
     "url": "https://physics.mcmaster.ca/~harris/mwgc.dat"},
    {"label": "vasiliev_baumgardt_2021", "citation": "Vasiliev & Baumgardt 2021, MNRAS 505, 5978",
     "doi": "10.1093/mnras/stab1475"},
]
corpus["metadata"]["schema_notes"]["gaia_edr3"] = (
    "Gaia EDR3 astrometry from Vasiliev & Baumgardt (2021) Table A1. "
    "mu_alpha_mas_yr is proper motion in RA * cos(dec). "
    "Errors include spatially correlated systematic floor (~0.011 mas parallax, ~0.026 mas/yr PM). "
    "parallax_mas has Lindegren et al. (2021) zero-point correction applied per-star. "
    "plummer_r0_arcmin is the Plummer scale radius used in the mixture model fit. "
    "n_members_gaia is the number of stars with good astrometry used in the fit. "
    "null in all gaia_edr3 fields = cluster not measurable by Gaia (e.g. 2MASS-GC01/02, GLIMPSE01/02)."
)

# ── WRITE JSON ────────────────────────────────────────────────────────────────
with open(OUT + "harris_gc_corpus_v1.1.json", "w") as f:
    json.dump(corpus, f, indent=2)
print(f"\nv1.1 JSON written: {total} clusters total")

# ── WRITE FLAT CSV ────────────────────────────────────────────────────────────
import csv
fields = [
    "cluster_id","alt_name","ra_hms","dec_dms","l_deg","b_deg",
    "r_sun_kpc","r_gc_kpc","x_kpc","y_kpc","z_kpc",
    "feh","feh_weight","ebv","v_hb","dist_mod","v_t","m_v_t",
    "spectral_type","ellipticity","bv","vi",
    "v_r_kms","v_r_err","sig_v_kms",
    "king_concentration","core_collapsed","core_collapse_uncertain",
    "r_core_arcmin","r_half_arcmin","r_core_kpc","r_half_kpc",
    "mu_v_central","log_rho0","log_t_rc_yr","log_t_rh_yr",
    "inner_galaxy","sgr_stream",
    # new Gaia columns
    "gaia_ra_deg","gaia_dec_deg",
    "mu_alpha_mas_yr","mu_alpha_err","mu_delta_mas_yr","mu_delta_err","corr_mu",
    "parallax_mas","parallax_err","plummer_r0_arcmin","n_members_gaia",
]
with open(OUT + "harris_gc_corpus_v1.1_flat.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    for c in corpus["clusters"]:
        ge = c.get("gaia_edr3") or {}
        row = {
            "cluster_id": c["cluster_id"], "alt_name": c["alt_name"],
            "ra_hms":  c["position"]["ra_hms"],  "dec_dms": c["position"]["dec_dms"],
            "l_deg":   c["position"]["l_deg"],   "b_deg":   c["position"]["b_deg"],
            "r_sun_kpc": c["distances"]["r_sun_kpc"], "r_gc_kpc": c["distances"]["r_gc_kpc"],
            "x_kpc": c["distances"]["x_kpc"], "y_kpc": c["distances"]["y_kpc"], "z_kpc": c["distances"]["z_kpc"],
            "feh": c["metallicity"]["feh"], "feh_weight": c["metallicity"]["feh_weight"], "ebv": c["metallicity"]["ebv"],
            "v_hb": c["photometry"]["v_hb"], "dist_mod": c["photometry"]["dist_mod"],
            "v_t": c["photometry"]["v_t"], "m_v_t": c["photometry"]["m_v_t"],
            "spectral_type": c["photometry"]["spectral_type"], "ellipticity": c["photometry"]["ellipticity"],
            "bv": c["photometry"]["colors"]["bv"], "vi": c["photometry"]["colors"]["vi"],
            "v_r_kms": c["kinematics"]["v_r_kms"], "v_r_err": c["kinematics"]["v_r_err"],
            "sig_v_kms": c["kinematics"]["sig_v_kms"],
            "king_concentration": c["structure"]["king_concentration"],
            "core_collapsed": c["structure"]["core_collapsed"],
            "core_collapse_uncertain": c["structure"]["core_collapse_uncertain"],
            "r_core_arcmin": c["structure"]["r_core_arcmin"], "r_half_arcmin": c["structure"]["r_half_arcmin"],
            "r_core_kpc": c["structure"]["r_core_kpc"], "r_half_kpc": c["structure"]["r_half_kpc"],
            "mu_v_central": c["structure"]["mu_v_central"], "log_rho0": c["structure"]["log_rho0"],
            "log_t_rc_yr": c["dynamics"]["log_t_rc_yr"], "log_t_rh_yr": c["dynamics"]["log_t_rh_yr"],
            "inner_galaxy": c["flags"]["inner_galaxy"], "sgr_stream": c["flags"]["sgr_stream"],
            "gaia_ra_deg":        ge.get("ra_deg"),
            "gaia_dec_deg":       ge.get("dec_deg"),
            "mu_alpha_mas_yr":    ge.get("mu_alpha_mas_yr"),
            "mu_alpha_err":       ge.get("mu_alpha_err"),
            "mu_delta_mas_yr":    ge.get("mu_delta_mas_yr"),
            "mu_delta_err":       ge.get("mu_delta_err"),
            "corr_mu":            ge.get("corr_mu"),
            "parallax_mas":       ge.get("parallax_mas"),
            "parallax_err":       ge.get("parallax_err"),
            "plummer_r0_arcmin":  ge.get("plummer_r0_arcmin"),
            "n_members_gaia":     ge.get("n_members_gaia"),
        }
        w.writerow(row)

import os
print(f"JSON:  {os.path.getsize(OUT + 'harris_gc_corpus_v1.1.json')/1024:.1f} KB")
print(f"CSV:   {os.path.getsize(OUT + 'harris_gc_corpus_v1.1_flat.csv')/1024:.1f} KB")

# ── SPOT CHECKS ───────────────────────────────────────────────────────────────
with open(OUT + "harris_gc_corpus_v1.1.json") as f:
    d = json.load(f)
gc = next(c for c in d["clusters"] if c["cluster_id"]=="NGC 104")
ge = gc["gaia_edr3"]
print(f"\nNGC 104 Gaia check:")
print(f"  mu_alpha={ge['mu_alpha_mas_yr']} ± {ge['mu_alpha_err']}")
print(f"  mu_delta={ge['mu_delta_mas_yr']} ± {ge['mu_delta_err']}")
print(f"  parallax={ge['parallax_mas']} ± {ge['parallax_err']}")
print(f"  n_members={ge['n_members_gaia']}")
print(f"  types: mu_alpha={type(ge['mu_alpha_mas_yr']).__name__}, n_members={type(ge['n_members_gaia']).__name__}")
# Check new cluster
new = next((c for c in d["clusters"] if c["cluster_id"]=="BH 140"), None)
if new:
    print(f"\nBH 140 (V21-only): feh={new['metallicity']['feh']}, mu_alpha={new['gaia_edr3']['mu_alpha_mas_yr']}")
