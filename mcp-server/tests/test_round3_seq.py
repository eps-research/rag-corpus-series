"""Round 3 (Reviewer 3, concern 3): no index text is truncated by the encoder,
and the stored vectors are what the served model gives for the full text."""
import json
import numpy as np
import pytest
from astro_rag_mcp.config import EMBEDDING_MAX_SEQ_LENGTH
from astro_rag_mcp.server import build_service

S = build_service(None, semantic=True)
S.semantic.start_model_load(background=False)
if S.semantic.status()["state"] not in ("ready", "degraded"):
    pytest.skip("embedding model not available", allow_module_level=True)


def test_no_index_text_exceeds_the_encoder_limit():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(S.semantic.model_name)
    for key, ci in S.semantic.indexes.items():
        n = max(len(tok(t)["input_ids"]) for t in ci.texts)
        assert n <= EMBEDDING_MAX_SEQ_LENGTH, (key, n)


@pytest.mark.parametrize("key", ["v7", "dwarf", "gc", "intz", "z1"])
def test_longest_text_reembeds_to_stored_vector(key):
    ci = S.semantic.indexes[key]
    assert ci.state == "ok", ci.reason
    j = max(range(len(ci.texts)), key=lambda k: len(ci.texts[k]))
    got = S.semantic._encoder([ci.texts[j]])[0]
    got = got / np.linalg.norm(got)
    assert float(np.sum((ci.index.reconstruct(j) - got) ** 2)) < 1e-3
