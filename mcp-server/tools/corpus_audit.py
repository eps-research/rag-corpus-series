#!/usr/bin/env python3
"""Definitional audit of the five served corpora.

For every derived field the audit records (a) its definition, (b) its inputs,
(c) whether those inputs are independent measurements, and (d) a reproduction
check: the field is recomputed from its inputs and compared with the stored
value. It was written in response to the KROSS omega defect (August 2026), in
which an estimator that needs two independently measured rotation-curve rings
was fed boundary points derived from integrated quantities.

Usage:  python tools/corpus_audit.py [--data-dir DIR] [--out audit_report]
Writes <out>.json (machine-readable) and <out>.md (table), and exits 1 if any
reproduction check fails.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from astro_rag_mcp.config import CORPORA, resolve_data_layout  # noqa: E402
from astro_rag_mcp.omega import check_corpus  # noqa: E402

G_KPC = 4.30091e-6          # kpc (km/s)^2 / Msun
ARCMIN_RAD = math.pi / 10800


def load(layout, key):
    doc = json.loads(layout.corpus_path(CORPORA[key]).read_text(encoding="utf-8"))
    return next(v for v in doc.values() if isinstance(v, list))


class Check:
    def __init__(self, corpus, field, definition, inputs, independent, tol):
        self.corpus, self.field, self.definition = corpus, field, definition
        self.inputs, self.independent, self.tol = inputs, independent, tol
        self.n = self.fail = 0
        self.examples: list[str] = []

    def test(self, name, stored, recomputed, tol=None):
        if stored is None or recomputed is None:
            return
        try:
            stored, recomputed = float(stored), float(recomputed)
        except (TypeError, ValueError):
            return
        if not (math.isfinite(stored) and math.isfinite(recomputed)):
            return
        self.n += 1
        t = self.tol if tol is None else tol
        if abs(stored - recomputed) > t(stored) if callable(t) else abs(stored - recomputed) > t:
            self.fail += 1
            if len(self.examples) < 5:
                self.examples.append(f"{name}: stored {stored:g}, recomputed {recomputed:g}")

    def row(self):
        return {"corpus": self.corpus, "field": self.field, "definition": self.definition,
                "inputs": self.inputs, "inputs_independent": self.independent,
                "checked": self.n, "failed": self.fail, "examples": self.examples}


def rel(frac, floor=0.0):
    return lambda v: max(abs(v) * frac, floor)


def audit_curves(key, recs, vcols, checks, notes):
    vcol = "/".join(vcols)
    c_n = Check(key, "n_points", "number of rows in the stored curve", "data", True, 0)
    c_max = Check(key, "vrot_max_kms", "max of stored velocities", f"data.{vcol}", True, 0.006)
    c_mean = Check(key, "vrot_mean_kms", "mean of stored velocities", f"data.{vcol}", True, 0.006)
    c_rmin = Check(key, "r_min_kpc", "smallest stored radius", "data.Rad", True, 0.006)
    c_rmax = Check(key, "r_max_kpc", "largest stored radius", "data.Rad", True, 0.006)
    estimated, empty = [], []
    for r in recs:
        col = next((c for c in vcols if any(x.get(c) is not None for x in r.get("data") or [])), None)
        rows = [x for x in r.get("data") or [] if col and x.get(col) is not None and x.get("Rad") is not None]
        if not rows:
            empty.append(r["galaxy"])
            continue
        v = [float(x[col]) for x in rows]
        rr = [float(x["Rad"]) for x in rows]
        c_n.test(r["galaxy"], r.get("n_points"), len(r.get("data") or []))
        c_max.test(r["galaxy"], r.get("vrot_max_kms"), max(v))
        c_mean.test(r["galaxy"], r.get("vrot_mean_kms"), statistics.fmean(v))
        if len(rows) == 1 and any("are estimates" in i for i in r.get("known_issues") or []):
            estimated.append(r["galaxy"])      # documented single-point estimate, not a measured extent
        else:
            c_rmin.test(r["galaxy"], r.get("r_min_kpc"), min(rr))
            c_rmax.test(r["galaxy"], r.get("r_max_kpc"), max(rr))
    checks += [c_n, c_max, c_mean, c_rmin, c_rmax]
    if empty:
        notes.append({"corpus": key, "note": f"{len(empty)} records have no rotation-curve rows "
                      f"(e.g. {', '.join(empty[:3])}); curve-derived fields are not defined for them."})
    if estimated:
        notes.append({"corpus": key, "note": f"{len(estimated)} single-point records (profile-width estimates) "
                      "carry r_min_kpc/r_max_kpc that are documented estimates, not measured radii "
                      "(r_min_kpc = 0.1 r_max_kpc); excluded from the extent checks and reported here."})


def audit(layout):
    checks: list[Check] = []
    notes: list[dict] = []

    # ── v7: HI rotation curves (observed rows only since v7.2) ──
    v7 = load(layout, "v7")
    audit_curves("v7", v7, ("Vobs", "Vrot"), checks, notes)

    # ── dwarf ──
    dw = load(layout, "dwarf")
    audit_curves("dwarf", dw, ("Vrot",), checks, notes)
    # LVHIS log_mdyn and the ratio are transcribed from Koribalski et al. (2019) Table 9,
    # which uses its own radius; this is a consistency check, not a reproduction.
    c = Check("dwarf", "log_mdyn", "catalogue value; consistent with log10(V_max^2 R_max / G)",
              "vrot_max_kms, r_max_kpc", True, 0.15)
    c2 = Check("dwarf", "mhi_mdyn_ratio", "catalogue value; consistent with 10^(mhi_log - log_mdyn)",
               "mhi_log_msun, log_mdyn", True, rel(0.15, 0.003))
    for r in dw:
        if r.get("vrot_max_kms") and r.get("r_max_kpc"):
            c.test(r["galaxy"], r.get("log_mdyn"), math.log10(r["vrot_max_kms"] ** 2 * r["r_max_kpc"] / G_KPC))
        if r.get("mhi_log_msun") is not None and r.get("log_mdyn") is not None:
            c2.test(r["galaxy"], r.get("mhi_mdyn_ratio"), 10 ** (r["mhi_log_msun"] - r["log_mdyn"]))
    checks += [c, c2]
    n_ready = sum(1 for r in dw if r.get("omega_ready"))
    notes.append({"corpus": "dwarf", "note": f"omega_ready is true for {n_ready} of {len(dw)} records, all "
                  "LITTLE THINGS curves that contain unmarked model rows (flagged by the server); "
                  "no omega values are stored in Dwarf v1.0."})

    # ── gc: Harris (2010) derived columns ──
    gc = load(layout, "gc")
    cd = Check("gc", "distances.r_sun_kpc", "sqrt(X^2+Y^2+Z^2) (Harris heliocentric X,Y,Z)", "x_kpc, y_kpc, z_kpc",
               True, 0.11)
    cm = Check("gc", "photometry.dist_mod", "(m-M)_V = 5 log10(R_sun/10 pc) + 3.1 E(B-V)", "r_sun_kpc, ebv", True, 0.06)
    crc = Check("gc", "structure.r_core_kpc", "r_core[arcmin] x R_sun (small angle)", "r_core_arcmin, r_sun_kpc", True,
                rel(0.15, 0.00015))
    crh = Check("gc", "structure.r_half_kpc", "r_half[arcmin] x R_sun (small angle)", "r_half_arcmin, r_sun_kpc", True,
                rel(0.15, 0.00015))
    cmv = Check("gc", "photometry.m_v_t", "V_t - (m-M)_V", "v_t, dist_mod", True, 0.02)
    for r in gc:
        n = r["cluster_id"]
        d, ph, st, met = r.get("distances", {}), r.get("photometry", {}), r.get("structure", {}), r.get("metallicity", {})
        if None not in (d.get("x_kpc"), d.get("y_kpc"), d.get("z_kpc")):
            cd.test(n, d.get("r_sun_kpc"), math.sqrt(d["x_kpc"] ** 2 + d["y_kpc"] ** 2 + d["z_kpc"] ** 2))
        if d.get("r_sun_kpc") and met.get("ebv") is not None:
            cm.test(n, ph.get("dist_mod"), 5 * math.log10(d["r_sun_kpc"] * 100) + 3.1 * met["ebv"])
        if d.get("r_sun_kpc"):
            if st.get("r_core_arcmin") is not None:
                crc.test(n, st.get("r_core_kpc"), st["r_core_arcmin"] * ARCMIN_RAD * d["r_sun_kpc"])
            if st.get("r_half_arcmin") is not None:
                crh.test(n, st.get("r_half_kpc"), st["r_half_arcmin"] * ARCMIN_RAD * d["r_sun_kpc"])
        if ph.get("v_t") is not None and ph.get("dist_mod") is not None:
            cmv.test(n, ph.get("m_v_t"), ph["v_t"] - ph["dist_mod"])
    checks += [cd, cm, crc, crh, cmv]

    # ── intz: KROSS + KMOS3D catalogue products ──
    iz = load(layout, "intz")
    cvs = Check("intz", "kinematics.v_over_sigma", "Vc / sigma0", "Vc_kms, sigma0_kms", True, rel(0.01, 0.002))
    clm = Check("intz", "stellar_properties.log_mass_msun", "log10(mass_msun)", "mass_msun", True, 0.002)
    cdl = Check("intz", "cosmology_derived.D_L_mpc", "(1+z)^2 D_A (Etherington relation)", "z_spec, D_A_mpc", True,
                rel(0.001, 0.5))
    for r in iz:
        ids = r.get("identifiers", {}); n = ids.get("name") or ids.get("id") or str(ids)
        k, sp, cz, z = r.get("kinematics", {}), r.get("stellar_properties", {}), r.get("cosmology_derived", {}), r.get("redshift", {})
        if k.get("Vc_kms") and k.get("sigma0_kms"):
            cvs.test(n, k.get("v_over_sigma"), k["Vc_kms"] / k["sigma0_kms"])
        if sp.get("mass_msun"):
            clm.test(n, sp.get("log_mass_msun"), math.log10(sp["mass_msun"]))
        if z.get("z_spec") is not None and cz.get("D_A_mpc"):
            cdl.test(n, cz.get("D_L_mpc"), (1 + z["z_spec"]) ** 2 * cz["D_A_mpc"])
    checks += [cvs, clm, cdl]
    scal = sum(1 for r in iz if (r.get("baryonic") or {}).get("v_bary_quality") == "statistical")
    extrap = sum(1 for r in iz if (r.get("kinematics") or {}).get("extrap_flag") == 1)
    notes.append({"corpus": "intz", "note": f"baryonic fields of {scal} of {len(iz)} records come from population "
                  "scaling relations (Tacconi et al. 2018), not per-galaxy measurements; they must not be used "
                  "where an independent measurement is required."})
    notes.append({"corpus": "intz", "note": f"Vc is extrapolated beyond the data (extrap_flag=1) for {extrap} of "
                  f"{len(iz)} records (KROSS catalogue flag)."})

    # ── z1: ALPINE per-ring products ──
    z1 = load(layout, "z1")
    cmd = Check("z1", "data.Mdyn_msun", "Vrot^2 R / G per ring", "data.Vrot_kms, data.R_kpc", True, rel(0.06))
    cvr = Check("z1", "data.v_over_sigma", "Vrot / sigma per ring", "data.Vrot_kms, data.sigma_kms", True, rel(0.01, 0.002))
    cmx = Check("z1", "vrot_max_kms", "max of per-ring Vrot", "data.Vrot_kms", True, 0.006)
    cmn = Check("z1", "vrot_mean_kms", "mean of per-ring Vrot", "data.Vrot_kms", True, 0.006)
    cnr = Check("z1", "n_rings", "number of rings", "data", True, 0)
    for r in z1:
        rows = r.get("data") or []
        for p in rows:
            if p.get("Vrot_kms") and p.get("R_kpc"):
                cmd.test(f"{r['galaxy']}@{p['R_kpc']}", p.get("Mdyn_msun"), p["Vrot_kms"] ** 2 * p["R_kpc"] / G_KPC)
            if p.get("Vrot_kms") and p.get("sigma_kms"):
                cvr.test(f"{r['galaxy']}@{p['R_kpc']}", p.get("v_over_sigma"), p["Vrot_kms"] / p["sigma_kms"])
        v = [p["Vrot_kms"] for p in rows if p.get("Vrot_kms") is not None]
        if v:
            cmx.test(r["galaxy"], r.get("vrot_max_kms"), max(v))
            cmn.test(r["galaxy"], r.get("vrot_mean_kms"), statistics.fmean(v))
            cnr.test(r["galaxy"], r.get("n_rings"), len(rows))
    checks += [cmd, cvr, cmx, cmn, cnr]

    omega = {k: check_corpus(k, load(layout, k)) for k in ("z1", "intz")}
    return checks, notes, omega


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--data-dir")
    ap.add_argument("--out", default="audit_report")
    a = ap.parse_args(argv)
    checks, notes, omega = audit(resolve_data_layout(a.data_dir))
    rows = [c.row() for c in checks]
    report = {"checks": rows, "omega": omega, "notes": notes,
              "n_checks": len(rows), "n_values": sum(r["checked"] for r in rows),
              "n_failed": sum(r["failed"] for r in rows)}
    Path(a.out + ".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = ["| Corpus | Field | Definition | Values checked | Mismatches |", "|---|---|---|---|---|"]
    md += [f"| {r['corpus']} | `{r['field']}` | {r['definition']} | {r['checked']} | {r['failed']} |" for r in rows]
    md += ["", "**omega:** " + "; ".join(f"{k}: {v['verified']} of {v['available']} available values reproduce "
                                         f"from measured rings, {v['withdrawn']} withdrawn, {len(v['errors'])} errors"
                                         for k, v in omega.items())]
    md += [""] + [f"- **{n['corpus']}:** {n['note']}" for n in notes]
    for r in rows:
        if r["examples"]:
            md += ["", f"Mismatches in {r['corpus']} `{r['field']}`:"] + [f"- {e}" for e in r["examples"]]
    Path(a.out + ".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    bad = report["n_failed"] + sum(len(v["errors"]) for v in omega.values())
    print(f"\n{report['n_checks']} checks, {report['n_values']} values, {report['n_failed']} mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
