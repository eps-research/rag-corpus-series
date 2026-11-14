#!/usr/bin/env python3
"""Retrieval benchmark for semantic_search: MiniLM + FAISS against a BM25 baseline.

Queries are natural-language discovery requests of the kind an LLM client
sends. Relevance is not judged by eye: every query has a predicate on the
served records (survey, numeric range, flag), so the judgments are exact,
reproducible and auditable. Grade 2 = meets the full request; grade 1 = meets
its main criterion only (where a query has two parts). Both systems rank the
same index texts (faiss/<stem>_texts.json) within the query's corpus.

Metrics per query (k = 10): P@5, P@10, R@10 (recall against min(|rel|, 10),
so large relevant sets are not penalised), nDCG@10 (graded), MRR, and
chance-corrected nDCG@10 (nDCG@10 minus the random-ranking expectation).

Systems: MiniLM + FAISS (as served), Okapi BM25, a hybrid that fuses the two
full rankings by reciprocal rank fusion (RRF, k = 60; Cormack et al. 2009),
and random ranking (mean of 200 draws).

Uncertainty (per-query scores are paired across systems): 95 % percentile
intervals on the mean difference in nDCG@10 from a paired bootstrap over
queries (10,000 resamples), and two-sided p-values from a paired sign-flip
permutation test (100,000 random sign assignments). Both use fixed seeds. The
results are also stratified by base rate (fraction of the corpus that is
relevant), because queries with large relevant sets barely discriminate.

Usage:
  python tools/semantic_benchmark.py                 # MiniLM (needs the model) and BM25
  python tools/semantic_benchmark.py --systems bm25  # baseline only, no model
Writes semantic_benchmark.json and semantic_benchmark.md.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

K = 10


def g(r: dict, path: str):
    for p in path.split("."):
        if not isinstance(r, dict):
            return None
        r = r.get(p)
    return r


def num(r, path, op, x):
    v = g(r, path)
    try:
        v = float(v)
    except (TypeError, ValueError):
        return False
    return v < x if op == "<" else v > x


# (id, corpus, query, grade-2 predicate, grade-1 predicate or None)
QUERIES = [
    ("v7-slow", "v7", "slowly rotating dwarf galaxies with maximum rotation velocity below 50 km/s",
     lambda r: num(r, "vrot_max_kms", "<", 50), lambda r: num(r, "vrot_max_kms", "<", 80)),
    ("v7-fast", "v7", "massive fast-rotating spiral galaxies with rotation velocities above 250 km/s",
     lambda r: num(r, "vrot_max_kms", ">", 250), lambda r: num(r, "vrot_max_kms", ">", 200)),
    ("v7-bulge", "v7", "SPARC galaxies with a bulge component",
     lambda r: r.get("survey") == "SPARC" and r.get("has_bulge") is True, lambda r: r.get("has_bulge") is True),
    ("v7-edgeon", "v7", "nearly edge-on galaxies with inclination above 80 degrees",
     lambda r: num(r, "inc_deg", ">", 80), lambda r: num(r, "inc_deg", ">", 70)),
    ("v7-near", "v7", "nearby galaxies closer than 5 Mpc",
     lambda r: num(r, "distance_mpc", "<", 5), lambda r: num(r, "distance_mpc", "<", 8)),
    ("v7-wallaby", "v7", "WALLABY survey rotation curves", lambda r: r.get("survey") == "WALLABY", None),
    ("v7-lt", "v7", "LITTLE THINGS dwarf irregular galaxies", lambda r: r.get("survey") == "LITTLE_THINGS", None),
    ("v7-extended", "v7", "very extended HI rotation curves reaching beyond 30 kpc",
     lambda r: num(r, "r_max_kpc", ">", 30), lambda r: num(r, "r_max_kpc", ">", 20)),
    ("dw-sculptor", "dwarf", "dwarf galaxies in the Sculptor group", lambda r: r.get("group_member") == "Sculptor", None),
    ("dw-angst", "dwarf", "VLA-ANGST galaxies with velocities from HI profile widths",
     lambda r: r.get("survey") == "VLA_ANGST", None),
    ("dw-gasrich", "dwarf", "gas-rich dwarfs with a high HI to dynamical mass ratio above 0.1",
     lambda r: num(r, "mhi_mdyn_ratio", ">", 0.1), lambda r: num(r, "mhi_mdyn_ratio", ">", 0.07)),
    ("dw-trgb", "dwarf", "dwarf galaxies with TRGB distances closer than 3 Mpc",
     lambda r: r.get("distance_method") == "TRGB" and num(r, "distance_mpc", "<", 3),
     lambda r: num(r, "distance_mpc", "<", 3)),
    ("gc-metalpoor", "gc", "metal-poor globular clusters with [Fe/H] below -2",
     lambda r: num(r, "metallicity.feh", "<", -2), lambda r: num(r, "metallicity.feh", "<", -1.7)),
    ("gc-metalrich", "gc", "metal-rich globular clusters in the inner Galaxy",
     lambda r: num(r, "metallicity.feh", ">", -0.8) and g(r, "flags.inner_galaxy") is True,
     lambda r: num(r, "metallicity.feh", ">", -0.8)),
    ("gc-cc", "gc", "core-collapsed globular clusters", lambda r: g(r, "structure.core_collapsed") is True, None),
    ("gc-sgr", "gc", "globular clusters associated with the Sagittarius stream",
     lambda r: g(r, "flags.sgr_stream") is True, None),
    ("gc-outer", "gc", "distant outer halo clusters more than 50 kpc from the Galactic centre",
     lambda r: num(r, "baumgardt2023.r_gc_kpc", ">", 50), lambda r: num(r, "baumgardt2023.r_gc_kpc", ">", 30)),
    ("gc-massive", "gc", "massive globular clusters above one million solar masses",
     lambda r: num(r, "baumgardt2023.mass_msun", ">", 1e6), lambda r: num(r, "baumgardt2023.mass_msun", ">", 5e5)),
    ("iz-z2", "intz", "star-forming galaxies at redshift above 2",
     lambda r: num(r, "redshift.z_spec", ">", 2), lambda r: num(r, "redshift.z_spec", ">", 1.5)),
    ("iz-kmos3d", "intz", "KMOS3D survey galaxies", lambda r: g(r, "identifiers.survey") == "KMOS3D", None),
    ("iz-sfr", "intz", "galaxies with star formation rates above 50 solar masses per year",
     lambda r: num(r, "stellar_properties.sfr_msun_yr", ">", 50),
     lambda r: num(r, "stellar_properties.sfr_msun_yr", ">", 20)),
    ("iz-massive", "intz", "massive galaxies with stellar mass above 10^10.8 solar masses",
     lambda r: num(r, "stellar_properties.log_mass_msun", ">", 10.8),
     lambda r: num(r, "stellar_properties.log_mass_msun", ">", 10.6)),
    ("z1-rot", "z1", "confirmed rotating disks at redshift above 4", lambda r: r.get("is_rotator") is True, None),
    ("z1-merger", "z1", "merging galaxies in ALPINE", lambda r: r.get("is_merger") is True, None),
    ("z1-dis", "z1", "dispersion-dominated galaxies without ordered rotation",
     lambda r: r.get("is_dispersion_dom") is True, None),
]


# Queries whose request hinges on a numeric threshold; the others ask for a
# survey, group, class or flag. Reported separately because the two kinds
# behave differently.
NUMERIC = {"v7-slow", "v7-fast", "v7-edgeon", "v7-near", "v7-extended", "dw-gasrich", "dw-trgb",
           "gc-metalpoor", "gc-metalrich", "gc-outer", "gc-massive", "iz-z2", "iz-sfr", "iz-massive"}


# ── BM25 (Okapi; Robertson & Zaragoza 2009), k1 = 1.2, b = 0.75 ──
TOKEN = re.compile(r"[a-z0-9]+(?:[.\-][a-z0-9]+)*")


def tokens(s: str) -> list[str]:
    return TOKEN.findall(s.lower())


class BM25:
    def __init__(self, docs: list[str], k1: float = 1.2, b: float = 0.75):
        self.docs = [Counter(tokens(d)) for d in docs]
        self.len = [sum(d.values()) for d in self.docs]
        self.avg = statistics.fmean(self.len)
        df = Counter(t for d in self.docs for t in d)
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self.k1, self.b = k1, b

    def rank(self, query: str, k: int) -> list[int]:
        q = tokens(query)
        scores = []
        for i, d in enumerate(self.docs):
            s = 0.0
            for t in q:
                f = d.get(t)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.len[i] / self.avg))
            scores.append((-s, i))
        scores.sort()
        return [i for _, i in scores[:k]]


def metrics(ranked: list[str], grade: dict[str, int]) -> dict[str, float]:
    rel = [grade.get(x, 0) for x in ranked[:K]]
    n_rel = sum(1 for v in grade.values() if v >= 2) or sum(1 for v in grade.values() if v >= 1)
    hit = [1 if v >= 2 else 0 for v in rel] if any(v >= 2 for v in grade.values()) else [1 if v else 0 for v in rel]
    dcg = sum((2 ** v - 1) / math.log2(i + 2) for i, v in enumerate(rel))
    ideal = sorted(grade.values(), reverse=True)[:K]
    idcg = sum((2 ** v - 1) / math.log2(i + 2) for i, v in enumerate(ideal)) or 1.0
    first = next((i for i, h in enumerate(hit) if h), None)
    return {"P@5": sum(hit[:5]) / 5, "P@10": sum(hit) / K, "R@10": sum(hit) / min(n_rel, K) if n_rel else 0.0,
            "nDCG@10": dcg / idcg, "MRR": 1 / (first + 1) if first is not None else 0.0}


def run(service, systems: list[str], seed: int = 0) -> dict:
    sem = service.semantic
    out = {"k": K, "queries": [], "systems": systems + ["random"]}
    rng = random.Random(seed)
    bm25 = {}
    for qid, corpus, text, p2, p1 in QUERIES:
        lc = service.corpora[corpus]
        ci = sem.indexes[corpus]
        grade = {}
        for oid in ci.ids:
            r = lc.records[lc.by_id[oid]]
            grade[oid] = 2 if p2(r) else (1 if p1 and p1(r) else 0)
        n2, n1 = sum(v == 2 for v in grade.values()), sum(v == 1 for v in grade.values())
        row = {"id": qid, "corpus": corpus, "query": text, "n_docs": len(grade), "n_grade2": n2, "n_grade1": n1}
        full = {}
        if "minilm" in systems:
            hits, _ = sem.search([corpus], text, len(ci.ids))
            full["minilm"] = [h["id"] for h in hits]
            row["minilm"] = metrics(full["minilm"], grade)
            row["minilm_top"] = full["minilm"][:5]
        if "bm25" in systems:
            if corpus not in bm25:
                bm25[corpus] = BM25(ci.texts)
            full["bm25"] = [ci.ids[i] for i in bm25[corpus].rank(text, len(ci.ids))]
            row["bm25"] = metrics(full["bm25"], grade)
        if "hybrid" in systems:
            row["hybrid"] = metrics(rrf([full["minilm"], full["bm25"]]), grade)
        row["base_rate"] = (n2 or n1) / len(grade)
        rnd = [metrics(rng.sample(ci.ids, K), grade) for _ in range(200)]
        row["random"] = {m: statistics.fmean(x[m] for x in rnd) for m in rnd[0]}
        out["queries"].append(row)
    for q in out["queries"]:
        for sy in out["systems"]:
            q[sy]["cnDCG@10"] = q[sy]["nDCG@10"] - q["random"]["nDCG@10"]
    ms = ("P@5", "P@10", "R@10", "nDCG@10", "MRR", "cnDCG@10")
    out["mean"] = {s: {m: statistics.fmean(q[s][m] for q in out["queries"]) for m in ms} for s in out["systems"]}
    for q in out["queries"]:
        q["kind"] = "numeric" if q["id"] in NUMERIC else "categorical"
    out["mean_by_kind"] = {
        kind: {s: {m: statistics.fmean(q[s][m] for q in out["queries"] if q["kind"] == kind) for m in ms}
               for s in out["systems"]}
        for kind in ("categorical", "numeric")}
    out["strata"] = {}
    for name, lo, hi in STRATA:
        qs = [q for q in out["queries"] if lo <= q["base_rate"] < hi]
        if qs:
            out["strata"][name] = {"n": len(qs), **{s: {m: statistics.fmean(q[s][m] for q in qs)
                                                        for m in ("nDCG@10", "cnDCG@10")}
                                                    for s in out["systems"]}}
    out["paired"] = paired_stats(out)
    return out


# Base-rate strata: fraction of the corpus that satisfies the request.
STRATA = (("base rate < 5%", 0.0, 0.05), ("5-20%", 0.05, 0.20), ("> 20%", 0.20, 1.01))

RRF_K = 60


def rrf(rankings: list[list[str]], k: int = RRF_K) -> list[str]:
    """Reciprocal rank fusion (Cormack, Clarke & Buettcher 2009) of full rankings."""
    score: dict[str, float] = {}
    for rk in rankings:
        for i, x in enumerate(rk):
            score[x] = score.get(x, 0.0) + 1.0 / (k + i + 1)
    return sorted(score, key=lambda x: (-score[x], x))


def paired_stats(res: dict, metric: str = "nDCG@10", n_boot: int = 10_000,
                 n_perm: int = 100_000, seed: int = 0) -> list[dict]:
    """Paired bootstrap CI and sign-flip permutation p for mean differences."""
    sysnames = [s for s in res["systems"] if s != "random"]
    pairs = [(a, b) for i, a in enumerate(sysnames) for b in sysnames[i + 1:]]
    pairs += [(a, "random") for a in sysnames]
    out = []
    for subset in ("all", "categorical", "numeric"):
        qs = [q for q in res["queries"] if subset == "all" or q["kind"] == subset]
        n = len(qs)
        for a, b in pairs:
            d = [q[a][metric] - q[b][metric] for q in qs]
            mean = statistics.fmean(d)
            rng = random.Random(seed)
            boots = sorted(statistics.fmean(rng.choices(d, k=n)) for _ in range(n_boot))
            lo, hi = boots[int(0.025 * n_boot)], boots[int(0.975 * n_boot) - 1]
            rng = random.Random(seed + 1)
            obs = abs(mean)
            ge = sum(abs(statistics.fmean(x if rng.random() < 0.5 else -x for x in d)) >= obs - 1e-12
                     for _ in range(n_perm))
            out.append({"subset": subset, "n": n, "a": a, "b": b, "metric": metric,
                        "mean_diff": mean, "ci95": [lo, hi], "p_perm": (ge + 1) / (n_perm + 1)})
    return out


def markdown(res: dict) -> str:
    ms = ("P@5", "P@10", "R@10", "nDCG@10", "MRR", "cnDCG@10")
    lines = [f"Mean over {len(res['queries'])} queries (k = {res['k']}):", "",
             "| System | " + " | ".join(ms) + " |", "|---|" + "---|" * len(ms)]
    for s in res["systems"]:
        lines.append(f"| {s} | " + " | ".join(f"{res['mean'][s][m]:.2f}" for m in ms) + " |")
    lines += ["", "nDCG@10 by query kind:", "", "| Kind | n | " + " | ".join(res["systems"]) + " |",
              "|---|---|" + "---|" * len(res["systems"])]
    for kind, d in res["mean_by_kind"].items():
        n = sum(q["kind"] == kind for q in res["queries"])
        lines.append(f"| {kind} | {n} | " + " | ".join(f"{d[s]['nDCG@10']:.2f}" for s in res["systems"]) + " |")
    lines += ["", "nDCG@10 (chance-corrected) by base rate:", "",
              "| Stratum | n | " + " | ".join(res["systems"]) + " |", "|---|---|" + "---|" * len(res["systems"])]
    for name, d in res["strata"].items():
        lines.append(f"| {name} | {d['n']} | " + " | ".join(
            f"{d[s]['nDCG@10']:.2f} ({d[s]['cnDCG@10']:+.2f})" for s in res["systems"]) + " |")
    lines += ["", "Paired differences in nDCG@10 (bootstrap 95% CI, sign-flip permutation p):", "",
              "| Subset | n | A - B | mean diff | 95% CI | p |", "|---|---|---|---|---|---|"]
    for r in res["paired"]:
        lines.append(f"| {r['subset']} | {r['n']} | {r['a']} - {r['b']} | {r['mean_diff']:+.3f} | "
                     f"[{r['ci95'][0]:+.3f}, {r['ci95'][1]:+.3f}] | {r['p_perm']:.3f} |")
    lines += ["", "| Query | Corpus | relevant (grade 2 / 1) | " + " | ".join(f"{s} nDCG@10" for s in res["systems"]) + " |",
              "|---|---|---|" + "---|" * len(res["systems"])]
    for q in res["queries"]:
        lines.append(f"| {q['query']} | {q['corpus']} | {q['n_grade2']} / {q['n_grade1']} of {q['n_docs']} | "
                     + " | ".join(f"{q[s]['nDCG@10']:.2f}" for s in res["systems"]) + " |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--systems", default="minilm,bm25,hybrid")
    ap.add_argument("--data-dir")
    ap.add_argument("--out", default="semantic_benchmark")
    a = ap.parse_args(argv)
    from astro_rag_mcp.server import build_service

    systems = [s for s in a.systems.split(",") if s]
    service = build_service(a.data_dir, semantic=True)
    if "minilm" in systems:
        service.semantic.start_model_load(background=False)
        st = service.semantic.status()
        print(f"model {st['embedding_model']} revision {st['embedding_revision']}", file=sys.stderr)
    res = run(service, systems)
    if "minilm" in systems:
        res["embedding_model"] = service.semantic.model_name
        res["embedding_revision"] = service.semantic.status()["embedding_revision"]
    Path(a.out + ".json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    md = markdown(res)
    Path(a.out + ".md").write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
