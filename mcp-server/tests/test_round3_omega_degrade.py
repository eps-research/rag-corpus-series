"""Round 3 (Reviewer 3, concern 5): a stored omega that fails the integrity
check is marked unverified for that record; the server keeps serving."""
from astro_rag_mcp.omega import RAD_GYR_PER_KMS_KPC
from astro_rag_mcp.server import build_service


def _corrupt_one_z1():
    s = build_service(None, semantic=False)
    z1 = s.corpora["z1"]
    i = next(k for k, r in enumerate(z1.records) if (r.get("omega") or {}).get("omega_available"))
    om = z1.records[i]["omega"]
    om["omega_value_rad_gyr"] = om["omega_value_rad_gyr"] + 1.0 / RAD_GYR_PER_KMS_KPC
    s._check_omega()
    return s, i, z1.records[i]


def test_clean_corpora_have_no_unverified_omega():
    s = build_service(None, semantic=False)
    assert s.omega_errors == []
    assert s.health()["status"] == "ok"
    assert s.health()["omega_check"]["z1"]["unverified"] == 0


def test_unverified_omega_degrades_one_record_not_the_server():
    s, i, rec = _corrupt_one_z1()
    name = rec.get("galaxy") or rec.get("name")
    # the server still answers, for this record and others
    r = s.call("get_object", corpus="z1", object_id=name)
    assert r["success"]
    assert any("UNVERIFIED" in w for w in r["warnings"])
    assert r["data"]["data_quality"]["status"] == "omega_unverified"
    assert s.call("list_corpora")["success"]
    # health reports it; the filter excludes it
    h = s.health()
    assert h["status"] == "degraded" and h["omega_check"]["z1"]["unverified"] == 1
    f = s.call("filter_objects", corpus="z1", field="vrot_max_kms", omega_ready_only=True, limit=100)
    assert f["data"]["n_excluded_flagged"] == 1
    assert f["data"]["n_matched"] == h["omega_check"]["z1"]["available"] - 1
    assert len(s.omega_errors) == 1


def test_verify_fails_on_unverified_omega(monkeypatch, capsys):
    from astro_rag_mcp import cli, server
    s, _, _ = _corrupt_one_z1()
    monkeypatch.setattr(server, "build_service", lambda *a, **k: s)
    assert cli.main(["verify", "--no-semantic"]) == 1
    assert "omega integrity" in capsys.readouterr().err
