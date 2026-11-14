"""corpus='all' never ranks corpora against each other (Reviewer 3, third report, concern 3).

Squared-L2 distances from indexes built on different text templates are not on a
common scale. Each searchable corpus therefore returns its own top_k, ranked
within that corpus, and the groups follow the corpus order of list_corpora."""
from astro_rag_mcp.corpus_service import CORPUS_KEYS


def test_all_is_grouped_and_ranked_within_corpus(service):
    env = service.call("semantic_search", corpus="all", query="rotating disk galaxy", top_k=3)
    assert env["success"], env["error"]
    res = env["data"]["results"]
    ok_keys = [k for k in CORPUS_KEYS if service.semantic.indexes[k].state == "ok"]
    # every searchable corpus contributes exactly top_k results, in corpus order
    assert [r["corpus"] for r in res] == [k for k in ok_keys for _ in range(3)]
    for k in ok_keys:
        grp = [r for r in res if r["corpus"] == k]
        assert [r["rank"] for r in grp] == [1, 2, 3]
        assert [r["score"] for r in grp] == sorted(r["score"] for r in grp)
    assert "not on a common scale" in env["data"]["ranking"]


def test_all_groups_equal_single_corpus_results(service):
    env = service.call("semantic_search", corpus="all", query="metal-poor halo", top_k=5)
    for k in CORPUS_KEYS:
        if service.semantic.indexes[k].state != "ok":
            continue
        one = service.call("semantic_search", corpus=k, query="metal-poor halo", top_k=5)
        a = [(r["id"], r["rank"], r["score"]) for r in env["data"]["results"] if r["corpus"] == k]
        b = [(r["id"], r["rank"], r["score"]) for r in one["data"]["results"]]
        assert a == b, k
