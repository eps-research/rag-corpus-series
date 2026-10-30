"""tools/semantic_benchmark.py: judgments are well-formed and the BM25 baseline runs.
(MiniLM numbers need the real model: ASTRO_RAG_TEST_REAL_MODEL=1.)"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import semantic_benchmark as sb  # noqa: E402


def test_every_query_has_relevant_records(service):
    assert len(sb.QUERIES) == 25
    assert len({q[0] for q in sb.QUERIES}) == 25
    assert sb.NUMERIC <= {q[0] for q in sb.QUERIES} and len(sb.NUMERIC) == 14
    for qid, corpus, _, p2, _ in sb.QUERIES:
        lc = service.corpora[corpus]
        assert any(p2(r) for r in lc.records), qid


def test_metrics_are_exact():
    grade = {"a": 2, "b": 1, "c": 0, "d": 2}
    m = sb.metrics(["a", "c", "d", "b"], grade)
    assert m["MRR"] == 1.0 and m["P@5"] == pytest.approx(2 / 5) and m["R@10"] == 1.0
    assert sb.metrics(["c"], grade)["nDCG@10"] == 0.0


def test_bm25_baseline_runs(service):
    res = sb.run(service, ["bm25"])
    assert res["mean"]["bm25"]["nDCG@10"] > res["mean"]["random"]["nDCG@10"]


@pytest.mark.needs_model
def test_minilm_benchmark_runs(service):
    service.semantic.start_model_load(background=False)
    res = sb.run(service, ["minilm", "bm25"])
    assert 0.0 <= res["mean"]["minilm"]["nDCG@10"] <= 1.0
