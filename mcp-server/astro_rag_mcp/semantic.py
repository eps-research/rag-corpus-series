"""FAISS semantic search with integrity checks.

Startup checks, per corpus (all must pass before that corpus is searchable):

* the three artifacts exist: ``<stem>.faiss``, ``<stem>_ids.json``, ``<stem>_texts.json``;
* the index is ``IndexFlatL2`` of dimension 384;
* vector count == ID count == text count == corpus record count;
* the ID sidecar is exactly the set of canonical corpus IDs (every ID resolves);
* all stored vectors are finite and unit-normalised;
* the index text agrees with the loaded records (``index_text.check_text``):
  an index built before a corpus correction is marked ``stale`` and semantic
  search on that corpus is refused until the index is rebuilt;
* if ``faiss/index_manifest.json`` lists the corpus, the SHA-256 of the
  corpus file the index was built from equals the loaded file's.

Query embeddings are L2-normalised explicitly, so scores do not depend on
whether a given model build ends in a Normalize layer.

When the embedding model has loaded, a reproducibility self-test re-embeds the
stored text of one record per corpus and requires it to land on its stored
vector (squared L2 < 1e-3). This detects a different or drifted model before it
can silently produce wrong rankings.

The embedding model (``sentence-transformers``) is optional. Without it the
other six tools work and ``semantic_search`` returns ``SEMANTIC_UNAVAILABLE``.
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np

from .config import EMBEDDING_DIM, EMBEDDING_MODEL, EMBEDDING_REVISION, DataLayout
from .corpus_service import LoadedCorpus, ServiceError, sha256_file
from .index_text import check_text

logger = logging.getLogger("astro_rag_mcp")

SELF_TEST_TOLERANCE = 1e-3
MANIFEST_NAME = "index_manifest.json"


def l2_normalize(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype="float32")
    n = np.linalg.norm(v, axis=1, keepdims=True)
    if not np.all(n > 0):
        raise ValueError("zero-norm embedding")
    return (v / n).astype("float32")
Encoder = Callable[[list[str]], np.ndarray]


class _CorpusIndex:
    def __init__(self, key: str):
        self.key = key
        self.index: Any = None
        self.ids: list[str] = []
        self.texts: list[str] = []
        self.sha256: dict[str, str] = {}
        self.state = "pending"        # ok | stale | failed
        self.reason: Optional[str] = None
        self.self_test: Optional[dict] = None
        self.stale_records: int = 0
        self.stale_fields: dict[str, int] = {}
        self.manifest: Optional[dict] = None


class SemanticIndex:
    def __init__(self, layout: DataLayout, corpora: dict[str, LoadedCorpus],
                 model_name: str = EMBEDDING_MODEL, encoder: Optional[Encoder] = None):
        self.layout = layout
        self.model_name = model_name
        self.indexes: dict[str, _CorpusIndex] = {}
        self._encoder: Optional[Encoder] = encoder
        self._model_state = "ready" if encoder else "not_loaded"
        self._model_error: Optional[str] = None
        self.model_revision: Optional[str] = None
        self.manifest: dict = self._read_manifest()
        self._ready = threading.Event()
        if encoder:
            self._ready.set()
        self._load_indexes(corpora)
        if encoder:
            self._self_test()

    def _read_manifest(self) -> dict:
        p = self.layout.faiss_dir() / MANIFEST_NAME
        if not p.is_file():
            return {}
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error("unreadable %s: %s", p, e)
            return {}

    def pinned_revision(self) -> Optional[str]:
        """Model revision recorded by the index builder, unless overridden."""
        if EMBEDDING_REVISION:
            return EMBEDDING_REVISION
        revs = {c.get("embedding_revision") for c in self.manifest.get("corpora", {}).values()}
        revs.discard(None)
        return revs.pop() if len(revs) == 1 else None

    # ── artifact loading and structural integrity ──
    def _load_indexes(self, corpora: dict[str, LoadedCorpus]) -> None:
        try:
            import faiss  # noqa: F401
        except ImportError as e:
            for key in corpora:
                ci = _CorpusIndex(key)
                ci.state, ci.reason = "failed", f"faiss is not installed ({e}); pip install faiss-cpu"
                self.indexes[key] = ci
            return
        import faiss

        fdir = self.layout.faiss_dir()
        for key, lc in corpora.items():
            ci = _CorpusIndex(key)
            self.indexes[key] = ci
            stem = lc.spec.faiss_stem
            paths = {
                "index": fdir / f"{stem}.faiss",
                "ids": fdir / f"{stem}_ids.json",
                "texts": fdir / f"{stem}_texts.json",
            }
            try:
                for name, p in paths.items():
                    if not p.is_file():
                        raise ValueError(f"missing FAISS artifact {p.name}")
                    ci.sha256[p.name] = sha256_file(p)
                index = faiss.read_index(str(paths["index"]))
                ids = json.loads(paths["ids"].read_text(encoding="utf-8"))
                texts = json.loads(paths["texts"].read_text(encoding="utf-8"))
                if type(index).__name__ != "IndexFlatL2":
                    raise ValueError(f"expected IndexFlatL2, found {type(index).__name__}")
                if index.d != EMBEDDING_DIM:
                    raise ValueError(f"index dimension {index.d}, expected {EMBEDDING_DIM}")
                n = len(lc.records)
                if not (index.ntotal == len(ids) == len(texts) == n):
                    raise ValueError(
                        f"count mismatch: vectors={index.ntotal} ids={len(ids)} "
                        f"texts={len(texts)} corpus records={n}"
                    )
                if len(set(ids)) != len(ids):
                    raise ValueError("duplicate IDs in ID sidecar")
                unresolved = sorted(set(ids) - set(lc.by_id))
                if unresolved:
                    raise ValueError(f"{len(unresolved)} index IDs do not resolve to corpus records, e.g. {unresolved[:3]}")
                vec = index.reconstruct_n(0, index.ntotal)
                if not np.isfinite(vec).all():
                    raise ValueError("non-finite stored vectors")
                norms = np.linalg.norm(vec, axis=1)
                if np.abs(norms - 1.0).max() > 1e-3:
                    raise ValueError(f"stored vectors not unit-normalised (max |norm-1| = {np.abs(norms-1).max():.2e})")
                ci.index, ci.ids, ci.texts = index, ids, texts
                ci.state = "ok"
                self._check_freshness(key, lc, ci, paths)
                if ci.state == "ok":
                    logger.info("faiss %-5s: %d vectors, d=%d, IDs and text verified",
                                key, index.ntotal, index.d)
            except Exception as e:  # recorded, reported by /health and list_corpora
                ci.state, ci.reason = "failed", str(e)
                logger.error("faiss %s: integrity check FAILED: %s", key, e)

    def _check_freshness(self, key: str, lc: LoadedCorpus, ci: _CorpusIndex, paths: dict) -> None:
        """Mark the index stale if it describes superseded record values."""
        entry = self.manifest.get("corpora", {}).get(key)
        if entry:
            ci.manifest = entry
            if entry.get("source_sha256") and entry["source_sha256"] != lc.sha256:
                ci.state = "stale"
                ci.reason = (f"index was built from a different corpus file "
                             f"(sha256 {entry['source_sha256'][:12]}..., loaded {lc.sha256[:12]}...)")
            for name, want in (entry.get("artifact_sha256") or {}).items():
                if ci.sha256.get(name) not in (None, want):
                    ci.state, ci.reason = "failed", f"{name} differs from index_manifest.json"
        fields: dict[str, int] = {}
        n = 0
        for oid, text in zip(ci.ids, ci.texts):
            bad = check_text(key, lc.records[lc.by_id[oid]], text)
            if bad:
                n += 1
                for f in bad:
                    fields[f] = fields.get(f, 0) + 1
        ci.stale_records, ci.stale_fields = n, fields
        if n and ci.state == "ok":
            ci.state = "stale"
            ci.reason = (f"index text disagrees with {lc.spec.name} v{lc.version} for {n} of "
                         f"{len(ci.ids)} records (fields: {fields}); the index predates a corpus "
                         "correction and must be rebuilt (build_scripts/build_faiss_indexes.py)")
        if ci.state == "stale":
            logger.error("faiss %s: STALE: %s", key, ci.reason)

    # ── embedding model ──
    def start_model_load(self, background: bool = True) -> None:
        if self._model_state in ("loading", "ready"):
            return
        self._model_state = "loading"
        if background:
            threading.Thread(target=self._load_model, name="embedding-model", daemon=True).start()
        else:
            self._load_model()

    def _load_model(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            self._model_state = "unavailable"
            self._model_error = (
                "sentence-transformers is not installed. Install it with "
                "'pip install -r requirements-semantic.txt' (or run launch.py without --no-semantic)."
            )
            logger.warning(self._model_error)
            self._ready.set()
            return
        try:
            kwargs = {"device": "cpu"}
            rev = self.pinned_revision()
            if rev:
                kwargs["revision"] = rev
            model = SentenceTransformer(self.model_name, **kwargs)
            self.model_revision = rev or _resolved_revision(model) or hf_cache_revision(self.model_name)

            def encode(texts: list[str]) -> np.ndarray:
                return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True,
                                    show_progress_bar=False).astype("float32", copy=False)

            self._encoder = encode
            self._model_state = "ready"
            logger.info("embedding model loaded: %s (revision %s)", self.model_name, self.model_revision)
            self._self_test()
        except Exception as e:
            self._model_state = "unavailable"
            self._model_error = (
                f"Could not load embedding model {self.model_name}: {type(e).__name__}: {e}. "
                "The first run downloads ~90 MB from huggingface.co; check network access "
                "or pre-download the model (see INSTALL.md)."
            )
            logger.error(self._model_error)
        finally:
            self._ready.set()

    def _self_test(self) -> None:
        for key, ci in self.indexes.items():
            if ci.state != "ok":
                continue   # a stale index's vectors describe other text; no meaningful probe
            stored = ci.index.reconstruct(0)
            got = l2_normalize(self._encoder([ci.texts[0]]))[0]
            d2 = float(np.sum((stored - got) ** 2))
            ci.self_test = {"probe_id": ci.ids[0], "squared_l2": d2, "passed": d2 < SELF_TEST_TOLERANCE}
            if d2 >= SELF_TEST_TOLERANCE:
                ci.state = "failed"
                ci.reason = (
                    f"embedding self-test failed: re-embedding '{ci.ids[0]}' differs from its "
                    f"stored vector (squared L2 {d2:.3g}). The local embedding model does not "
                    "match the one used to build the index."
                )
                logger.error("faiss %s: %s", key, ci.reason)

    # ── status ──
    def status_for(self, key: str) -> str:
        ci = self.indexes.get(key)
        if ci is None or ci.state in ("failed", "stale"):
            return "failed" if ci is None else ci.state
        return {"ready": "ready", "loading": "model_loading"}.get(self._model_state, "model_unavailable")

    def status(self) -> dict:
        state = self._model_state
        if any(ci.state in ("failed", "stale") for ci in self.indexes.values()):
            state = "degraded" if state == "ready" else state
        return {
            "state": state,
            "embedding_model": self.model_name,
            "embedding_revision": self.model_revision,
            "pinned_revision": self.pinned_revision(),
            "model_error": self._model_error,
            "indexes": {
                k: {"state": ci.state, "reason": ci.reason,
                    "vectors": None if ci.index is None else int(ci.index.ntotal),
                    "stale_records": ci.stale_records, "stale_fields": ci.stale_fields,
                    "built_from": ci.manifest,
                    "self_test": ci.self_test, "sha256": ci.sha256}
                for k, ci in self.indexes.items()
            },
        }

    def index_sha256(self, key: str) -> Optional[str]:
        ci = self.indexes.get(key)
        if not ci:
            return None
        return next((v for n, v in ci.sha256.items() if n.endswith(".faiss")), None)

    # ── search ──
    def search(self, keys: list[str], query: str, top_k: int,
               wait_s: float = 120.0) -> tuple[list[dict], dict[str, str]]:
        """Return (hits, excluded) where excluded maps corpus -> reason."""
        if self._model_state == "not_loaded":
            self.start_model_load(background=True)
        if not self._ready.wait(timeout=wait_s):
            raise ServiceError("SEMANTIC_LOADING",
                               "The embedding model is still loading; retry in a minute.")
        if self._model_state != "ready" or self._encoder is None:
            raise ServiceError("SEMANTIC_UNAVAILABLE", self._model_error or "embedding model unavailable")
        excluded = {k: f"{self.indexes[k].state}: {self.indexes[k].reason}"
                    for k in keys if self.indexes[k].state != "ok"}
        if excluded and len(excluded) == len(keys):
            stale = all(self.indexes[k].state == "stale" for k in keys)
            raise ServiceError("INDEX_STALE" if stale else "INDEX_INTEGRITY_FAILED",
                               f"Semantic index unavailable: {excluded}", indexes=excluded)
        q = l2_normalize(self._encoder([query]).reshape(1, -1))
        hits = []
        for k in keys:
            ci = self.indexes[k]
            if ci.state != "ok":
                continue
            dist, idx = ci.index.search(q, min(top_k, ci.index.ntotal))
            for d, i in zip(dist[0], idx[0]):
                if i < 0:
                    continue
                d = float(d)
                hits.append({"corpus": k, "id": ci.ids[i], "score": round(d, 6),
                             "cosine_similarity": round(1.0 - d / 2.0, 6), "text": ci.texts[i]})
        # Deterministic order: distance, then corpus order, then ID.
        order = {k: n for n, k in enumerate(keys)}
        hits.sort(key=lambda h: (h["score"], order[h["corpus"]], h["id"]))
        return hits[:top_k], excluded


def hf_cache_revision(model_name: str, cache_dir: Optional[str] = None) -> Optional[str]:
    """Commit hash of the locally cached Hugging Face snapshot of ``model_name``.

    Reads the cache layout directly (``models--org--name/refs/main`` and
    ``snapshots/<hash>/``), so it works across sentence-transformers and
    huggingface_hub versions. Returns None if the model is not cached.
    """
    import os
    from pathlib import Path

    if cache_dir is None:
        try:
            from huggingface_hub import constants
            cache_dir = constants.HF_HUB_CACHE
        except Exception:
            home = os.environ.get("HF_HOME") or os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
            cache_dir = os.path.join(home, "hub")
    repo = Path(cache_dir) / ("models--" + model_name.replace("/", "--"))
    ref = repo / "refs" / "main"
    if ref.is_file():
        h = ref.read_text(encoding="utf-8").strip()
        if len(h) == 40 and (repo / "snapshots" / h).is_dir():
            return h
    snaps = sorted((repo / "snapshots").glob("*")) if (repo / "snapshots").is_dir() else []
    if len(snaps) == 1 and len(snaps[0].name) == 40:
        return snaps[0].name
    return None


def _resolved_revision(model: Any) -> Optional[str]:
    """Best-effort: the Hugging Face snapshot hash the model was loaded from."""
    try:
        import re as _re
        for mod in model.modules():
            path = getattr(getattr(mod, "auto_model", None), "name_or_path", None)
            if path:
                m = _re.search(r"snapshots[/\\]([0-9a-f]{40})", str(path))
                if m:
                    return m.group(1)
    except Exception:
        pass
    return None
