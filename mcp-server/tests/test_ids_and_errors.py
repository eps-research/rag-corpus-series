"""Identifier resolution, field resolution and error envelopes."""

import pytest


@pytest.mark.parametrize("corpus,raw,expected", [
    ("v7", "NGC0024", "SPARC:NGC0024"),
    ("v7", "sparc:ngc0024", "SPARC:NGC0024"),
    ("v7", "NGC 0024", "SPARC:NGC0024"),
    ("v7", "NGC 24", "SPARC:NGC0024"),
    ("v7", "ngc24", "SPARC:NGC0024"),
    ("v7", "SPARC:NGC3198", "SPARC:NGC3198"),
    ("v7", "THINGS:NGC3198", "THINGS:NGC3198"),
    ("dwarf", "DDO 154", None),
    ("gc", "NGC 104", "NGC 104"),
    ("gc", "ngc104", "NGC 104"),
    ("intz", "C-HiZ_z1_111", "KROSS:C-HiZ_z1_111"),
    ("z1", "CG32", "ALPINE:CG32"),
])
def test_id_variants(service, corpus, raw, expected):
    env = service.call("get_object", corpus=corpus, object_id=raw)
    if expected is None:          # dwarf DDO154 may exist in more than one survey
        assert env["success"] or env["error"]["code"] == "AMBIGUOUS_OBJECT_ID"
        return
    assert env["success"], env["error"]
    assert env["data"]["object_id"] == expected


def test_ambiguous_name_is_not_silently_resolved(service):
    """NGC3198 is in both SPARC and THINGS with different rotation curves."""
    env = service.call("get_object", corpus="v7", object_id="NGC3198")
    assert not env["success"]
    assert env["error"]["code"] == "AMBIGUOUS_OBJECT_ID"
    assert set(env["error"]["candidates"]) == {"SPARC:NGC3198", "THINGS:NGC3198"}


def test_not_found_suggests(service):
    env = service.call("get_object", corpus="v7", object_id="NGC0025")
    assert env["error"]["code"] == "OBJECT_NOT_FOUND"
    assert "SPARC:NGC0024" in env["error"]["suggestions"]


def test_unknown_corpus(service):
    env = service.call("list_objects", corpus="sparc")
    assert env["error"]["code"] == "UNKNOWN_CORPUS"
    assert env["error"]["valid"] == ["v7", "dwarf", "gc", "intz", "z1"]


def test_unknown_field_is_an_error_not_zero_results(service):
    env = service.call("filter_objects", corpus="v7", field="distance_mcp", min_val=1)
    assert env["error"]["code"] == "UNKNOWN_FIELD"
    assert "distance_mpc" in env["error"]["suggestions"]


def test_ambiguous_nested_field(service):
    env = service.call("search_metadata", corpus="intz", field="survey", value="KROSS")
    assert env["error"]["code"] == "AMBIGUOUS_FIELD"
    ok = service.call("search_metadata", corpus="intz", field="identifiers.survey", value="KROSS")
    assert ok["success"] and ok["data"]["n_matched"] > 0


def test_tabular_data_is_not_a_field(service):
    env = service.call("filter_objects", corpus="v7", field="data", min_val=0)
    assert env["error"]["code"] == "INVALID_ARGUMENT"


@pytest.mark.parametrize("kw", [{"limit": 0}, {"limit": 501}, {"offset": -1}])
def test_paging_bounds(service, kw):
    env = service.call("list_objects", corpus="v7", **kw)
    assert env["error"]["code"] == "INVALID_ARGUMENT"


def test_min_greater_than_max(service):
    env = service.call("filter_objects", corpus="v7", field="distance_mpc", min_val=10, max_val=1)
    assert env["error"]["code"] == "INVALID_ARGUMENT"


def test_search_metadata_substring(service):
    env = service.call("search_metadata", corpus="v7", field="survey", value="little things")
    assert env["success"] and env["data"]["n_matched"] == 26


def test_list_objects_filters_and_paging(service):
    env = service.call("list_objects", corpus="v7", survey="sparc", limit=10, offset=5)
    d = env["data"]
    assert d["n_filtered"] == 175 and d["n_returned"] == 10
    assert all(o.startswith("SPARC:") for o in d["object_ids"])
    t1 = service.call("list_objects", corpus="v7", quality_tier=1)["data"]["n_filtered"]
    t2 = service.call("list_objects", corpus="v7", quality_tier=2)["data"]["n_filtered"]
    assert t1 + t2 == 438


def test_unknown_tool(service):
    assert service.call("drop_tables")["error"]["code"] == "UNKNOWN_TOOL"
