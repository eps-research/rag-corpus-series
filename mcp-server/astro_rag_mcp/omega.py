"""The omega kinematic estimator and its integrity check on served data.

Canonical estimator (Flynn & Cannaliato 2025, Eq. 6), from two independently
measured rotation-curve rings (R1, V1) inner and (R2, V2) outer::

    outer_term    = V2 / R2
    inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)
    omega_kms_kpc = outer_term - inner_term          [km/s/kpc]
    omega_rad_gyr = omega_kms_kpc * 1.0227           [1 km/s/kpc = 1.0227 rad/Gyr]

This module is the single implementation used by the server, the tests and
the audit tools. Its validation protocol (``tests/test_omega.py``) is:

1. Analytic cases. A Keplerian curve (V proportional to R^-1/2) gives exactly
   zero; a solid-body curve (V = a R) gives a (1 - (R1/R2)^1.5); a flat curve
   gives V (1/R2 - R1^0.5/R2^1.5). The superseded implementation, which
   applied the factor (R1/R2)^1.5 to the whole difference of the two terms,
   fails the Keplerian case; this is how the tests guard against its return.
4. Static check. ``check_omega_formula.py`` (repository root) rejects the
   superseded and compact forms in source files; CI runs it on every push.
2. Regression. Every omega value stored in a served corpus is recomputed from
   its stored boundary points at server start-up (``check_corpus``).
3. Provenance. Stored boundary points must be rows of the record's own
   measured rotation curve, not derived quantities (the KROSS defect, August
   2026). Withdrawn values must carry no current value.
"""

from __future__ import annotations

import math
from typing import Any

RAD_GYR_PER_KMS_KPC = 1.0227
REL_TOL = 1e-6


def omega_kms_kpc(r1: float, v1: float, r2: float, v2: float) -> float:
    """Canonical Eq. 6 in km/s/kpc. Requires 0 < r1 < r2."""
    if not (r1 > 0 and r2 > r1):
        raise ValueError(f"omega needs 0 < R1 < R2 (got R1={r1}, R2={r2})")
    outer_term = v2 / r2
    inner_term = (v1 / r1) * (r1 / r2) ** 1.5
    return outer_term - inner_term


def omega_rad_gyr(r1: float, v1: float, r2: float, v2: float) -> float:
    return RAD_GYR_PER_KMS_KPC * omega_kms_kpc(r1, v1, r2, v2)


def omega_rad_gyr_uncertainty(r1: float, v1: float, e1: float, r2: float, v2: float, e2: float) -> float:
    """1-sigma uncertainty from the two velocity errors (linear propagation;
    radii and inclination treated as exact, as in the source tables)."""
    d1 = (1 / r1) * (r1 / r2) ** 1.5
    d2 = 1 / r2
    return RAD_GYR_PER_KMS_KPC * math.hypot(d1 * e1, d2 * e2)


def check_corpus(key: str, records: list[dict]) -> dict[str, Any]:
    """Recompute every stored omega of a corpus; return a report.

    Records with ``omega.omega_available`` true must reproduce their stored
    value from their stored boundary points, and those points must be rows of
    the record's own curve. Withdrawn records must hold no current value.
    """
    report: dict[str, Any] = {"available": 0, "withdrawn": 0, "verified": 0, "errors": []}
    for r in records:
        om = r.get("omega")
        if not isinstance(om, dict):
            continue
        name = r.get("galaxy") or r.get("name") or "?"
        if om.get("omega_available") is not True:
            report["withdrawn"] += 1
            if om.get("omega_value_rad_gyr") is not None:
                report["errors"].append(f"{key}:{name}: withdrawn omega still carries a value")
            continue
        report["available"] += 1
        try:
            r1, v1, r2, v2 = (float(om[k]) for k in ("R1_kpc", "V1_kms", "R2_kpc", "V2_kms"))
        except (KeyError, TypeError, ValueError):
            report["errors"].append(f"{key}:{name}: omega has no stored boundary points")
            continue
        stored = om.get("omega_value_rad_gyr")
        recomputed = omega_rad_gyr(r1, v1, r2, v2)
        if stored is None or not math.isclose(float(stored), recomputed, rel_tol=REL_TOL, abs_tol=1e-9):
            report["errors"].append(f"{key}:{name}: stored omega {stored} != canonical {recomputed:.6f}")
            continue
        rows = {(round(float(p["R_kpc"]), 4), round(float(p["Vrot_kms"]), 3))
                for p in r.get("data") or [] if p.get("R_kpc") is not None and p.get("Vrot_kms") is not None}
        if (round(r1, 4), round(v1, 3)) not in rows or (round(r2, 4), round(v2, 3)) not in rows:
            report["errors"].append(f"{key}:{name}: boundary points are not rows of the measured curve")
            continue
        report["verified"] += 1
    return report
