"""Round 3 (Reviewer 3): flagged records and derived-field consistency."""
from astro_rag_mcp.server import build_service

S = build_service(None, semantic=False)


def test_omega_ready_only_excludes_model_row_curves():
    r = S.call("filter_objects", corpus="dwarf", field="vrot_max_kms", omega_ready_only=True, limit=500)
    assert r["success"]
    for m in r["data"]["results"]:
        assert m.get("data_quality") != "contains_model_rows"
    assert r["data"]["n_excluded_flagged"] > 0
    assert any("model rows" in w for w in r["warnings"])


def test_omega_ready_default_off_is_unchanged():
    r = S.call("filter_objects", corpus="dwarf", field="vrot_max_kms", limit=500)
    assert r["success"] and r["data"]["n_excluded_flagged"] == 0


def test_ngc5408_ratio_warning_and_only_ngc5408():
    r = S.call("get_object", corpus="dwarf", object_id="LVHIS:NGC5408")
    assert any("mhi_mdyn_ratio" in w for w in r["warnings"])
    assert r["data"]["data_quality"]["status"] == "derived_field_inconsistent"
    bad = [k for k, v in S.record_notes.items() if v.get("status") == "derived_field_inconsistent"]
    assert len(bad) == 1
