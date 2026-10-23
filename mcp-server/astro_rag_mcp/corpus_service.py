"""Shared corpus service: loading, integrity checks and the seven operations.

Every interface (MCP tools, REST endpoints, browser UI) calls the functions in
this module, so the result for a given request is identical whichever
interface is used.

Every operation returns an *envelope*::

    {"success": bool, "tool": str, "data": dict | None,
     "human_text": str | None, "warnings": [str],
     "error": {"code": str, "message": str, ...} | None}

``data`` carries the machine-readable result; ``human_text`` is a short
plain-language summary intended for direct LLM consumption.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from difflib import get_close_matches
from pathlib import Path
from typing import Any, Optional

from . import __version__
from .config import (
    CORPORA,
    CORPUS_KEYS,
    CORRECTION_NOTICES,
    EXPECTED_TOTAL,
    CorpusSpec,
    DataLayout,
)

logger = logging.getLogger("astro_rag_mcp")

MAX_LIMIT = 500
# Sub-structures that are tabular data or column documentation, not metadata.
NON_METADATA_KEYS = {"data", "columns", "model_iso_oh2015"}


# ── Envelope helpers ──────────────────────────────────────────────────────────

class ServiceError(Exception):
    """A request-level error with a stable machine-readable code."""

    def __init__(self, code: str, message: str, **details: Any):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


def ok(tool: str, data: dict, human_text: str, warnings: Optional[list[str]] = None) -> dict:
    return {
        "success": True,
        "tool": tool,
        "data": data,
        "human_text": human_text,
        "warnings": warnings or [],
        "error": None,
    }


def fail(tool: str, err: ServiceError) -> dict:
    return {
        "success": False,
        "tool": tool,
        "data": None,
        "human_text": f"Error ({err.code}): {err.message}",
        "warnings": [],
        "error": {"code": err.code, "message": err.message, **err.details},
    }


# ── Normalisation helpers ─────────────────────────────────────────────────────

def normalize(s: str) -> str:
    """Collapse spaces, underscores, hyphens and case: 'DDO 133' == 'ddo_133'."""
    return re.sub(r"[\s_\-]+", "", str(s)).lower()


def normalize_loose(s: str) -> str:
    """normalize() plus leading zeros dropped from catalogue numbers: NGC0024 == NGC 24."""
    return re.sub(r"(?<![0-9])0+(?=[0-9])", "", normalize(s))


def canonical_object_id(key: str, r: dict) -> str:
    """Stable, unique identifier for a record (identical to the FAISS ID sidecars)."""
    if key == "gc":
        return str(r["cluster_id"])
    if key == "intz":
        ids = r["identifiers"]
        return f'{ids["survey"]}:{ids.get("name") or ids.get("id")}'
    return f'{r["survey"]}:{r["galaxy"]}'


def display_name(key: str, r: dict) -> str:
    if key == "gc":
        return str(r["cluster_id"])
    if key == "intz":
        ids = r["identifiers"]
        return str(ids.get("name") or ids.get("id"))
    return str(r["galaxy"])


def record_survey(r: dict) -> Optional[str]:
    if r.get("survey") is not None:
        return str(r["survey"])
    ids = r.get("identifiers")
    if isinstance(ids, dict) and ids.get("survey") is not None:
        return str(ids["survey"])
    return None


def record_quality_tier(r: dict) -> Optional[Any]:
    if "quality_tier" in r:
        return r["quality_tier"]
    meta = r.get("metadata")
    if isinstance(meta, dict):
        return meta.get("quality_tier")
    return None


def omega_ready(r: dict) -> bool:
    """True if the record carries a currently valid omega determination."""
    if r.get("omega_ready") is True:
        return True
    om = r.get("omega")
    return isinstance(om, dict) and om.get("omega_available") is True


def _iter_leaf_paths(d: dict, prefix: tuple = ()):
    for k, v in d.items():
        if not prefix and k in NON_METADATA_KEYS:
            continue
        if isinstance(v, dict):
            yield from _iter_leaf_paths(v, prefix + (k,))
        else:
            yield prefix + (k,)


def get_path(r: dict, path: tuple) -> Any:
    cur: Any = r
    for part in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ── Loaded corpus ─────────────────────────────────────────────────────────────

@dataclass
class LoadedCorpus:
    spec: CorpusSpec
    path: Path
    sha256: str
    version: str
    records: list[dict]
    ids: list[str]                                   # canonical IDs, record order
    by_id: dict[str, int] = field(default_factory=dict)          # canonical -> row
    by_norm: dict[str, list[int]] = field(default_factory=dict)  # normalized alias -> rows
    by_loose: dict[str, list[int]] = field(default_factory=dict) # zero-insensitive alias -> rows
    leaf_paths: dict[str, set] = field(default_factory=dict)     # leaf name -> {paths}
    all_paths: set = field(default_factory=set)

    def build_indexes(self) -> None:
        for i, cid in enumerate(self.ids):
            if cid in self.by_id:
                raise ValueError(f"{self.spec.key}: duplicate canonical id {cid!r}")
            self.by_id[cid] = i
            aliases = {cid, display_name(self.spec.key, self.records[i])}
            ids = self.records[i].get("identifiers")
            if isinstance(ids, dict):
                for k in ("name", "id"):
                    if ids.get(k):
                        aliases.add(str(ids[k]))
            alt = self.records[i].get("alt_name")
            if alt:
                aliases.add(str(alt))
            for a in aliases:
                for table, key in ((self.by_norm, normalize(a)), (self.by_loose, normalize_loose(a))):
                    rows = table.setdefault(key, [])
                    if i not in rows:
                        rows.append(i)
        for r in self.records:
            for p in _iter_leaf_paths(r):
                self.all_paths.add(p)
        for p in self.all_paths:
            self.leaf_paths.setdefault(p[-1], set()).add(p)


def _version_from_file(spec: CorpusSpec, doc: dict) -> str:
    for meta_key in ("metadata", "corpus_metadata"):
        meta = doc.get(meta_key)
        if isinstance(meta, dict):
            v = meta.get("version")
            if v and str(v) not in ("Z1",):
                return str(v)
    return spec.release_label


def load_corpus(spec: CorpusSpec, layout: DataLayout) -> LoadedCorpus:
    path = layout.corpus_path(spec)
    if not path.is_file():
        raise FileNotFoundError(f"Corpus file for '{spec.key}' not found: {path}")
    doc = json.loads(path.read_text(encoding="utf-8"))
    records = doc.get(spec.container)
    if not isinstance(records, list):
        raise ValueError(f"{path}: expected a top-level '{spec.container}' list")
    if len(records) != spec.expected_records:
        raise ValueError(
            f"{spec.key}: expected {spec.expected_records} records, found {len(records)} in {path}"
        )
    ids = [canonical_object_id(spec.key, r) for r in records]
    lc = LoadedCorpus(
        spec=spec,
        path=path,
        sha256=sha256_file(path),
        version=_version_from_file(spec, doc),
        records=records,
        ids=ids,
    )
    lc.build_indexes()
    return lc


def read_checksum_file(path: Path) -> dict[str, str]:
    """Parse a ``sha256sum``-style file: '<hex>  <relative path>' per line."""
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, rel = line.split(None, 1)
        out[rel.strip().lstrip("*")] = digest.lower()
    return out


# ── The service ───────────────────────────────────────────────────────────────

class CorpusService:
    """Holds the loaded corpora and implements the seven operations."""

    def __init__(self, layout: DataLayout, semantic: Any = None):
        self.layout = layout
        self.corpora: dict[str, LoadedCorpus] = {}
        self.semantic = semantic          # astro_rag_mcp.semantic.SemanticIndex or None
        self.checksum_report: dict[str, Any] = {"checked": False}

    # ── loading ──
    def load(self, verify_checksums: bool = True) -> None:
        for key, spec in CORPORA.items():
            self.corpora[key] = load_corpus(spec, self.layout)
            logger.info(
                "corpus %-5s v%s: %d records (%s)",
                key, self.corpora[key].version, len(self.corpora[key].records),
                self.corpora[key].path.name,
            )
        total = sum(len(c.records) for c in self.corpora.values())
        if total != EXPECTED_TOTAL:
            raise ValueError(f"expected {EXPECTED_TOTAL} records in total, found {total}")
        if verify_checksums:
            self.verify_checksums()

    def verify_checksums(self) -> dict:
        """Compare data files with data/SHA256SUMS when the file is present.

        A release ZIP and the Docker image ship SHA256SUMS; a mismatch there
        means the data were modified after release and is a hard error.
        """
        f = self.layout.checksum_file()
        if not f.is_file():
            self.checksum_report = {
                "checked": False,
                "reason": f"no {f.name} in {self.layout.kind} data layout",
            }
            return self.checksum_report
        expected = read_checksum_file(f)
        mismatches, missing = [], []
        for rel, digest in expected.items():
            p = self.layout.root / rel
            if not p.is_file():
                missing.append(rel)
            elif sha256_file(p) != digest:
                mismatches.append(rel)
        self.checksum_report = {
            "checked": True,
            "files": len(expected),
            "mismatches": mismatches,
            "missing": missing,
        }
        if mismatches or missing:
            raise ValueError(
                f"Data checksum verification failed: mismatched={mismatches} missing={missing}. "
                "Re-download the release; do not edit files in data/."
            )
        return self.checksum_report

    # ── helpers ──
    def _corpus(self, corpus: str) -> LoadedCorpus:
        if corpus not in self.corpora:
            raise ServiceError(
                "UNKNOWN_CORPUS",
                f"Unknown corpus '{corpus}'. Valid keys: {', '.join(CORPUS_KEYS)}.",
                valid=CORPUS_KEYS,
            )
        return self.corpora[corpus]

    @staticmethod
    def _check_page(limit: int, offset: int) -> None:
        if not 1 <= int(limit) <= MAX_LIMIT:
            raise ServiceError("INVALID_ARGUMENT", f"limit must be between 1 and {MAX_LIMIT}")
        if int(offset) < 0:
            raise ServiceError("INVALID_ARGUMENT", "offset must be >= 0")

    def provenance(self, lc: LoadedCorpus) -> dict:
        p = {
            "corpus": lc.spec.key,
            "corpus_name": lc.spec.name,
            "corpus_version": lc.version,
            "zenodo_doi": lc.spec.zenodo_doi,
            "source_file": lc.path.name,
            "source_sha256": lc.sha256,
            "server_version": __version__,
        }
        if lc.spec.key in CORRECTION_NOTICES:
            p["correction_notice"] = CORRECTION_NOTICES[lc.spec.key]
        return p

    def resolve_field(self, lc: LoadedCorpus, name: str) -> tuple:
        """Map a user field name to a record path.

        Accepts a top-level key ('distance_mpc'), a dotted path
        ('redshift.z_spec'), or an unambiguous nested leaf name ('z_spec').
        """
        name = (name or "").strip()
        if not name:
            raise ServiceError("INVALID_ARGUMENT", "field must not be empty")
        if name.split(".")[0] in NON_METADATA_KEYS:
            raise ServiceError(
                "INVALID_ARGUMENT",
                f"'{name}' is tabular rotation-curve data, not a metadata field; "
                "use get_object to retrieve it.",
            )
        path = tuple(name.split("."))
        if path in lc.all_paths:
            return path
        candidates = sorted(lc.leaf_paths.get(name, set()))
        if len(candidates) == 1:
            return candidates[0]
        dotted = [".".join(p) for p in candidates]
        if len(candidates) > 1:
            raise ServiceError(
                "AMBIGUOUS_FIELD",
                f"Field '{name}' occurs at several places in corpus '{lc.spec.key}': "
                f"{dotted}. Use the dotted path.",
                candidates=dotted,
            )
        all_dotted = sorted(".".join(p) for p in lc.all_paths)
        close = get_close_matches(name, all_dotted + list(lc.leaf_paths), n=6, cutoff=0.6)
        raise ServiceError(
            "UNKNOWN_FIELD",
            f"Field '{name}' does not exist in corpus '{lc.spec.key}'."
            + (f" Did you mean: {close}?" if close else " Use get_corpus_schema to list fields."),
            suggestions=close,
        )

    def resolve_object(self, lc: LoadedCorpus, raw_id: str) -> int:
        raw_id = (raw_id or "").strip()
        if not raw_id:
            raise ServiceError("INVALID_ARGUMENT", "object_id must not be empty")
        if raw_id in lc.by_id:
            return lc.by_id[raw_id]
        rows = lc.by_norm.get(normalize(raw_id), []) or lc.by_loose.get(normalize_loose(raw_id), [])
        if len(rows) == 1:
            return rows[0]
        if len(rows) > 1:
            cands = [lc.ids[i] for i in rows]
            raise ServiceError(
                "AMBIGUOUS_OBJECT_ID",
                f"'{raw_id}' matches {len(cands)} records in corpus '{lc.spec.key}' "
                f"(the same galaxy observed by different surveys): {cands}. "
                "Repeat the request with one of these survey-qualified IDs.",
                candidates=cands,
            )
        close_norm = get_close_matches(normalize(raw_id), list(lc.by_norm), n=5, cutoff=0.6)
        sugg = sorted({lc.ids[i] for n in close_norm for i in lc.by_norm[n]})[:5]
        raise ServiceError(
            "OBJECT_NOT_FOUND",
            f"Object '{raw_id}' not found in corpus '{lc.spec.key}'."
            + (f" Did you mean: {sugg}?" if sugg else f" Use list_objects(corpus='{lc.spec.key}') to browse IDs."),
            suggestions=sugg,
        )

    def _row_summary(self, lc: LoadedCorpus, i: int) -> dict:
        r = lc.records[i]
        return {
            "object_id": lc.ids[i],
            "name": display_name(lc.spec.key, r),
            "survey": record_survey(r),
        }

    # ── 1. list_corpora ──
    def list_corpora(self) -> dict:
        rows = []
        for key, lc in self.corpora.items():
            s = lc.spec
            rows.append({
                "key": key,
                "name": s.name,
                "version": lc.version,
                "description": s.description,
                "n_objects": len(lc.records),
                "object_type": s.object_type,
                "redshift_range": s.redshift_range,
                "tracer": s.tracer,
                "zenodo_doi": s.zenodo_doi,
                "source_sha256": lc.sha256,
                "semantic_search": self.semantic.status_for(key) if self.semantic else "disabled",
                "correction_notice": CORRECTION_NOTICES.get(key),
            })
        total = sum(r["n_objects"] for r in rows)
        human = f"{len(rows)} corpora, {total} objects in total:\n" + "\n".join(
            f"- {r['key']}: {r['name']} v{r['version']}, {r['n_objects']} {r['object_type']}s, "
            f"{r['redshift_range']}, DOI {r['zenodo_doi']}"
            for r in rows
        )
        return ok("list_corpora", {"server_version": __version__, "n_total": total, "corpora": rows}, human)

    # ── 2. list_objects ──
    def list_objects(self, corpus: str, survey: Optional[str] = None,
                     quality_tier: Optional[int] = None, limit: int = 100, offset: int = 0) -> dict:
        lc = self._corpus(corpus)
        self._check_page(limit, offset)
        rows = []
        for i, r in enumerate(lc.records):
            if survey and normalize(record_survey(r) or "") != normalize(survey):
                continue
            if quality_tier is not None:
                qt = record_quality_tier(r)
                try:
                    if qt is None or int(qt) != int(quality_tier):
                        continue
                except (TypeError, ValueError):
                    continue
            rows.append(i)
        page = rows[offset: offset + limit]
        data = {
            "corpus": corpus,
            "n_total": len(lc.records),
            "n_filtered": len(rows),
            "n_returned": len(page),
            "offset": offset,
            "limit": limit,
            "object_ids": [lc.ids[i] for i in page],
            "objects": [self._row_summary(lc, i) for i in page],
            "provenance": self.provenance(lc),
        }
        human = (
            f"{len(rows)} of {len(lc.records)} objects in '{corpus}' match"
            + (f" survey={survey}" if survey else "")
            + (f" quality_tier={quality_tier}" if quality_tier is not None else "")
            + f"; showing {len(page)} from offset {offset}: "
            + ", ".join(data["object_ids"][:20])
            + (" ..." if len(page) > 20 else "")
        )
        return ok("list_objects", data, human)

    # ── 3. get_object ──
    def get_object(self, corpus: str, object_id: str) -> dict:
        lc = self._corpus(corpus)
        i = self.resolve_object(lc, object_id)
        r = lc.records[i]
        warnings = []
        om = r.get("omega")
        if isinstance(om, dict) and om.get("omega_available") is False and any(
            k.startswith("legacy_omega") for k in om
        ):
            warnings.append(
                "This record's omega value is WITHDRAWN (omega.omega_available=false). "
                "omega.legacy_omega_value is retained for provenance only and is not a valid measurement."
            )
        data = {
            "corpus": corpus,
            "object_id": lc.ids[i],
            "requested_id": object_id,
            "record": r,
            "provenance": self.provenance(lc),
        }
        human = f"{lc.ids[i]} from {lc.spec.name} v{lc.version} (DOI {lc.spec.zenodo_doi})."
        summary_fields = ["distance_mpc", "inc_deg", "vrot_mean_kms", "vrot_max_kms",
                          "quality_tier", "hubble_type"]
        bits = [f"{f}={r[f]}" for f in summary_fields if r.get(f) is not None]
        if bits:
            human += " " + ", ".join(bits) + "."
        if warnings:
            human += " WARNING: " + " ".join(warnings)
        return ok("get_object", data, human, warnings)

    # ── 4. search_metadata ──
    def search_metadata(self, corpus: str, field: str, value: str,
                        limit: int = 100, offset: int = 0) -> dict:
        lc = self._corpus(corpus)
        self._check_page(limit, offset)
        path = self.resolve_field(lc, field)
        needle = normalize(value or "")
        if not needle:
            raise ServiceError("INVALID_ARGUMENT", "value must not be empty")
        matches = []
        for i, r in enumerate(lc.records):
            v = get_path(r, path)
            if v is None or isinstance(v, (dict, list)):
                continue
            if needle in normalize(v):
                matches.append({**self._row_summary(lc, i), "match": v})
        page = matches[offset: offset + limit]
        dotted = ".".join(path)
        data = {
            "corpus": corpus,
            "field": field,
            "resolved_field": dotted,
            "value": value,
            "match_rule": "case-insensitive substring; spaces, underscores and hyphens ignored",
            "n_matched": len(matches),
            "n_returned": len(page),
            "offset": offset,
            "limit": limit,
            "results": page,
            "provenance": self.provenance(lc),
        }
        human = (
            f"{len(matches)} objects in '{corpus}' have {dotted} containing '{value}'"
            + (": " + ", ".join(m["object_id"] for m in page[:20]) if page else ".")
            + (" ..." if len(page) > 20 else "")
        )
        return ok("search_metadata", data, human)

    # ── 5. filter_objects ──
    def filter_objects(self, corpus: str, field: str, min_val: Optional[float] = None,
                       max_val: Optional[float] = None, omega_ready_only: bool = False,
                       limit: int = 100, offset: int = 0) -> dict:
        lc = self._corpus(corpus)
        self._check_page(limit, offset)
        if min_val is not None and max_val is not None and min_val > max_val:
            raise ServiceError("INVALID_ARGUMENT", f"min_val ({min_val}) must be <= max_val ({max_val})")
        path = self.resolve_field(lc, field)
        matches, n_numeric = [], 0
        for i, r in enumerate(lc.records):
            if omega_ready_only and not omega_ready(r):
                continue
            v = get_path(r, path)
            if isinstance(v, bool) or v is None:
                continue
            try:
                num = float(v)
            except (TypeError, ValueError):
                continue
            n_numeric += 1
            if min_val is not None and num < min_val:
                continue
            if max_val is not None and num > max_val:
                continue
            matches.append({**self._row_summary(lc, i), "value": num})
        page = matches[offset: offset + limit]
        dotted = ".".join(path)
        data = {
            "corpus": corpus,
            "field": field,
            "resolved_field": dotted,
            "min_val": min_val,
            "max_val": max_val,
            "bounds": "inclusive",
            "omega_ready_only": omega_ready_only,
            "n_total": len(lc.records),
            "n_with_numeric_value": n_numeric,
            "n_matched": len(matches),
            "n_returned": len(page),
            "offset": offset,
            "limit": limit,
            "results": page,
            "provenance": self.provenance(lc),
        }
        rng = f"{'-inf' if min_val is None else min_val} <= {dotted} <= {'inf' if max_val is None else max_val}"
        human = (
            f"{len(matches)} of {len(lc.records)} objects in '{corpus}' satisfy {rng}"
            + (" (omega-ready only)" if omega_ready_only else "")
            + f"; {n_numeric} records have a numeric {dotted}."
        )
        warnings = []
        if n_numeric == 0:
            warnings.append(f"No record in '{corpus}' has a numeric value for {dotted}.")
        return ok("filter_objects", data, human, warnings)

    # ── 6. get_corpus_schema ──
    def get_corpus_schema(self, corpus: str) -> dict:
        lc = self._corpus(corpus)
        fields: dict[str, dict] = {}
        for p in sorted(lc.all_paths):
            types, n = set(), 0
            for r in lc.records:
                v = get_path(r, p)
                if v is not None:
                    n += 1
                    types.add(type(v).__name__)
            fields[".".join(p)] = {"types": sorted(types), "n_non_null": n}
        columns = {}
        for r in lc.records:
            if isinstance(r.get("columns"), dict):
                columns = r["columns"]
                break
        data = {
            "corpus": corpus,
            "name": lc.spec.name,
            "version": lc.version,
            "n_records": len(lc.records),
            "id_format": {
                "gc": "cluster_id, e.g. 'NGC 104'",
                "intz": "'SURVEY:name', e.g. 'KROSS:C-HiZ_z1_111'",
            }.get(corpus, "'SURVEY:galaxy', e.g. 'SPARC:NGC0024'; bare names accepted when unique"),
            "metadata_fields": fields,
            "data_columns": columns,
            "field_name_rules": "Use a top-level name, a dotted path, or a unique nested leaf name.",
            "provenance": self.provenance(lc),
        }
        human = (
            f"Corpus '{corpus}' ({lc.spec.name} v{lc.version}) has {len(lc.records)} records and "
            f"{len(fields)} metadata fields. Examples: "
            + ", ".join(list(fields)[:25])
        )
        return ok("get_corpus_schema", data, human)

    # ── 7. semantic_search ──
    def semantic_search(self, corpus: str, query: str, top_k: int = 5) -> dict:
        if not (query or "").strip():
            raise ServiceError("INVALID_ARGUMENT", "query must not be empty")
        if not 1 <= int(top_k) <= 50:
            raise ServiceError("INVALID_ARGUMENT", "top_k must be between 1 and 50")
        keys = CORPUS_KEYS if corpus == "all" else [self._corpus(corpus).spec.key]
        if self.semantic is None:
            raise ServiceError(
                "SEMANTIC_UNAVAILABLE",
                "Semantic search is disabled in this deployment. The other six tools are unaffected.",
            )
        hits = self.semantic.search(keys, query, int(top_k))   # may raise ServiceError
        results = []
        for h in hits:
            lc = self.corpora[h["corpus"]]
            row = lc.by_id.get(h["id"])
            results.append({
                "rank": len(results) + 1,
                "corpus": h["corpus"],
                "id": h["id"],
                "object_id": h["id"],
                "name": display_name(h["corpus"], lc.records[row]) if row is not None else None,
                "score": h["score"],
                "cosine_similarity": h["cosine_similarity"],
                "text": h["text"],
            })
        data = {
            "corpus": corpus,
            "query": query,
            "top_k": int(top_k),
            "n_returned": len(results),
            "metric": "squared L2 distance between unit-normalised MiniLM embeddings (lower = closer); "
                      "cosine_similarity = 1 - score/2",
            "embedding_model": self.semantic.model_name,
            "index_sha256": {k: self.semantic.index_sha256(k) for k in keys},
            "results": results,
            "caution": "Semantic rank is a discovery aid, not a measurement. Retrieve values with get_object.",
        }
        human = f"Top {len(results)} semantic matches for '{query}' in {corpus}:\n" + "\n".join(
            f"{r['rank']}. {r['id']} ({r['corpus']}) score={r['score']:.3f}" for r in results
        )
        return ok("semantic_search", data, human)

    # ── dispatch used by every interface ──
    def call(self, tool: str, **kwargs: Any) -> dict:
        fn = {
            "list_corpora": self.list_corpora,
            "list_objects": self.list_objects,
            "get_object": self.get_object,
            "search_metadata": self.search_metadata,
            "filter_objects": self.filter_objects,
            "get_corpus_schema": self.get_corpus_schema,
            "semantic_search": self.semantic_search,
        }.get(tool)
        if fn is None:
            return fail(tool, ServiceError("UNKNOWN_TOOL", f"Unknown tool '{tool}'"))
        try:
            return fn(**kwargs)
        except ServiceError as e:
            return fail(tool, e)
        except Exception as e:  # never leak a traceback to an MCP client
            logger.exception("tool %s failed", tool)
            return fail(tool, ServiceError("INTERNAL_ERROR", f"{type(e).__name__}: {e}"))

    def health(self) -> dict:
        sem = self.semantic.status() if self.semantic else {"state": "disabled"}
        loaded = {k: len(c.records) for k, c in self.corpora.items()}
        healthy = sum(loaded.values()) == EXPECTED_TOTAL
        return {
            "status": "ok" if healthy and sem.get("state") in
                      ("ready", "disabled", "loading", "not_loaded") else "degraded",
            "server": "eps-astro-rag-mcp",
            "version": __version__,
            "transport": {"mcp": "/mcp (Streamable HTTP, JSON-RPC 2.0); no SSE endpoint",
                          "rest": "/api/*", "docs": "/docs", "ui": "/"},
            "data_layout": self.layout.kind,
            "corpora": {k: {"records": len(c.records), "version": c.version, "sha256": c.sha256}
                        for k, c in self.corpora.items()},
            "n_total": sum(loaded.values()),
            "checksums": self.checksum_report,
            "semantic_search": sem,
        }
