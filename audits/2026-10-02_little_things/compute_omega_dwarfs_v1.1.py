#!/usr/bin/env python3
"""
compute_omega_dwarfs.py  —  v1.1 (October 2026)
═══════════════════════════════════════════════════════════════════════════
Per-galaxy omega (ω) for the omega-ready galaxies of the
Dwarf/Irregular Galaxy HI Rotation Curve Corpus v1.0.

Estimator: Flynn & Cannaliato (2025), Frontiers in Astronomy and Space
Sciences 12, Eq. 1/6.  DOI: 10.3389/fspas.2025.1680387

STATUS OF OUTPUT
  Eligibility-level, per-galaxy values only. No population statistic is
  reported (see Flynn 2026, FAIR2 platform paper, Limitations 2, 3, 10).

CHANGES FROM v1.0 (May 2026)
  1. Unit conversion corrected. v1.0 divided km/s/kpc by 1.022 and labelled
     the result rad/Gyr; the correct conversion multiplies by 1.0227.
     v1.0 'omega_radGyr' values were ~4.4% low.
  2. Boundary-ring convention made explicit. The LITTLE THINGS records
     (transferred from HI Corpus v7) contain the observed curve followed
     by an appended second curve on the same radii (4-decimal, smooth,
     errV copied from the observed rows). v1.0 sorted the concatenation
     by radius, so R1/V1 came from the observed curve but R2/V2 could
     come from the appended curve. v1.1 uses the observed block only:
     the rows before the first decrease in radius in the HI v7 record
     (where the two curves are stored as consecutive blocks).
  3. Withdrawn outer-gap diagnostic removed (Vadj_R2, outer_gap_kms):
     with this estimator Vadj(R2) reduces to the Keplerian value, so the
     gap's sign is algebraically fixed.
  4. SPARC comparison columns removed (zscore_vs_sparc,
     within_1sigma_sparc): v1.0 compared against 7.06 labelled rad/Gyr,
     but 7.06 is km/s/kpc (7.22 rad/Gyr), and no population comparison
     is reported.
  5. No silent 1.0 km/s floor on missing errV; sigma is left blank and
     flagged when a boundary uncertainty is absent.

Usage:
  python3 compute_omega_dwarfs.py --corpus dwarf_irregular_corpus_v1.json \
                                  --v7 rotation_curve_corpus_v7.json \
                                  --output omega_results_dwarfs_v1.1.csv
═══════════════════════════════════════════════════════════════════════════
"""

import argparse
import csv
import json
import math

KMS_KPC_TO_RAD_GYR = 1.0227          # 1 km/s/kpc = 1.0227 rad/Gyr (multiply)
CONVENTION = "observed_block_innermost_outermost"
STATUS = "eligibility_only_not_validated"
FORMULA = "outer_term=(V2/R2); inner_term=(V1/R1)*((R1/R2)**1.5); omega=outer_term-inner_term"


def observed_block(data):
    """Rows up to (not including) the first decrease in radius."""
    for i in range(1, len(data)):
        if data[i]["Rad"] < data[i - 1]["Rad"]:
            return data[:i], len(data) - i
    return data, 0


def omega_eq6(R1, V1, R2, V2):
    """Canonical Eq. 6, named-term form. Returns km/s/kpc."""
    outer_term = (V2 / R2)
    inner_term = (V1 / R1) * ((R1 / R2) ** 1.5)
    omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]
    return omega_kms_kpc, outer_term, inner_term


def sigma_eq7(sV1, R1, sV2, R2):
    """Eq. 7 linear propagation. Returns km/s/kpc."""
    return math.sqrt((sV2 / R2) ** 2 + (sV1 / R1) ** 2 * (R1 / R2) ** 3)


def process_galaxy(g, v7_by_name):
    # The dwarf records store the observed and appended curves interleaved
    # (sorted by radius). The HI v7 record for the same galaxy keeps them as
    # two consecutive blocks, so the observed rows are taken from v7.
    # (Checked: for all 24 omega-ready galaxies the dwarf rows equal the v7
    # observed block plus the v7 appended block, row for row.)
    src = v7_by_name.get(g["galaxy"])
    if src is None:
        raise KeyError(f"{g['galaxy']}: not found in HI v7 corpus")
    vkey = "Vobs" if "Vobs" in src["data"][0] else "Vrot"
    obs, n_appended = observed_block(src["data"])
    if len(obs) < 2:
        return None
    radii = [p["Rad"] for p in obs]
    if len(set(radii)) != len(radii):
        raise ValueError(f"{g['galaxy']}: repeated radii inside observed block")

    p1, p2 = obs[0], obs[-1]
    R1, V1, R2, V2 = p1["Rad"], p1[vkey], p2["Rad"], p2[vkey]
    omega_kms_kpc, outer_term, inner_term = omega_eq6(R1, V1, R2, V2)
    omega_rad_gyr = omega_kms_kpc * KMS_KPC_TO_RAD_GYR   # 1 km/s/kpc = 1.0227 rad/Gyr

    sV1, sV2 = p1.get("errV"), p2.get("errV")
    if sV1 is not None and sV2 is not None:
        sig_kms_kpc = sigma_eq7(sV1, R1, sV2, R2)
        sig_rad_gyr = sig_kms_kpc * KMS_KPC_TO_RAD_GYR
        sig_flag = ""
    else:
        sig_kms_kpc = sig_rad_gyr = None
        sig_flag = "missing_boundary_errV"

    return {
        "galaxy": g["galaxy"],
        "survey": g["survey"],
        "n_points_observed": len(obs),
        "n_appended_rows_excluded": n_appended,
        "distance_mpc": g.get("distance_mpc"),
        "R1_kpc": R1, "V1_kms": V1, "eV1_kms": sV1,
        "R2_kpc": R2, "V2_kms": V2, "eV2_kms": sV2,
        "omega_kms_kpc": round(omega_kms_kpc, 4),
        "sigma_omega_kms_kpc": None if sig_kms_kpc is None else round(sig_kms_kpc, 4),
        "omega_rad_gyr": round(omega_rad_gyr, 4),
        "sigma_omega_rad_gyr": None if sig_rad_gyr is None else round(sig_rad_gyr, 4),
        "inner_term_fraction": round(inner_term / outer_term, 4),
        "sigma_flag": sig_flag,
        "boundary_convention": CONVENTION,
        "formula": FORMULA,
        "status": STATUS,
    }


def main():
    ap = argparse.ArgumentParser(description="Per-galaxy omega for the dwarf corpus (v1.1)")
    ap.add_argument("--corpus", default="dwarf_irregular_corpus_v1.json")
    ap.add_argument("--v7", default="rotation_curve_corpus_v7.json",
                    help="HI Corpus v7 JSON (source of the observed-block rows)")
    ap.add_argument("--output", default="omega_results_dwarfs_v1.1.csv")
    args = ap.parse_args()

    with open(args.corpus) as f:
        corpus = json.load(f)
    with open(args.v7) as f:
        v7_by_name = {g["galaxy"]: g for g in json.load(f)["galaxies"] if g.get("data")}

    rows = [r for g in corpus["galaxies"] if g.get("omega_ready")
            for r in [process_galaxy(g, v7_by_name)] if r]
    rows.sort(key=lambda r: r["galaxy"])

    with open(args.output, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"{len(rows)} galaxies written to {args.output}")
    print("Per-galaxy eligibility values only; no population statistic is reported.")


if __name__ == "__main__":
    main()
