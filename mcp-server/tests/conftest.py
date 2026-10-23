"""Shared fixtures.

The real embedding model (all-MiniLM-L6-v2) needs a one-time download from
huggingface.co. Tests that need it are marked ``needs_model`` and are skipped
unless ``ASTRO_RAG_TEST_REAL_MODEL=1``. All other semantic tests use an
*oracle* encoder that returns the stored FAISS vector for any stored text,
which exercises the whole search path (index, ID sidecars, ranking, envelope)
deterministically without the model.
"""

from __future__ import annotations

import hashlib
import json
import os
import socket
import sys
import threading
import time
from pathlib import Path

import numpy as np
import pytest
import uvicorn

SERVER_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_ROOT))

from astro_rag_mcp.config import CORPORA, resolve_data_layout  # noqa: E402
from astro_rag_mcp.server import build_app, build_service  # noqa: E402

REAL_MODEL = os.getenv("ASTRO_RAG_TEST_REAL_MODEL") == "1"


def pytest_configure(config):
    config.addinivalue_line("markers", "needs_model: requires the real MiniLM embedding model")


def pytest_collection_modifyitems(config, items):
    if REAL_MODEL:
        return
    skip = pytest.mark.skip(reason="set ASTRO_RAG_TEST_REAL_MODEL=1 to run real-model tests")
    for item in items:
        if "needs_model" in item.keywords:
            item.add_marker(skip)


def make_oracle_encoder(data_dir=None):
    import faiss

    layout = resolve_data_layout(data_dir)
    table: dict[str, np.ndarray] = {}
    for spec in CORPORA.values():
        stem = layout.faiss_dir() / spec.faiss_stem
        idx = faiss.read_index(str(stem) + ".faiss")
        texts = json.loads(Path(str(stem) + "_texts.json").read_text(encoding="utf-8"))
        vecs = idx.reconstruct_n(0, idx.ntotal)
        for t, v in zip(texts, vecs):
            table.setdefault(t, v)

    def encode(texts):
        out = []
        for t in texts:
            if t in table:
                out.append(table[t])
            else:  # deterministic pseudo-embedding for free text
                seed = int(hashlib.sha256(t.encode()).hexdigest()[:8], 16)
                v = np.random.default_rng(seed).standard_normal(384).astype("float32")
                out.append(v / np.linalg.norm(v))
        return np.vstack(out).astype("float32")

    return encode


@pytest.fixture(scope="session")
def oracle():
    return make_oracle_encoder()


@pytest.fixture(scope="session")
def service(oracle):
    return build_service(encoder=oracle)


@pytest.fixture(scope="session")
def client(service):
    from fastapi.testclient import TestClient

    with TestClient(build_app(service)) as c:
        yield c


def rest(client, tool, **params):
    params = {k: v for k, v in params.items() if v is not None}
    r = client.get(f"/api/{tool}", params=params)
    return r.status_code, r.json()


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def live_server(service):
    port = _free_port()
    cfg = uvicorn.Config(build_app(service, port=port), host="127.0.0.1", port=port, log_level="warning")
    srv = uvicorn.Server(cfg)
    th = threading.Thread(target=srv.run, daemon=True)
    th.start()
    for _ in range(100):
        if srv.started:
            break
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}"
    srv.should_exit = True
    th.join(timeout=5)


