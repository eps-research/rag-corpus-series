"""Validation protocol for the omega estimator (see astro_rag_mcp/omega.py).

These tests run in CI on every push. They would have failed on the
implementation that produced the withdrawn cross-epoch sign reversal.
"""

import copy
import math

import numpy as np
import pytest

from astro_rag_mcp.omega import (
    RAD_GYR_PER_KMS_KPC,
    check_corpus,
    omega_kms_kpc,
    omega_rad_gyr,
    omega_rad_gyr_uncertainty,
)


def superseded(r1, v1, r2, v2):
    """The withdrawn implementation (August 2026). Kept only as a test target."""
    return (v2 / r2 - v1 / r1) * (r1 / r2) ** 1.5


RADII = [(0.5, 2.0), (1.17, 3.5), (2.0, 10.0), (0.3, 0.9)]


@pytest.mark.parametrize("r1,r2", RADII)
def test_keplerian_curve_gives_zero(r1, r2):
    k = 200.0
    v1, v2 = k / math.sqrt(r1), k / math.sqrt(r2)
    assert omega_kms_kpc(r1, v1, r2, v2) == pytest.approx(0.0, abs=1e-12)
    # The superseded form is not zero on a Keplerian curve: the test that guards it.
    assert abs(superseded(r1, v1, r2, v2)) > 1.0


@pytest.mark.parametrize("r1,r2", RADII)
def test_solid_body_curve(r1, r2):
    a = 40.0
    assert omega_kms_kpc(r1, a * r1, r2, a * r2) == pytest.approx(a * (1 - (r1 / r2) ** 1.5))


@pytest.mark.parametrize("r1,r2", RADII)
def test_flat_curve(r1, r2):
    v = 150.0
    assert omega_kms_kpc(r1, v, r2, v) == pytest.approx(v * (1 / r2 - r1 ** 0.5 / r2 ** 1.5))
    assert omega_kms_kpc(r1, v, r2, v) > 0


def test_unit_conversion_multiplies():
    assert omega_rad_gyr(1, 100, 4, 100) == pytest.approx(RAD_GYR_PER_KMS_KPC * omega_kms_kpc(1, 100, 4, 100))
    assert RAD_GYR_PER_KMS_KPC == pytest.approx(1.0227, abs=1e-4)


def test_radii_must_be_ordered():
    with pytest.raises(ValueError):
        omega_kms_kpc(3.0, 100, 1.0, 100)


def test_uncertainty_matches_monte_carlo():
    r1, v1, e1, r2, v2, e2 = 1.17, 117.43, 20.71, 3.5, 115.04, 26.96
    rng = np.random.default_rng(0)
    s = omega_rad_gyr(r1, rng.normal(v1, e1, 200_000), r2, rng.normal(v2, e2, 200_000))
    assert omega_rad_gyr_uncertainty(r1, v1, e1, r2, v2, e2) == pytest.approx(float(np.std(s)), rel=0.01)


def test_served_omega_values_all_verified(service):
    rep = service.omega_report
    assert rep["z1"] == {"available": 8, "withdrawn": 0, "verified": 8, "errors": []}
    assert rep["intz"]["withdrawn"] == 1292 and rep["intz"]["available"] == 0
    assert service.health()["omega_check"]["z1"]["verified"] == 8


def test_z1_values_reproduce_the_correction(service):
    """All eight Tier-1 ALPINE rotators: superseded form negative, canonical positive."""
    for r in service.corpora["z1"].records:
        om = r.get("omega") or {}
        if not om.get("omega_available"):
            continue
        args = (om["R1_kpc"], om["V1_kms"], om["R2_kpc"], om["V2_kms"])
        assert superseded(*args) < 0 < omega_kms_kpc(*args)


def _z1_records(service):
    return copy.deepcopy(service.corpora["z1"].records)


def test_check_detects_a_wrong_stored_value(service):
    recs = _z1_records(service)
    om = next(r["omega"] for r in recs if r["omega"]["omega_available"])
    args = (om["R1_kpc"], om["V1_kms"], om["R2_kpc"], om["V2_kms"])
    om["omega_value_rad_gyr"] = RAD_GYR_PER_KMS_KPC * superseded(*args)
    assert any("!= canonical" in e for e in check_corpus("z1", recs)["errors"])


def test_check_detects_derived_boundary_points(service):
    """The KROSS defect: boundary points not taken from measured rings."""
    recs = _z1_records(service)
    r = next(r for r in recs if r["omega"]["omega_available"])
    om = r["omega"]
    om["V1_kms"] = round(0.6577 * om["V2_kms"], 3)
    om["omega_value_rad_gyr"] = omega_rad_gyr(om["R1_kpc"], om["V1_kms"], om["R2_kpc"], om["V2_kms"])
    assert any("not rows of the measured curve" in e for e in check_corpus("z1", recs)["errors"])


def test_check_detects_value_on_withdrawn_record(service):
    recs = copy.deepcopy(service.corpora["intz"].records[:3])
    recs[0]["omega"]["omega_value_rad_gyr"] = -5.9
    assert check_corpus("intz", recs)["errors"]


def test_corpus_audit_reports_only_known_findings(tmp_path):
    """tools/corpus_audit.py: every derived field reproduces from its inputs,
    except one known inconsistency between two transcribed catalogue values
    (Dwarf v1.0, NGC5408: mhi_mdyn_ratio vs mhi_log_msun and log_mdyn),
    reported to the corpus maintainer."""
    import json
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
    import corpus_audit

    corpus_audit.main(["--out", str(tmp_path / "a")])
    rep = json.loads((tmp_path / "a.json").read_text(encoding="utf-8"))
    failed = [(c["corpus"], c["field"], e) for c in rep["checks"] for e in c["examples"]]
    assert [(c, f) for c, f, _ in failed] == [("dwarf", "mhi_mdyn_ratio")]
    assert failed[0][2].startswith("NGC5408")
    assert rep["n_values"] > 5000
    assert all(not v["errors"] for v in rep["omega"].values())
