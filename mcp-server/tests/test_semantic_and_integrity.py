"""FAISS integrity gate and semantic search."""

import json
import shutil

import pytest

from astro_rag_mcp.config import CORPORA, resolve_data_layout
from astro_rag_mcp.corpus_service import sha256_file
from astro_rag_mcp.server import build_service


def test_all_indexes_pass_integrity(service):
    st = service.semantic.status()
    assert st["state"] == "ready"
    for key, idx in st["indexes"].items():
        assert idx["state"] == "ok", (key, idx["reason"])
        assert idx["vectors"] == CORPORA[key].expected_records
        assert idx["self_test"]["passed"]


@pytest.mark.parametrize("key", list(CORPORA))
def test_record_text_retrieves_itself(service, key):
    ci = service.semantic.indexes[key]
    for probe in (0, len(ci.ids) // 2, len(ci.ids) - 1):
        env = service.call("semantic_search", corpus=key, query=ci.texts[probe], top_k=3)
        assert env["success"], env["error"]
        top = env["data"]["results"][0]
        # identical texts (if any) tie at distance 0; the probe must be among them
        zero = [r["id"] for r in env["data"]["results"] if r["score"] < 1e-6]
        assert ci.ids[probe] in zero
        assert top["score"] < 1e-6 and top["cosine_similarity"] > 0.999999


def test_results_resolve_with_get_object(service):
    env = service.call("semantic_search", corpus="all", query="rotating disk", top_k=20)
    assert env["success"] and env["data"]["n_returned"] == 20
    scores = [r["score"] for r in env["data"]["results"]]
    assert scores == sorted(scores)
    for r in env["data"]["results"]:
        got = service.call("get_object", corpus=r["corpus"], object_id=r["id"])
        assert got["success"] and got["data"]["object_id"] == r["id"]


def test_semantic_is_deterministic(service):
    a = service.call("semantic_search", corpus="v7", query="dwarf irregular", top_k=10)
    b = service.call("semantic_search", corpus="v7", query="dwarf irregular", top_k=10)
    assert a == b


@pytest.mark.parametrize("kw,code", [
    ({"corpus": "v7", "query": "", "top_k": 5}, "INVALID_ARGUMENT"),
    ({"corpus": "v7", "query": "x", "top_k": 0}, "INVALID_ARGUMENT"),
    ({"corpus": "v7", "query": "x", "top_k": 51}, "INVALID_ARGUMENT"),
    ({"corpus": "nope", "query": "x", "top_k": 5}, "UNKNOWN_CORPUS"),
])
def test_semantic_argument_errors(service, kw, code):
    assert service.call("semantic_search", **kw)["error"]["code"] == code


def _copy_release_layout(tmp_path):
    """Copy the data into the release layout (data/corpora, data/faiss)."""
    src = resolve_data_layout()
    dst = tmp_path / "data"
    (dst / "corpora").mkdir(parents=True)
    shutil.copytree(src.faiss_dir(), dst / "faiss")
    for spec in CORPORA.values():
        shutil.copy2(src.corpus_path(spec), dst / "corpora" / spec.filename)
    return dst


def test_corrupted_id_sidecar_disables_only_that_corpus(tmp_path, oracle):
    dst = _copy_release_layout(tmp_path)
    p = dst / "faiss" / "z1_corpus_ids.json"
    ids = json.loads(p.read_text())
    ids[0] = "ALPINE:DOES_NOT_EXIST"
    p.write_text(json.dumps(ids))
    svc = build_service(str(dst), encoder=oracle)
    st = svc.semantic.status()["indexes"]
    assert st["z1"]["state"] == "failed" and "do not resolve" in st["z1"]["reason"]
    assert all(st[k]["state"] == "ok" for k in ("v7", "dwarf", "gc", "intz"))
    env = svc.call("semantic_search", corpus="z1", query="rotator", top_k=3)
    assert env["error"]["code"] == "INDEX_INTEGRITY_FAILED"
    # The other six tools still work on z1.
    assert svc.call("get_object", corpus="z1", object_id="CG32")["success"]


def test_wrong_embedding_model_is_detected(tmp_path, oracle):
    import numpy as np

    def wrong_model(texts):                       # e.g. a different MiniLM revision
        v = oracle(texts)
        v[:, :8] = -v[:, :8]
        return v / np.linalg.norm(v, axis=1, keepdims=True)

    svc = build_service(encoder=wrong_model)
    assert all(i["state"] == "failed" and "self-test" in i["reason"]
               for i in svc.semantic.status()["indexes"].values())


def test_checksum_mismatch_refuses_to_start(tmp_path, oracle):
    dst = _copy_release_layout(tmp_path)
    lines = []
    for f in sorted(p for p in dst.rglob("*") if p.is_file()):
        lines.append(f"{sha256_file(f)}  {f.relative_to(dst).as_posix()}")
    (dst / "SHA256SUMS").write_text("\n".join(lines) + "\n")
    build_service(str(dst), encoder=oracle)       # intact: loads
    with open(dst / "corpora" / CORPORA["gc"].filename, "a") as fh:
        fh.write(" ")
    with pytest.raises(ValueError, match="checksum"):
        build_service(str(dst), encoder=oracle)


def test_semantic_disabled_keeps_other_tools(tmp_path):
    svc = build_service(semantic=False)
    assert svc.call("semantic_search", corpus="v7", query="x")["error"]["code"] == "SEMANTIC_UNAVAILABLE"
    assert svc.call("filter_objects", corpus="v7", field="distance_mpc", min_val=1)["success"]


def test_missing_sentence_transformers_reports_clearly(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name.startswith("sentence_transformers"):
            raise ImportError("No module named 'sentence_transformers'")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    svc = build_service()
    svc.semantic.start_model_load(background=False)
    env = svc.call("semantic_search", corpus="v7", query="dwarf")
    assert env["error"]["code"] == "SEMANTIC_UNAVAILABLE"
    assert "requirements-semantic.txt" in env["error"]["message"]
    assert svc.call("list_corpora")["success"]


@pytest.mark.needs_model
def test_real_model_self_test_and_manuscript_z1_query():
    """Real MiniLM: the self-test must pass, and the manuscript Sec. 3.1 query
    must return the listed Z1 top five (ALPINE:J0817 first)."""
    svc = build_service()
    svc.semantic.start_model_load(background=False)
    st = svc.semantic.status()
    assert st["state"] == "ready", st
    env = svc.call("semantic_search", corpus="z1",
                   query="confirmed ALPINE rotator high redshift", top_k=5)
    ids = [r["id"] for r in env["data"]["results"]]
    assert ids == ["ALPINE:J0817", "ALPINE:VC5100822662", "ALPINE:VC5110377875",
                   "ALPINE:DC552206", "ALPINE:CG32"], env["data"]["results"]
    assert abs(env["data"]["results"][0]["score"] - 0.811) < 0.002
