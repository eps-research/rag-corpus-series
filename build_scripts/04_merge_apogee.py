"""
Merge APOGEE DR17 GC VAC (Schiavon et al. 2024, MNRAS 528, 1393)
into harris_gc_corpus_v1.2.json → produce v1.3

Source: Table 1 of Schiavon et al. 2024 (arxiv:2310.07764)
  72 Galactic GCs, mean [Fe/H] from APOGEE, n_members per cluster

New block per cluster: "apogee_dr17"
  {
    "feh_apogee":      float | None,   # mean [Fe/H] from APOGEE ASPCAP
    "rv_mean_kms":     float | None,   # mean RV (km/s)
    "rv_err":          float | None,   # error on mean RV
    "r_sun_kpc":       float | None,   # heliocentric distance (VB catalogue)
    "r_gc_kpc":        float | None,   # galactocentric distance
    "mass_1e4_msun":   float | None,   # mass in 10^4 Msun
    "r_jacobi_deg":    float | None,   # Jacobi radius in degrees
    "n_members":       int   | None,   # number of likely+outlier members in VAC
    "provenance":      dict
  }

Data-type standards: all numerics native float/int, missing = None
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



def fv(s):
    if s is None: return None
    s = str(s).strip().replace('−','-').replace('\u2212','-')
    if not s or s in ('—','–',''): return None
    m = re.match(r'^([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)', s)
    return float(m.group(1)) if m else None

# ── TABLE 1 from Schiavon et al. 2024 ────────────────────────────────────────
# Columns: name, ra, dec, feh_apogee, rv_mean, rv_err, r_sun_kpc, r_gc_kpc,
#          mass_1e4_msun, r_jacobi_deg, n_members
RAW_APOGEE = _load_table("schiavon2024_table1", 11, 11)

# ID normalisation map
A_MAP = {
    "Palomar 1":  "Pal 1",
    "Palomar 5":  "Pal 5",
    "Palomar 6":  "Pal 6",
    "Palomar 10": "Pal 10",
    "Rup 106":    "Rup 106",
    "UKS 1":      "UKS 1",
    "FSR 1758":   "FSR 1758",
    "HP 1":       "HP 1",
    "Terzan 2":   "Terzan 2",
    "Terzan 4":   "Terzan 4",
    "Terzan 5":   "Terzan 5",
    "Terzan 9":   "Terzan 9",
    "Terzan 10":  "Terzan 10",
    "Terzan 12":  "Terzan 12",
    "Djorg 2":    "Djorg 2",
    "Ton 2":      "Ton 2",
    "Liller 1":   "Liller 1",
}

def resolve(name):
    return A_MAP.get(name, name)

apogee = {}
for line in RAW_APOGEE.strip().splitlines():
    p = line.split('\t')
    if len(p) < 11: continue
    cid = resolve(p[0].strip())
    apogee[cid] = {
        "feh_apogee":    fv(p[3]),
        "rv_mean_kms":   fv(p[4]),
        "rv_err":        fv(p[5]),
        "r_sun_kpc":     fv(p[6]),
        "r_gc_kpc":      fv(p[7]),
        "mass_1e4_msun": fv(p[8]),
        "r_jacobi_deg":  fv(p[9]),
        "n_members":     int(float(p[10])) if p[10].strip() else None,
    }

print(f"APOGEE entries parsed: {len(apogee)}")

# ── LOAD V1.2 ─────────────────────────────────────────────────────────────────
with open(OUT + "harris_gc_corpus_v1.2.json") as f:
    corpus = json.load(f)

PROV_A = {
    "source":    "Schiavon et al. 2024 (APOGEE DR17 GC VAC)",
    "doi":       "10.1093/mnras/stad3419",
    "arxiv":     "2310.07764",
    "citation":  "Schiavon et al. 2024, MNRAS 528, 1393",
    "instrument":"APOGEE spectrograph (H-band, R~22500)",
    "pipeline":  "ASPCAP synspec_rev1 with NLTE for Na, Mg, K, Ca",
    "notes":     "Mean cluster [Fe/H] and RV from likely+outlier member stars. "
                 "n_members = total entries in VAC (likely + outlier). "
                 "r_sun_kpc and r_gc_kpc are from Baumgardt & Vasiliev (2021) as tabulated in the VAC. "
                 "mass_1e4_msun in units of 10^4 solar masses."
}

EMPTY_A = {k: None for k in [
    "feh_apogee","rv_mean_kms","rv_err",
    "r_sun_kpc","r_gc_kpc","mass_1e4_msun","r_jacobi_deg","n_members"
]}

n_matched = 0
for c in corpus["clusters"]:
    cid = c["cluster_id"]
    if cid in apogee:
        d = apogee[cid]
        c["apogee_dr17"] = {**d, "provenance": PROV_A}
        n_matched += 1
    else:
        c["apogee_dr17"] = {**EMPTY_A, "provenance": None}

print(f"Clusters matched to APOGEE: {n_matched}/72 expected")

# ── UPDATE METADATA ───────────────────────────────────────────────────────────
total = len(corpus["clusters"])
corpus["metadata"]["version"]     = "1.4.0"
corpus["metadata"]["title"]       = "Milky Way Globular Cluster Corpus v1.4.0"
corpus["metadata"]["n_clusters"]  = total
corpus["metadata"]["description"] = (
    "Harris (1996, 2010 ed.) 157-cluster catalog merged with "
    "Vasiliev & Baumgardt (2021) Gaia EDR3 proper motions (v1.1), "
    "Baumgardt et al. (2023) N-body structural/orbital parameters (v1.2), "
    "and Schiavon et al. (2024) APOGEE DR17 mean chemical abundances. "
    "Version 1.4.0 rebuilds Harris-derived fields from checksum-verified fixed-width "
    "source tables using declared character offsets. "
    "Four independent surveys: photometry/structure (Harris), kinematics (Vasiliev), "
    "dynamics/orbits (Baumgardt), chemistry (APOGEE). "
    "174 clusters total; chemistry available for 72."
)
corpus["metadata"]["n_apogee"] = n_matched
corpus["metadata"]["sources"].append({
    "label":    "schiavon2024_apogee_dr17",
    "citation": "Schiavon et al. 2024, MNRAS 528, 1393",
    "doi":      "10.1093/mnras/stad3419",
    "arxiv":    "2310.07764",
})
corpus["metadata"]["schema_notes"]["apogee_dr17"] = (
    "Mean chemical abundances from APOGEE DR17 GC VAC (Schiavon et al. 2024). "
    "feh_apogee = mean [Fe/H] from ASPCAP; may differ from Harris feh by ~0.1 dex due to "
    "different methods (photometric vs spectroscopic). "
    "rv_mean_kms = mean radial velocity from APOGEE members. "
    "mass_1e4_msun = cluster mass in units of 10^4 solar masses (from Baumgardt & Vasiliev 2021). "
    "r_jacobi_deg = Jacobi (tidal) radius in degrees. "
    "n_members = number of likely+outlier candidate members in the VAC. "
    "null in all fields = cluster not observed/identified in APOGEE DR17."
)


# ── RELEASE / FAIR² METADATA ──────────────────────────────────────────────────
# v1.4.0 is produced directly by the checksum-verified 01→04 build chain.
# Historical v1.3.x repair material is retained in separate audit sidecars,
# never inside searchable current-data records.
md = corpus["metadata"]

md["corpus"] = "Milky Way Globular Cluster Corpus"
md["creator"] = "David C. Flynn, EPS Research"
md["orcid"] = "0000-0002-2768-6650"
md["license"] = "CC BY 4.0"
md["github"] = "https://github.com/eps-research/rag-corpus-series"
md["last_modified"] = "2026-08-20"
md["supersedes"] = "1.3.3"

# Do NOT attach the previous version-specific Zenodo DOI to v1.4.0.
# A v1.4.0 version DOI will be inserted only after the new deposit exists.
md.pop("zenodo_doi", None)

md["coordinate_frame"] = (
    "distances.x/y/z_kpc are heliocentric Cartesian coordinates "
    "(Sun at origin) from the Harris source fields. "
    "baumgardt2023.x/y/z_kpc are Galactocentric and are not interchangeable "
    "with distances.x/y/z_kpc."
)

md["notes"] = (
    "v1.4.0 is a clean rebuild of all Harris-derived fields from the "
    "checksum-verified Harris (1996, 2010 edition) fixed-width catalogue "
    "snapshot using declared character offsets. It supersedes the v1.3.3 "
    "patch-based repair path. Historical v1.3.x values and repair evidence "
    "are retained separately in gc_v133_prior_audit.json and "
    "gc_v140_change_manifest.json so stale values cannot be indexed or "
    "returned as current data. Non-Harris Gaia EDR3, Baumgardt et al. (2023), "
    "and APOGEE DR17 blocks are preserved through the merge chain. "
    "The 17 Vasiliev-only clusters receive Galactic l/b coordinates "
    "deterministically transformed from the published ICRS/J2000 RA/Dec; "
    "relative to the prior rounded corpus values, the largest observed "
    "coordinate difference is 0.0018 deg."
)

md["schema_notes"]["coordinate_frame"] = (
    "distances.x_kpc/y_kpc/z_kpc are Harris heliocentric Cartesian "
    "coordinates. baumgardt2023.x_kpc/y_kpc/z_kpc use the independent "
    "Baumgardt Galactocentric frame."
)

md["schema_notes"]["vasiliev_only_position"] = (
    "For the 17 clusters present in Vasiliev & Baumgardt (2021) but absent "
    "from Harris, position.l_deg and position.b_deg are calculated from the "
    "published ICRS/J2000 ra_deg and dec_deg using the standard IAU J2000 "
    "equatorial-to-Galactic transformation."
)

with open(OUT + "harris_gc_corpus_v1.4.0.json","w") as f:
    json.dump(corpus, f, indent=2)

# ── JSONL ─────────────────────────────────────────────────────────────────────
with open(OUT + "harris_gc_corpus_v1.4.0.jsonl","w") as f:
    for c in corpus["clusters"]:
        f.write(json.dumps(c) + "\n")

# ── FLAT CSV (add apogee columns) ─────────────────────────────────────────────
import csv
fields = [
    "cluster_id","alt_name","l_deg","b_deg",
    "harris_r_sun_kpc","harris_r_gc_kpc","harris_x_kpc","harris_y_kpc","harris_z_kpc",
    "feh","ebv","m_v_t","dist_mod",
    "king_c","core_collapsed","r_core_arcmin","r_half_arcmin","r_half_kpc","log_rho0",
    "log_t_rc_yr","log_t_rh_yr","v_r_harris_kms","inner_galaxy","sgr_stream",
    "gaia_mu_alpha","gaia_mu_alpha_err","gaia_mu_delta","gaia_mu_delta_err",
    "gaia_corr_mu","gaia_parallax_mas","gaia_parallax_err","gaia_n_members",
    "b_r_sun_kpc","b_r_sun_err","b_r_gc_kpc","b_r_gc_err",
    "b_rv_kms","b_rv_err","b_mu_alpha","b_mu_alpha_err","b_mu_delta","b_mu_delta_err",
    "b_x_kpc","b_y_kpc","b_z_kpc","b_u_kms","b_v_kms","b_w_kms",
    "b_r_peri_kpc","b_r_apo_kpc","b_mass_msun","b_mass_err","b_v_mag","b_ml_v",
    "b_rc_pc","b_rhl_pc","b_rhm_pc","b_rt_pc",
    "b_log_rho_c","b_log_rho_hm","b_log_trh_yr","b_t_diss_gyr",
    "b_mf_slope","b_sigma0_kms","b_v_esc_kms","b_eta_c","b_eta_h",
    "b_a_rot_kms","b_p_rot_pct","b_n_rv","b_n_pm",
    # APOGEE columns
    "a_feh","a_rv_kms","a_rv_err","a_r_sun_kpc","a_r_gc_kpc",
    "a_mass_1e4_msun","a_r_jacobi_deg","a_n_members",
]

with open(OUT + "harris_gc_corpus_v1.4.0_flat.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    for c in corpus["clusters"]:
        ge = c.get("gaia_edr3") or {}
        b  = c.get("baumgardt2023") or {}
        a  = c.get("apogee_dr17") or {}
        row = {
            "cluster_id":       c["cluster_id"],
            "alt_name":         c["alt_name"],
            "l_deg":            c["position"]["l_deg"],
            "b_deg":            c["position"]["b_deg"],
            "harris_r_sun_kpc": c["distances"]["r_sun_kpc"],
            "harris_r_gc_kpc":  c["distances"]["r_gc_kpc"],
            "harris_x_kpc":     c["distances"]["x_kpc"],
            "harris_y_kpc":     c["distances"]["y_kpc"],
            "harris_z_kpc":     c["distances"]["z_kpc"],
            "feh":              c["metallicity"]["feh"],
            "ebv":              c["metallicity"]["ebv"],
            "m_v_t":            c["photometry"]["m_v_t"],
            "dist_mod":         c["photometry"]["dist_mod"],
            "king_c":           c["structure"]["king_concentration"],
            "core_collapsed":   c["structure"]["core_collapsed"],
            "r_core_arcmin":    c["structure"]["r_core_arcmin"],
            "r_half_arcmin":    c["structure"]["r_half_arcmin"],
            "r_half_kpc":       c["structure"]["r_half_kpc"],
            "log_rho0":         c["structure"]["log_rho0"],
            "log_t_rc_yr":      c["dynamics"]["log_t_rc_yr"],
            "log_t_rh_yr":      c["dynamics"]["log_t_rh_yr"],
            "v_r_harris_kms":   c["kinematics"]["v_r_kms"],
            "inner_galaxy":     c["flags"]["inner_galaxy"],
            "sgr_stream":       c["flags"]["sgr_stream"],
            "gaia_mu_alpha":    ge.get("mu_alpha_mas_yr"),
            "gaia_mu_alpha_err":ge.get("mu_alpha_err"),
            "gaia_mu_delta":    ge.get("mu_delta_mas_yr"),
            "gaia_mu_delta_err":ge.get("mu_delta_err"),
            "gaia_corr_mu":     ge.get("corr_mu"),
            "gaia_parallax_mas":ge.get("parallax_mas"),
            "gaia_parallax_err":ge.get("parallax_err"),
            "gaia_n_members":   ge.get("n_members_gaia"),
            "b_r_sun_kpc":      b.get("r_sun_kpc"),
            "b_r_sun_err":      b.get("r_sun_err"),
            "b_r_gc_kpc":       b.get("r_gc_kpc"),
            "b_r_gc_err":       b.get("r_gc_err"),
            "b_rv_kms":         b.get("rv_kms"),
            "b_rv_err":         b.get("rv_err"),
            "b_mu_alpha":       b.get("mu_alpha_mas_yr"),
            "b_mu_alpha_err":   b.get("mu_alpha_err"),
            "b_mu_delta":       b.get("mu_delta_mas_yr"),
            "b_mu_delta_err":   b.get("mu_delta_err"),
            "b_x_kpc":          b.get("x_kpc"),
            "b_y_kpc":          b.get("y_kpc"),
            "b_z_kpc":          b.get("z_kpc"),
            "b_u_kms":          b.get("u_kms"),
            "b_v_kms":          b.get("v_kms"),
            "b_w_kms":          b.get("w_kms"),
            "b_r_peri_kpc":     b.get("r_peri_kpc"),
            "b_r_apo_kpc":      b.get("r_apo_kpc"),
            "b_mass_msun":      b.get("mass_msun"),
            "b_mass_err":       b.get("mass_err"),
            "b_v_mag":          b.get("v_mag"),
            "b_ml_v":           b.get("ml_v"),
            "b_rc_pc":          b.get("rc_pc"),
            "b_rhl_pc":         b.get("rhl_pc"),
            "b_rhm_pc":         b.get("rhm_pc"),
            "b_rt_pc":          b.get("rt_pc"),
            "b_log_rho_c":      b.get("log_rho_c"),
            "b_log_rho_hm":     b.get("log_rho_hm"),
            "b_log_trh_yr":     b.get("log_trh_yr"),
            "b_t_diss_gyr":     b.get("t_diss_gyr"),
            "b_mf_slope":       b.get("mf_slope"),
            "b_sigma0_kms":     b.get("sigma0_kms"),
            "b_v_esc_kms":      b.get("v_esc_kms"),
            "b_eta_c":          b.get("eta_c"),
            "b_eta_h":          b.get("eta_h"),
            "b_a_rot_kms":      b.get("a_rot_kms"),
            "b_p_rot_pct":      b.get("p_rot_pct"),
            "b_n_rv":           b.get("n_rv"),
            "b_n_pm":           b.get("n_pm"),
            "a_feh":            a.get("feh_apogee"),
            "a_rv_kms":         a.get("rv_mean_kms"),
            "a_rv_err":         a.get("rv_err"),
            "a_r_sun_kpc":      a.get("r_sun_kpc"),
            "a_r_gc_kpc":       a.get("r_gc_kpc"),
            "a_mass_1e4_msun":  a.get("mass_1e4_msun"),
            "a_r_jacobi_deg":   a.get("r_jacobi_deg"),
            "a_n_members":      a.get("n_members"),
        }
        w.writerow(row)

# ── TYPE AUDIT ────────────────────────────────────────────────────────────────
test = next(c for c in corpus["clusters"] if c["cluster_id"]=="NGC 104")
a = test["apogee_dr17"]
assert type(a["feh_apogee"])==float
assert type(a["rv_mean_kms"])==float
assert type(a["n_members"])==int
print("Type audit passed")

import os
print(f"\nv1.4.0 complete:")
print(f"  JSON:  {os.path.getsize(OUT + 'harris_gc_corpus_v1.4.0.json')/1024:.1f} KB")
print(f"  JSONL: {os.path.getsize(OUT + 'harris_gc_corpus_v1.4.0.jsonl')/1024:.1f} KB")
print(f"  CSV:   {os.path.getsize(OUT + 'harris_gc_corpus_v1.4.0_flat.csv')/1024:.1f} KB")
print(f"\nNGC 104 APOGEE: feh={a['feh_apogee']}, rv={a['rv_mean_kms']} km/s, n_members={a['n_members']}")

# Final coverage summary
has_harris  = sum(1 for c in corpus["clusters"] if c["metallicity"]["feh"] is not None)
has_gaia    = sum(1 for c in corpus["clusters"] if c.get("gaia_edr3") and c["gaia_edr3"].get("mu_alpha_mas_yr") is not None)
has_b       = sum(1 for c in corpus["clusters"] if c.get("baumgardt2023") and c["baumgardt2023"].get("mass_msun") is not None)
has_apogee  = sum(1 for c in corpus["clusters"] if c.get("apogee_dr17") and c["apogee_dr17"].get("feh_apogee") is not None)
print(f"\nCoverage:")
print(f"  Harris photometry/structure : {has_harris}/174")
print(f"  Vasiliev 2021 Gaia PM       : {has_gaia}/174")
print(f"  Baumgardt 2023 N-body       : {has_b}/174")
print(f"  APOGEE DR17 chemistry       : {has_apogee}/174")

# Count total non-null data points
def count_nonnull(obj):
    if isinstance(obj, dict):
        return sum(count_nonnull(v) for k,v in obj.items() if k != 'provenance')
    elif isinstance(obj, list):
        return sum(count_nonnull(v) for v in obj)
    elif obj is not None and obj != '':
        return 1
    return 0

total_pts = sum(count_nonnull(c) for c in corpus["clusters"])
# add cluster_id and alt_name
total_pts += sum(1 for c in corpus["clusters"] if c.get("cluster_id"))
total_pts += sum(1 for c in corpus["clusters"] if c.get("alt_name"))
print(f"\nTotal non-null data points: {total_pts:,}")
