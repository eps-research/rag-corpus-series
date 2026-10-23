"""Corpus integrity and the concrete numbers quoted in the manuscript."""

import pytest

from astro_rag_mcp.config import CORPORA


def test_counts(service):
    counts = {k: len(c.records) for k, c in service.corpora.items()}
    assert counts == {"v7": 438, "dwarf": 129, "gc": 174, "intz": 1292, "z1": 31}
    assert sum(counts.values()) == 2064


def test_canonical_ids_unique(service):
    for c in service.corpora.values():
        assert len(set(c.ids)) == len(c.ids)


def test_list_corpora(service):
    env = service.call("list_corpora")
    assert env["success"]
    assert env["data"]["n_total"] == 2064
    assert [c["key"] for c in env["data"]["corpora"]] == list(CORPORA)
    assert all(c["zenodo_doi"].startswith("10.5281/zenodo.") for c in env["data"]["corpora"])


def test_ngc0024_record(service):
    """Manuscript Sec. 3.2.1: vrot_mean_kms 84.659, distance_mpc 7.3."""
    env = service.call("get_object", corpus="v7", object_id="NGC0024")
    assert env["success"], env
    rec = env["data"]["record"]
    assert rec["vrot_mean_kms"] == 84.659
    assert rec["distance_mpc"] == 7.3
    assert env["data"]["object_id"] == "SPARC:NGC0024"


def test_v7_distance_filter(service):
    """Manuscript Sec. 3.2.2 quotes 119 for HI corpus v7.0. The bundled corpus is
    v7.3 (WALLABY distances re-sourced, 2026-10-15), which gives 115."""
    env = service.call("filter_objects", corpus="v7", field="distance_mpc", min_val=1, max_val=10)
    assert env["success"]
    expected = {"7.0": 119, "7.3": 115}[service.corpora["v7"].version]
    assert env["data"]["n_matched"] == expected


def test_intz_redshift_filter_nested_field(service):
    """Manuscript Sec. 3.2.2: intz z_spec in [0.5, 1.0] -> 822 of 1,292.
    z_spec is nested at redshift.z_spec; the bare name must resolve to it."""
    env = service.call("filter_objects", corpus="intz", field="z_spec", min_val=0.5, max_val=1.0)
    assert env["success"], env
    assert env["data"]["resolved_field"] == "redshift.z_spec"
    assert env["data"]["n_matched"] == 822
    dotted = service.call("filter_objects", corpus="intz", field="redshift.z_spec",
                          min_val=0.5, max_val=1.0)
    assert dotted["data"]["n_matched"] == 822


def test_vrot_max_routing_example(service):
    """Manuscript Sec. 2.4 routing example: vrot_max_kms >= 150 must be answerable."""
    env = service.call("filter_objects", corpus="v7", field="vrot_max_kms", min_val=150)
    assert env["success"] and env["data"]["n_matched"] > 0
    assert all(r["value"] >= 150 for r in env["data"]["results"])


def test_omega_ready_only(service):
    z1 = service.call("filter_objects", corpus="z1", field="redshift", omega_ready_only=True)
    assert z1["data"]["n_matched"] == 8          # eight Tier-1 ALPINE rotators
    intz = service.call("filter_objects", corpus="intz", field="z_spec", omega_ready_only=True)
    assert intz["data"]["n_matched"] == 0        # all IntZ omega withdrawn


def test_withdrawn_omega_is_flagged(service):
    env = service.call("get_object", corpus="intz", object_id="C-HiZ_z1_111")
    assert env["success"]
    assert env["data"]["record"]["omega"]["omega_available"] is False
    assert any("WITHDRAWN" in w for w in env["warnings"])
    assert "withdrawn" in env["data"]["provenance"]["correction_notice"].lower()


@pytest.mark.parametrize("key", list(CORPORA))
def test_schema_lists_fields(service, key):
    env = service.call("get_corpus_schema", corpus=key)
    assert env["success"]
    assert env["data"]["n_records"] == CORPORA[key].expected_records
    assert len(env["data"]["metadata_fields"]) > 5


def test_schema_contains_manuscript_fields(service):
    v7 = service.call("get_corpus_schema", corpus="v7")["data"]["metadata_fields"]
    intz = service.call("get_corpus_schema", corpus="intz")["data"]["metadata_fields"]
    for f in ("distance_mpc", "vrot_mean_kms", "vrot_max_kms", "inc_deg", "quality_tier"):
        assert f in v7
    assert "redshift.z_spec" in intz
