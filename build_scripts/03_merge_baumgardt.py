"""
Merge Baumgardt et al. (2023) v4 database into harris_gc_corpus_v1.1.json
Adds a 'baumgardt2023' block to each cluster.

Sources:
  Orbits table:    https://people.smp.uq.edu.au/HolgerBaumgardt/globular/orbits.html
  Structure table: https://people.smp.uq.edu.au/HolgerBaumgardt/globular/parameter.html

Data-type standards (matching SPARC/Harris corpus):
  - All numerics: native Python float or int (never str)
  - Missing/unmeasured: None  (→ JSON null)
  - Errors stored as separate _err float fields
  - No unit conversion unless documented in schema_notes
"""

import json, re, csv

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
    """Parse float or return None. Handles '—' and empty strings."""
    if s is None: return None
    s = str(s).strip().replace('−','-').replace('\u2212','-')
    if not s or s in ('—','–','-',''):  return None
    # Strip trailing text like 'kpc', 'Gyr' etc. — just get the number
    m = re.match(r'^([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)', s)
    if m: return float(m.group(1))
    return None

def parse_pm(s):
    """Parse 'value ± err' string → (float|None, float|None)"""
    if not s or s.strip() in ('—','–'): return None, None
    s = s.strip().replace('±','±').replace('\u00b1','±').replace('−','-').replace('\u2212','-')
    if '±' in s:
        parts = s.split('±')
        return fv(parts[0]), fv(parts[1])
    return fv(s), None

def parse_mass(s):
    """Parse '8.53 ± 0.05 · 10^5' style strings → (float|None, float|None) in solar masses"""
    if not s or s.strip() in ('—','–'): return None, None
    s = s.strip().replace('\u00b7','*').replace('·','*').replace('\u00d7','*').replace('×','*')
    s = s.replace('\u2212','-').replace('−','-')
    # Pattern: value ± err * 10^N or value * 10^N
    m = re.match(r'([+-]?\d+\.?\d*)\s*(?:±\s*([+-]?\d+\.?\d*))?\s*[*·×]\s*10\^?(\d+)', s)
    if m:
        val, err, exp = m.groups()
        factor = 10**int(exp)
        v = float(val) * factor if val else None
        e = float(err) * factor if err else None
        return v, e
    # Fallback: try plain number
    return fv(s), None

# ── BAUMGARDT ORBITS DATA ─────────────────────────────────────────────────────
# Tab-separated: name, ra, dec, l, b, r_sun±err, r_gc±err, rv±err,
#                mu_a±err, mu_d±err, rho_mu, X±err, Y±err, Z±err,
#                U±err, V±err, W±err, r_peri±err, r_apo±err
# Parsed from the HTML table - values extracted manually from the fetched content

RAW_ORBITS = _load_table("baumgardt2023_orbits", 32, 32)

# Structural parameters — abbreviated (key fields only, from the HTML above)
# Full columns: name, ra, dec, r_sun±err, r_gc±err, n_rv, n_pm, mass±err,
#   V±err, ml_v±err, rc_pc, rhl_pc, rhm_pc, rt_pc,
#   log_rho_c, log_rho_hm, log_trh, log_mini, t_diss,
#   mf_range_lo, mf_range_hi, mf_slope±err,
#   sigma0, v_esc, eta_c, eta_h, a_rot±err, p_rot
RAW_STRUCT = _load_table("baumgardt2023_structure", 34, 35)

# ── ID MAP: Baumgardt name → Harris cluster_id ────────────────────────────────
B_MAP = {
    "ESO 452-SC11": "1636-283",
    "Terzan 3": "Terzan 3",   "Ter 3": "Terzan 3",
    "Terzan 2": "Terzan 2",   "Ter 2": "Terzan 2",
    "Terzan 4": "Terzan 4",   "Ter 4": "Terzan 4",
    "Terzan 5": "Terzan 5",   "Ter 5": "Terzan 5",
    "Terzan 6": "Terzan 6",   "Ter 6": "Terzan 6",
    "Terzan 7": "Terzan 7",   "Ter 7": "Terzan 7",
    "Terzan 8": "Terzan 8",   "Ter 8": "Terzan 8",
    "Terzan 9": "Terzan 9",   "Ter 9": "Terzan 9",
    "Terzan 10":"Terzan 10",  "Ter 10":"Terzan 10",
    "Terzan 12":"Terzan 12",  "Ter 12":"Terzan 12",
    "Terzan 1": "Terzan 1",   "Ter 1": "Terzan 1",
    "IC 1276":  "IC 1276",    "Pal 7": "IC 1276",
    "HP 1":     "HP 1",
    "Lynga 7":  "Lynga 7",
    "Ton 2":    "Ton 2",
    "Djorg 1":  "Djorg 1",    "Djor 1":"Djorg 1",
    "Djorg 2":  "Djorg 2",    "Djor 2":"Djorg 2",
    "VVV-CL001":"VVV CL001",
    "FSR 1716": "FSR 1716",
    "FSR 1735": "FSR 1735",
    "FSR 1758": "FSR 1758",
    "BH 261":   "BH 261",
}

def resolve_id(name):
    return B_MAP.get(name, name)

def parse_orbits():
    out = {}
    for line in RAW_ORBITS.strip().splitlines():
        p = line.split('\t')
        if len(p) < 32: continue
        cid = resolve_id(p[0].strip())
        out[cid] = {
            "ra_deg":       fv(p[1]),  "dec_deg":      fv(p[2]),
            "l_deg":        fv(p[3]),  "b_deg":        fv(p[4]),
            "r_sun_kpc":    fv(p[5]),  "r_sun_err":    fv(p[6]),
            "r_gc_kpc":     fv(p[7]),  "r_gc_err":     fv(p[8]),
            "rv_kms":       fv(p[9]),  "rv_err":       fv(p[10]),
            "mu_alpha_mas_yr":fv(p[11]),"mu_alpha_err":fv(p[12]),
            "mu_delta_mas_yr":fv(p[13]),"mu_delta_err":fv(p[14]),
            "rho_mu":       fv(p[15]),
            "x_kpc":        fv(p[16]), "x_err":        fv(p[17]),
            "y_kpc":        fv(p[18]), "y_err":        fv(p[19]),
            "z_kpc":        fv(p[20]), "z_err":        fv(p[21]),
            "u_kms":        fv(p[22]), "u_err":        fv(p[23]),
            "v_kms":        fv(p[24]), "v_err":        fv(p[25]),
            "w_kms":        fv(p[26]), "w_err":        fv(p[27]),
            "r_peri_kpc":   fv(p[28]), "r_peri_err":   fv(p[29]),
            "r_apo_kpc":    fv(p[30]), "r_apo_err":    fv(p[31]),
        }
    return out

def parse_struct():
    out = {}
    for line in RAW_STRUCT.strip().splitlines():
        p = line.split('\t')
        if len(p) < 28: continue
        cid = resolve_id(p[0].strip())
        # Columns: name,ra,dec,r_sun,r_sun_err,r_gc,r_gc_err,n_rv,n_pm,
        #          mass,mass_err, V,V_err, MLv,MLv_err,
        #          rc_pc,rhl_pc,rhm_pc,rt_pc,
        #          log_rho_c,log_rho_hm,log_trh,log_mini,t_diss_gyr,
        #          mf_lo,mf_hi,mf_slope,mf_slope_err,
        #          sigma0_kms,v_esc_kms,eta_c,eta_h,
        #          a_rot,a_rot_err,p_rot  (last 3 may be absent)
        def fi(i): return int(float(p[i])) if i < len(p) and p[i].strip() else None
        def ff(i): return fv(p[i]) if i < len(p) else None
        out[cid] = {
            "r_sun_kpc":    ff(3), "r_sun_err":    ff(4),
            "r_gc_kpc":     ff(5), "r_gc_err":     ff(6),
            "n_rv":         fi(7), "n_pm":         fi(8),
            "mass_msun":    ff(9), "mass_err":     ff(10),
            "v_mag":        ff(11),"v_mag_err":    ff(12),
            "ml_v":         ff(13),"ml_v_err":     ff(14),
            "rc_pc":        ff(15),"rhl_pc":       ff(16),
            "rhm_pc":       ff(17),"rt_pc":        ff(18),
            "log_rho_c":    ff(19),"log_rho_hm":  ff(20),
            "log_trh_yr":   ff(21),"log_mini_msun":ff(22),
            "t_diss_gyr":   ff(23),
            "mf_range_lo":  ff(24),"mf_range_hi":  ff(25),
            "mf_slope":     ff(26),"mf_slope_err": ff(27),
            "sigma0_kms":   ff(28),"v_esc_kms":    ff(29),
            "eta_c":        ff(30),"eta_h":        ff(31),
            "a_rot_kms":    ff(32) if len(p)>32 else None,
            "a_rot_err":    ff(33) if len(p)>33 else None,
            "p_rot_pct":    ff(34) if len(p)>34 else None,
        }
    return out

orb = parse_orbits()
strc = parse_struct()
print(f"Orbits parsed: {len(orb)}")
print(f"Structure parsed: {len(strc)}")

# ── LOAD V1.1 CORPUS ──────────────────────────────────────────────────────────
with open(OUT + "harris_gc_corpus_v1.1.json") as f:
    corpus = json.load(f)
existing_ids = {c["cluster_id"] for c in corpus["clusters"]}

# ── MERGE ─────────────────────────────────────────────────────────────────────
PROV_B = {
    "source":    "Baumgardt et al. 2023 (v4 database)",
    "url":       "https://people.smp.uq.edu.au/HolgerBaumgardt/globular/",
    "version":   "v4 (March 2023)",
    "notes":     "N-body fits to RVs + Gaia DR3 PMs + HST mass functions. Distances from Baumgardt & Vasiliev (2021). Orbital integration in Irrgang et al. (2013) potential.",
    "citations": [
        "Baumgardt & Hilker 2018, MNRAS 478, 1520",
        "Baumgardt & Vasiliev 2021, MNRAS 505, 5957",
        "Baumgardt et al. 2023, arXiv:2303.01636",
        "Sollima, Baumgardt & Hilker 2019, MNRAS 485, 1460",
    ]
}

EMPTY_B = {k: None for k in [
    "ra_deg","dec_deg","l_deg","b_deg",
    "r_sun_kpc","r_sun_err","r_gc_kpc","r_gc_err",
    "rv_kms","rv_err","mu_alpha_mas_yr","mu_alpha_err",
    "mu_delta_mas_yr","mu_delta_err","rho_mu",
    "x_kpc","x_err","y_kpc","y_err","z_kpc","z_err",
    "u_kms","u_err","v_kms","v_err","w_kms","w_err",
    "r_peri_kpc","r_peri_err","r_apo_kpc","r_apo_err",
    "n_rv","n_pm","mass_msun","mass_err","v_mag","v_mag_err",
    "ml_v","ml_v_err","rc_pc","rhl_pc","rhm_pc","rt_pc",
    "log_rho_c","log_rho_hm","log_trh_yr","log_mini_msun","t_diss_gyr",
    "mf_range_lo","mf_range_hi","mf_slope","mf_slope_err",
    "sigma0_kms","v_esc_kms","eta_c","eta_h",
    "a_rot_kms","a_rot_err","p_rot_pct",
]}

n_matched = 0
for c in corpus["clusters"]:
    cid = c["cluster_id"]
    o = orb.get(cid, {})
    s = strc.get(cid, {})
    if o or s:
        n_matched += 1
        b = {**EMPTY_B, **o, **s, "provenance": PROV_B}
    else:
        b = {**EMPTY_B, "provenance": None}
    c["baumgardt2023"] = b

print(f"Clusters with Baumgardt data: {n_matched}")

# ── NEW B-ONLY CLUSTERS ───────────────────────────────────────────────────────
# Gran 2, Gran 3 / Patchick 125, Gran 5, Patchick 126, Sagittarius II, VVV-CL160
# These are in Baumgardt but not in Harris or V21
NEW_B_CLUSTERS = {
    "Gran 2":       {"ra":257.890, "dec":-24.849},
    "Gran 3":       {"ra":256.256, "dec":-35.496},
    "Gran 5":       {"ra":267.228, "dec":-24.170},
    "Patchick 126": {"ra":256.411, "dec":-47.342},
    "Sagittarius II":{"ra":298.169,"dec":-22.066},
    "VVV-CL160":    {"ra":271.738, "dec":-20.011},
}
# These are in RAW_ORBITS: Gran 3, Gran 2, Patchick 126, Gran 5, VVV-CL160
# Sagittarius II is not in our parsed tables — skip for now

new_b = 0
for name in ["Gran 2", "Gran 3", "Gran 5", "Patchick 126", "VVV-CL160"]:
    if name not in existing_ids:
        o = orb.get(name, {})
        s = strc.get(name, {})
        if not o and not s: continue
        b = {**EMPTY_B, **o, **s, "provenance": PROV_B}
        rec = {
            "cluster_id": name, "alt_name": None,
            "position": {"ra_hms":None,"dec_dms":None,
                         "l_deg": o.get("l_deg"), "b_deg": o.get("b_deg")},
            "distances":  {k:None for k in ["r_sun_kpc","r_gc_kpc","x_kpc","y_kpc","z_kpc"]},
            "metallicity":{"feh":None,"feh_weight":None,"ebv":None},
            "photometry": {"v_hb":None,"dist_mod":None,"v_t":None,"m_v_t":None,
                           "spectral_type":None,"ellipticity":None,
                           "colors":{"ub":None,"bv":None,"vr":None,"vi":None}},
            "kinematics": {"v_r_kms":o.get("rv_kms"),"v_r_err":o.get("rv_err"),
                           "v_lsr_kms":None,"sig_v_kms":None,"sig_v_err":None},
            "structure":  {k:None for k in ["king_concentration","core_collapsed",
                           "core_collapse_uncertain","r_core_arcmin","r_half_arcmin",
                           "r_core_kpc","r_half_kpc","mu_v_central","log_rho0"]},
            "dynamics":   {"log_t_rc_yr":None,"log_t_rh_yr":None},
            "flags":      {"inner_galaxy": bool(o.get("r_gc_kpc") and o.get("r_gc_kpc") < 3.0),
                           "sgr_stream": False},
            "gaia_edr3":  {k: None for k in ["ra_deg","dec_deg","mu_alpha_mas_yr","mu_alpha_err",
                           "mu_delta_mas_yr","mu_delta_err","corr_mu","parallax_mas",
                           "parallax_err","plummer_r0_arcmin","n_members_gaia","provenance"]},
            "baumgardt2023": b,
            "provenance": {"source":"Baumgardt et al. 2023 (not in Harris 2010 or Vasiliev 2021)",
                           "url":"https://people.smp.uq.edu.au/HolgerBaumgardt/globular/",
                           "citation":"Baumgardt et al. 2023"}
        }
        # fix booleans
        rec["structure"]["core_collapsed"] = False
        rec["structure"]["core_collapse_uncertain"] = False
        corpus["clusters"].append(rec)
        new_b += 1
        print(f"  Appended new cluster: {name}")

# ── UPDATE METADATA ───────────────────────────────────────────────────────────
total = len(corpus["clusters"])
corpus["metadata"]["version"] = "1.2"
corpus["metadata"]["title"]   = "Milky Way Globular Cluster Corpus v1.2"
corpus["metadata"]["n_clusters"] = total
corpus["metadata"]["description"] = (
    "Harris (1996, 2010 ed.) 157-cluster catalog merged with Vasiliev & Baumgardt (2021) "
    "Gaia EDR3 proper motions (v1.1) and Baumgardt et al. (2023) N-body structural/orbital "
    "parameters (v1.2). Each cluster record carries up to three independent data blocks: "
    "harris (photometric/structural), gaia_edr3 (Gaia kinematics), and baumgardt2023 "
    "(N-body masses, radii, velocities, orbital integrals)."
)
corpus["metadata"]["n_baumgardt_only"] = new_b
corpus["metadata"]["sources"].append({
    "label":    "baumgardt2023_v4",
    "citation": "Baumgardt et al. 2023 (v4 database, March 2023)",
    "url":      "https://people.smp.uq.edu.au/HolgerBaumgardt/globular/",
})
corpus["metadata"]["schema_notes"]["baumgardt2023"] = (
    "N-body fit parameters from Baumgardt et al. (2023) v4 database. "
    "Distances (r_sun_kpc, r_gc_kpc) are Baumgardt & Vasiliev (2021) values — more precise than Harris. "
    "Radii rc_pc/rhl_pc/rhm_pc/rt_pc are in parsecs (not arcmin). "
    "3D space velocities U/V/W in km/s in Galactocentric frame. "
    "r_peri_kpc/r_apo_kpc are orbital pericenter/apocenter in Irrgang et al. (2013) potential. "
    "log_trh_yr = log10(half-mass relaxation time/yr). "
    "mf_slope = global IMF slope (Salpeter = -2.3). "
    "sigma0_kms = central 1D velocity dispersion. "
    "a_rot_kms/p_rot_pct = Sollima et al. (2019) rotation amplitude and detection probability. "
    "eta_c/eta_h = Trenti & van der Marel (2013) mass segregation parameters."
)

with open(OUT + "harris_gc_corpus_v1.2.json","w") as f:
    json.dump(corpus, f, indent=2)
print(f"\nv1.2 written: {total} clusters")

# ── FLAT CSV (all three data blocks) ─────────────────────────────────────────
fields = [
    # identity
    "cluster_id","alt_name","l_deg","b_deg",
    # Harris distances
    "harris_r_sun_kpc","harris_r_gc_kpc","harris_x_kpc","harris_y_kpc","harris_z_kpc",
    # Harris metallicity/photometry
    "feh","ebv","m_v_t","dist_mod",
    # Harris structure
    "king_c","core_collapsed","r_core_arcmin","r_half_arcmin","r_half_kpc","log_rho0",
    # Harris dynamics
    "log_t_rc_yr","log_t_rh_yr",
    # Harris kinematics
    "v_r_harris_kms",
    # flags
    "inner_galaxy","sgr_stream",
    # Gaia EDR3 (Vasiliev 2021)
    "gaia_mu_alpha","gaia_mu_alpha_err","gaia_mu_delta","gaia_mu_delta_err",
    "gaia_corr_mu","gaia_parallax_mas","gaia_parallax_err","gaia_n_members",
    # Baumgardt 2023 - distances
    "b_r_sun_kpc","b_r_sun_err","b_r_gc_kpc","b_r_gc_err",
    # Baumgardt 2023 - kinematics
    "b_rv_kms","b_rv_err","b_mu_alpha","b_mu_alpha_err","b_mu_delta","b_mu_delta_err",
    "b_x_kpc","b_y_kpc","b_z_kpc","b_u_kms","b_v_kms","b_w_kms",
    "b_r_peri_kpc","b_r_apo_kpc",
    # Baumgardt 2023 - structural
    "b_mass_msun","b_mass_err","b_v_mag","b_ml_v",
    "b_rc_pc","b_rhl_pc","b_rhm_pc","b_rt_pc",
    "b_log_rho_c","b_log_rho_hm","b_log_trh_yr","b_t_diss_gyr",
    "b_mf_slope","b_sigma0_kms","b_v_esc_kms",
    "b_eta_c","b_eta_h","b_a_rot_kms","b_p_rot_pct",
    "b_n_rv","b_n_pm",
]

import csv
with open(OUT + "harris_gc_corpus_v1.2_flat.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    for c in corpus["clusters"]:
        ge = c.get("gaia_edr3") or {}
        b  = c.get("baumgardt2023") or {}
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
        }
        w.writerow(row)

# ── TYPE AUDIT ────────────────────────────────────────────────────────────────
test = next(c for c in corpus["clusters"] if c["cluster_id"]=="NGC 104")
b = test["baumgardt2023"]
for k in ["mass_msun","rc_pc","sigma0_kms","rv_kms","r_peri_kpc"]:
    v = b.get(k)
    if v is not None:
        assert type(v)==float, f"{k}={v} is {type(v)}, not float"
assert type(b["n_rv"])==int, "n_rv not int"
print("Type audit passed")

print(f"\nNGC 104 spot check:")
print(f"  mass_msun={b['mass_msun']:.0f}  sigma0={b['sigma0_kms']}  rc_pc={b['rc_pc']}")
print(f"  r_peri={b['r_peri_kpc']}  r_apo={b['r_apo_kpc']}")
print(f"  mf_slope={b['mf_slope']}  p_rot={b['p_rot_pct']}%")

import os
print(f"\nJSON: {os.path.getsize(OUT + 'harris_gc_corpus_v1.2.json')/1024:.1f} KB")
print(f"CSV:  {os.path.getsize(OUT + 'harris_gc_corpus_v1.2_flat.csv')/1024:.1f} KB")
