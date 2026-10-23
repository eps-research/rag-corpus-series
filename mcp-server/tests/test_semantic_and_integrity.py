"""FAISS integrity gate, index freshness and semantic search.

These tests do not hard-code which shipped index is currently stale. They
check that the server's verdict for every index agrees with an independent
recomputation, and they exercise the stale -> rebuilt path on a synthetic
rebuild in a temporary directory.
"""

import hashlib
import json
import shutil

import numpy as np
import pytest

from astro_rag_mcp.config import CORPORA, resolve_data_layout
from astro_rag_mcp.corpus_service import sha256_file
from astro_rag_mcp.index_text import check_text, refresh_v7_text
from astro_rag_mcp.server import build_service


def _ok_keys(service):
    return [k for k, ci in service.semantic.indexes.items() if ci.state == "ok"]


def test_index_verdicts_match_independent_recheck(service):
    st = service.semantic.status()
    for key, idx in st["indexes"].items():
        lc = service.corpora[key]
        ci = service.semantic.indexes[key]
        assert idx["vectors"] == CORPORA[key].expected_records
        n_bad = sum(bool(check_text(key, lc.records[lc.by_id[i]], t)) for i, t in zip(ci.ids, ci.texts))
        assert idx["stale_records"] == n_bad
        if n_bad:
            assert idx["state"] == "stale"
        else:
            assert idx["state"] == "ok", (key, idx["reason"])
            assert idx["self_test"]["passed"]


def test_shipped_v7_index_status_is_reported(service):
    """The v7 index in the repository at fb6c592 was built from HI v7.0; the
    corpus is v7.3. Until it is rebuilt, v7 semantic search must be refused."""
    ci = service.semantic.indexes["v7"]
    if ci.state == "ok":
        pytest.skip("v7 index has been rebuilt")
    env = service.call("semantic_search", corpus="v7", query="dwarf irregular", top_k=5)
    assert env["error"]["code"] == "INDEX_STALE"
    assert "v7.3" in env["error"]["message"]
    # other tools on v7 are unaffected
    assert service.call("get_object", corpus="v7", object_id="NGC0024")["success"]


def test_all_corpora_search_warns_about_excluded(service):
    env = service.call("semantic_search", corpus="all", query="rotating disk", top_k=20)
    assert env["success"]
    excluded = set(env["data"]["excluded_corpora"])
    assert excluded == {k for k, ci in service.semantic.indexes.items() if ci.state != "ok"}
    assert {r["corpus"] for r in env["data"]["results"]}.isdisjoint(excluded)
    assert len(env["warnings"]) == len(excluded)


@pytest.mark.parametrize("key", list(CORPORA))
def test_record_text_retrieves_itself(service, key):
    ci = service.semantic.indexes[key]
    if ci.state != "ok":
        pytest.skip(f"{key} index is {ci.state}")
    for probe in (0, len(ci.ids) // 2, len(ci.ids) - 1):
        env = service.call("semantic_search", corpus=key, query=ci.texts[probe], top_k=3)
        assert env["success"], env["error"]
        top = env["data"]["results"][0]
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
    a = service.call("semantic_search", corpus="z1", query="rotator", top_k=10)
    b = service.call("semantic_search", corpus="z1", query="rotator", top_k=10)
    assert a == b


@pytest.mark.parametrize("kw,code", [
    ({"corpus": "z1", "query": "", "top_k": 5}, "INVALID_ARGUMENT"),
    ({"corpus": "z1", "query": "x", "top_k": 0}, "INVALID_ARGUMENT"),
    ({"corpus": "z1", "query": "x", "top_k": 51}, "INVALID_ARGUMENT"),
    ({"corpus": "nope", "query": "x", "top_k": 5}, "UNKNOWN_CORPUS"),
])
def test_semantic_argument_errors(service, kw, code):
    assert service.call("semantic_search", **kw)["error"]["code"] == code


# ── normalisation ─────────────────────────────────────────────────────────────

def test_query_normalisation_is_explicit(oracle):
    """An encoder that returns un-normalised vectors (a model build without a
    Normalize layer) must give identical results: the server normalises."""
    def scaled(texts):
        return oracle(texts) * 3.7

    a = build_service(encoder=oracle).call("semantic_search", corpus="z1", query="rotator", top_k=8)
    b = build_service(encoder=scaled).call("semantic_search", corpus="z1", query="rotator", top_k=8)
    assert a["data"]["results"] == b["data"]["results"]


def test_stored_vectors_are_unit_norm(service):
    for key, ci in service.semantic.indexes.items():
        v = ci.index.reconstruct_n(0, ci.index.ntotal)
        assert np.abs(np.linalg.norm(v, axis=1) - 1).max() < 1e-3, key


# ── freshness detection and the rebuild path ─────────────────────────────────

def _copy_release_layout(tmp_path):
    src = resolve_data_layout()
    dst = tmp_path / "data"
    (dst / "corpora").mkdir(parents=True)
    shutil.copytree(src.faiss_dir(), dst / "faiss")
    (dst / "faiss" / "index_manifest.json").unlink(missing_ok=True)
    for spec in CORPORA.values():
        shutil.copy2(src.corpus_path(spec), dst / "corpora" / spec.filename)
    return dst


def _pseudo(texts):
    out = []
    for t in texts:
        seed = int(hashlib.sha256(t.encode()).hexdigest()[:8], 16)
        v = np.random.default_rng(seed).standard_normal(384).astype("float32")
        out.append(v / np.linalg.norm(v))
    return np.vstack(out).astype("float32")


def _synthetic_rebuild(dst, key, texts, ids):
    """What build_faiss_indexes.py --install does, with a stand-in encoder."""
    import faiss

    stem = CORPORA[key].faiss_stem
    idx = faiss.IndexFlatL2(384)
    idx.add(_pseudo(texts))
    fdir = dst / "faiss"
    faiss.write_index(idx, str(fdir / f"{stem}.faiss"))
    (fdir / f"{stem}_texts.json").write_text(json.dumps(texts))
    (fdir / f"{stem}_ids.json").write_text(json.dumps(ids))
    src = dst / "corpora" / CORPORA[key].filename
    manifest = {"schema": 1, "corpora": {key: {
        "source_sha256": sha256_file(src), "embedding_revision": "0" * 40,
        "artifact_sha256": {f"{stem}{s}": sha256_file(fdir / f"{stem}{s}")
                            for s in (".faiss", "_ids.json", "_texts.json")}}}}
    (fdir / "index_manifest.json").write_text(json.dumps(manifest))


def test_v7_refresh_then_rebuild_clears_staleness(tmp_path):
    dst = _copy_release_layout(tmp_path)
    svc = build_service(str(dst), semantic=False)
    lc = svc.corpora["v7"]
    fdir = dst / "faiss"
    ids = json.loads((fdir / "v7_sparc_ids.json").read_text())
    old = json.loads((fdir / "v7_sparc_texts.json").read_text())
    new = [refresh_v7_text(t, lc.records[lc.by_id[i]]) for i, t in zip(ids, old)]
    assert all(not check_text("v7", lc.records[lc.by_id[i]], t) for i, t in zip(ids, new))
    # Before 'known issues', only value groups change and the untraceable
    # 'omega ready' clause is removed; the rest of the legacy grammar is kept.
    import re
    head = lambda s: s.split(". known issues ", 1)[0]  # noqa: E731
    strip = lambda s: re.sub(r"-?\d+(?:\.\d+)?|None", "#", s)  # noqa: E731
    for a, b in zip(old, new):
        a_head = re.sub(r"\. omega ready (?:True|False|None)", "", head(a))
        assert strip(a_head) == strip(head(b)), (a, b)
    assert all("omega ready" not in t for t in new)

    _synthetic_rebuild(dst, "v7", new, ids)
    rebuilt = build_service(str(dst), encoder=_pseudo)
    v7 = rebuilt.semantic.indexes["v7"]
    assert v7.state == "ok", v7.reason
    assert v7.self_test["passed"]
    assert rebuilt.semantic.pinned_revision() == "0" * 40
    env = rebuilt.call("semantic_search", corpus="v7", query=new[5], top_k=1)
    assert env["data"]["results"][0]["id"] == ids[5]

    # a later corpus correction makes the rebuilt index stale again (manifest check)
    corpus = dst / "corpora" / CORPORA["v7"].filename
    corpus.write_text(corpus.read_text() + " ")
    again = build_service(str(dst), encoder=_pseudo)
    assert again.semantic.indexes["v7"].state == "stale"
    assert "different corpus file" in again.semantic.indexes["v7"].reason


def test_edited_index_text_is_detected(tmp_path, oracle):
    dst = _copy_release_layout(tmp_path)
    p = dst / "faiss" / "z1_corpus_texts.json"
    texts = json.loads(p.read_text())
    texts[3] = texts[3].replace("redshift z=", "redshift z=9", 1)
    p.write_text(json.dumps(texts))
    svc = build_service(str(dst), encoder=oracle)
    ci = svc.semantic.indexes["z1"]
    assert ci.state == "stale" and ci.stale_records == 1 and ci.stale_fields == {"redshift": 1}


def test_corrupted_id_sidecar_disables_only_that_corpus(tmp_path, oracle):
    dst = _copy_release_layout(tmp_path)
    p = dst / "faiss" / "z1_corpus_ids.json"
    ids = json.loads(p.read_text())
    ids[0] = "ALPINE:DOES_NOT_EXIST"
    p.write_text(json.dumps(ids))
    svc = build_service(str(dst), encoder=oracle)
    st = svc.semantic.status()["indexes"]
    assert st["z1"]["state"] == "failed" and "do not resolve" in st["z1"]["reason"]
    assert all(st[k]["state"] in ("ok", "stale") for k in ("v7", "dwarf", "gc", "intz"))
    env = svc.call("semantic_search", corpus="z1", query="rotator", top_k=3)
    assert env["error"]["code"] == "INDEX_INTEGRITY_FAILED"
    assert svc.call("get_object", corpus="z1", object_id="CG32")["success"]


def test_wrong_embedding_model_is_detected(oracle):
    def wrong_model(texts):                       # e.g. a different MiniLM revision
        v = oracle(texts)
        v[:, :8] = -v[:, :8]
        return v

    svc = build_service(encoder=wrong_model)
    probed = [i for i in svc.semantic.status()["indexes"].values() if i["self_test"] is not None]
    assert probed
    assert all(i["state"] == "failed" and "self-test" in i["reason"] for i in probed)


def test_checksum_mismatch_refuses_to_start(tmp_path, oracle):
    dst = _copy_release_layout(tmp_path)
    lines = []
    for f in sorted(p for p in dst.rglob("*") if p.is_file()):
        lines.append(f"{sha256_file(f)}  {f.relative_to(dst).as_posix()}")
    (dst / "SHA256SUMS").write_text("\n".join(lines) + "\n")
    build_service(str(dst), encoder=oracle)
    with open(dst / "corpora" / CORPORA["gc"].filename, "a") as fh:
        fh.write(" ")
    with pytest.raises(ValueError, match="checksum"):
        build_service(str(dst), encoder=oracle)


def test_semantic_disabled_keeps_other_tools():
    svc = build_service(semantic=False)
    assert svc.call("semantic_search", corpus="z1", query="x")["error"]["code"] == "SEMANTIC_UNAVAILABLE"
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
    env = svc.call("semantic_search", corpus="z1", query="dwarf")
    assert env["error"]["code"] == "SEMANTIC_UNAVAILABLE"
    assert "requirements-semantic.txt" in env["error"]["message"]
    assert svc.call("list_corpora")["success"]


@pytest.mark.needs_model
def test_real_model_self_test_and_manuscript_z1_query():
    """Real MiniLM: self-test must pass on every fresh index, and the
    manuscript Sec. 3.1 query must return the listed Z1 top five."""
    svc = build_service()
    svc.semantic.start_model_load(background=False)
    st = svc.semantic.status()
    for key, idx in st["indexes"].items():
        if idx["state"] != "stale":
            assert idx["state"] == "ok" and idx["self_test"]["passed"], (key, idx)
    env = svc.call("semantic_search", corpus="z1",
                   query="confirmed ALPINE rotator high redshift", top_k=5)
    ids = [r["id"] for r in env["data"]["results"]]
    assert ids == ["ALPINE:J0817", "ALPINE:VC5100822662", "ALPINE:VC5110377875",
                   "ALPINE:DC552206", "ALPINE:CG32"], env["data"]["results"]
    assert abs(env["data"]["results"][0]["score"] - 0.811) < 0.002


@pytest.mark.needs_model
def test_real_model_is_normalised_natively():
    """Documents the answer to the normalisation question with the real model:
    MiniLM output with normalize_embeddings=False already has unit norm."""
    from sentence_transformers import SentenceTransformer

    m = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
    v = m.encode(["Galaxy NGC0024. survey SPARC."], normalize_embeddings=False)
    assert abs(float(np.linalg.norm(v[0])) - 1.0) < 1e-4
