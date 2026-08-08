#!/usr/bin/env python3
"""
EPS Astro-RAG omega remediation audit (Node1/local repository)
Generated 2026-08-07.

Run from the repository root:
    python3 audit_omega_remediation_v2.py

The script does not modify repository files. It:
- captures git provenance/status
- scans source/docs/notebooks for the known buggy Eq.6 pattern
- checks for stale sign-reversal / "recomputation in progress" text
- validates Z1 CSV/JSON omega signs and computes the true statistical median
- validates IntZ current omega fields are unavailable/null while permitting legacy_omega_value
- compares local data-file MD5 hashes with the current Zenodo records when files are found
- checks the public API health endpoint
- writes a JSON audit report in the repository root
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import statistics
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()

ZENODO_MD5 = {
    # Z1 v3 — Zenodo 21834678
    "high_z_kinematic_corpus_Z1.json": "1a5136bf36a226f0df2dfa504ef9c740",
    "omega_results_z1.csv": "95a77c2192dd2ea9b3438734bb7d0bf6",
    "fig_hz_nb3_eps_omega_bridge.png": "12634d7f7f0ad62e83e65abaa02bea08",
    # IntZ v2 — Zenodo 21841382
    "intz_corpus_v1b.json": "ebdcacc95805009423ff950b040da647",
    "intz_corpus_v1b.jsonl": "0030a2d765c06c4382c1c1ba4418e5dd",
    "intz_corpus_v1b_flat.csv": "21804f6c3a6b9e6a394e60eb82eb8369",
}

BUG_PATTERNS = [
    re.compile(r"\(\s*V2\s*/\s*R2\s*-\s*V1\s*/\s*R1\s*\)\s*\*\s*\(\s*R1\s*/\s*R2\s*\)\s*\*\*\s*1\.5", re.I),
    re.compile(r"\(\s*V_?2\s*/\s*R_?2\s*-\s*V_?1\s*/\s*R_?1\s*\)\s*[·×*]\s*\(\s*R_?1\s*/\s*R_?2\s*\)\s*(?:\^|\*\*)\s*1\.5", re.I),
]

STALE_PATTERNS = {
    "recomputation_in_progress": re.compile(r"recomputation\s+in\s+progress", re.I),
    "negative_z1_13_05": re.compile(r"(?:−|-)\s*13\.05"),
    "negative_kross_9_09": re.compile(r"(?:−|-)\s*9\.0?9"),
    "sign_reversal_claim": re.compile(r"\b(?:robust|monotonic|kinematic)?\s*sign\s+reversal\b", re.I),
}

TEXT_SUFFIXES = {".py", ".md", ".txt", ".ipynb", ".json", ".jsonl", ".csv", ".yaml", ".yml", ".toml"}

def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {"returncode": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}

def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)

def find_named(name: str):
    # Ignore .git internals.
    return sorted(p for p in ROOT.rglob(name) if ".git" not in p.parts)

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def omega_obj_value(g):
    om = g.get("omega")
    if isinstance(om, dict):
        for key in ("omega_value_rad_gyr", "omega_rad_gyr", "omega_value"):
            v = om.get(key)
            if isinstance(v, (int, float)):
                return float(v)
    return None

report = {
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "root": str(ROOT),
    "git": {},
    "bug_formula_hits": [],
    "stale_claim_hits": {},
    "zenodo_md5": {},
    "z1": {},
    "intz": {},
    "api": {},
    "critical_failures": [],
    "warnings": [],
}

# ---- Git provenance ----
report["git"]["head"] = run(["git", "rev-parse", "HEAD"])
report["git"]["branch"] = run(["git", "branch", "--show-current"])
report["git"]["status"] = run(["git", "status", "--short"])
report["git"]["last_commit"] = run(["git", "log", "-1", "--oneline", "--decorate"])

# ---- Repository-wide scan ----
stale_hits = {k: [] for k in STALE_PATTERNS}
for p in ROOT.rglob("*"):
    if not p.is_file() or ".git" in p.parts or p.suffix.lower() not in TEXT_SUFFIXES or p.name == "CORRECTIONS.md" or p.name == "audit_omega_remediation_v2.py":
        continue
    # Avoid very large downloaded corpora for free-text stale-claim scan except notebooks/docs/code.
    if p.stat().st_size > 20_000_000:
        continue
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue

    for pat in BUG_PATTERNS:
        if pat.search(text):
            # Collect matching lines for quick remediation.
            for n, line in enumerate(text.splitlines(), 1):
                if pat.search(line):
                    report["bug_formula_hits"].append({"file": rel(p), "line": n, "text": line[:500]})

    # Stale prose is most meaningful in docs/notebooks/papers, not legacy dataset fields.
    if p.suffix.lower() in {".md", ".txt", ".ipynb", ".py"} or "paper" in str(p).lower():
        for label, pat in STALE_PATTERNS.items():
            for n, line in enumerate(text.splitlines(), 1):
                if pat.search(line):
                    stale_hits[label].append({"file": rel(p), "line": n, "text": line[:500]})

report["stale_claim_hits"] = stale_hits

if report["bug_formula_hits"]:
    report["critical_failures"].append(
        f"Known buggy Eq.6 parenthesization remains in {len(report['bug_formula_hits'])} source/doc/notebook line(s)."
    )

# ---- Hash comparisons ----
for name, expected in ZENODO_MD5.items():
    matches = find_named(name)
    if not matches:
        report["zenodo_md5"][name] = {"found": False, "expected": expected}
        continue
    entries = []
    for p in matches:
        actual = md5(p)
        entries.append({"path": rel(p), "actual": actual, "expected": expected, "match": actual == expected})
    report["zenodo_md5"][name] = {"found": True, "files": entries}
    for e in entries:
        if not e["match"]:
            report["warnings"].append(f"MD5 differs from current Zenodo file: {e['path']}")

# ---- Z1 CSV ----
z1_csvs = find_named("omega_results_z1.csv")
if z1_csvs:
    p = z1_csvs[0]
    with p.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    vals = []
    for r in rows:
        for key in ("omega_rad_gyr", "omega_value_rad_gyr", "omega"):
            raw = r.get(key)
            if raw not in (None, ""):
                try:
                    vals.append(float(raw))
                    break
                except ValueError:
                    pass
    if vals:
        report["z1"]["csv"] = {
            "path": rel(p),
            "n": len(vals),
            "n_positive": sum(v > 0 for v in vals),
            "n_negative": sum(v < 0 for v in vals),
            "median": statistics.median(vals),
            "mean": statistics.mean(vals),
            "min": min(vals),
            "max": max(vals),
            "sorted": sorted(vals),
        }
        if any(v <= 0 for v in vals):
            report["critical_failures"].append("Z1 corrected CSV contains non-positive omega value(s).")
        # Public Zenodo/GitHub currently state +13.776 as "median"; true median of 8 values is ~12.621.
        if abs(statistics.median(vals) - 12.621) > 0.01:
            report["critical_failures"].append(
                f"Z1 summary-statistic mismatch: true median={statistics.median(vals):.6f}, not +12.621."
            )
else:
    report["warnings"].append("omega_results_z1.csv not found locally.")

# ---- Z1 JSON ----
z1_jsons = find_named("high_z_kinematic_corpus_Z1.json")
if z1_jsons:
    p = z1_jsons[0]
    try:
        z1 = load_json(p)
        gals = z1.get("galaxies", [])
        rot = [g for g in gals if g.get("is_rotator") and g.get("quality_tier") == 1]
        vals = [omega_obj_value(g) for g in rot]
        vals = [v for v in vals if v is not None]
        versions = []
        for g in rot:
            om = g.get("omega")
            if isinstance(om, dict) and om.get("formula_version"):
                versions.append(om.get("formula_version"))
        report["z1"]["json"] = {
            "path": rel(p), "tier1_rotators": len(rot), "omega_values_found": len(vals),
            "all_positive": bool(vals) and all(v > 0 for v in vals),
            "median": statistics.median(vals) if vals else None,
            "mean": statistics.mean(vals) if vals else None,
            "formula_versions": sorted(set(versions)),
        }
        if vals and not all(v > 0 for v in vals):
            report["critical_failures"].append("Z1 JSON contains non-positive corrected omega value(s).")
    except Exception as e:
        report["warnings"].append(f"Could not parse Z1 JSON {rel(p)}: {e}")
else:
    report["warnings"].append("high_z_kinematic_corpus_Z1.json not found locally.")

# ---- IntZ JSON ----
intz_jsons = find_named("intz_corpus_v1b.json")
if intz_jsons:
    p = intz_jsons[0]
    try:
        iz = load_json(p)
        gals = iz.get("galaxies", [])
        available = 0
        active_nonnull = []
        legacy_count = 0
        for g in gals:
            om = g.get("omega")
            if not isinstance(om, dict):
                continue
            if om.get("omega_available") is True:
                available += 1
            active = om.get("omega_value_rad_gyr")
            if active is not None:
                active_nonnull.append(active)
            if om.get("legacy_omega_value") is not None:
                legacy_count += 1
        report["intz"]["json"] = {
            "path": rel(p), "galaxies": len(gals), "omega_available_true": available,
            "active_omega_nonnull": len(active_nonnull), "legacy_omega_values": legacy_count,
        }
        if available or active_nonnull:
            report["critical_failures"].append(
                f"IntZ current omega not fully nulled: omega_available_true={available}, active_nonnull={len(active_nonnull)}."
            )
    except Exception as e:
        report["warnings"].append(f"Could not parse IntZ JSON {rel(p)}: {e}")
else:
    report["warnings"].append("intz_corpus_v1b.json not found locally.")

# ---- IntZ flat CSV ----
intz_csvs = find_named("intz_corpus_v1b_flat.csv")
if intz_csvs:
    p = intz_csvs[0]
    with p.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    true_avail = []
    active_nonnull = []
    for i, r in enumerate(rows, 2):
        av = str(r.get("omega_available", "")).strip().lower()
        if av in {"true", "1", "yes"}:
            true_avail.append(i)
        v = str(r.get("omega_value_rad_gyr", "")).strip()
        if v and v.lower() not in {"null", "none", "nan"}:
            active_nonnull.append((i, v))
    report["intz"]["csv"] = {
        "path": rel(p), "rows": len(rows), "omega_available_true": len(true_avail),
        "active_omega_nonnull": len(active_nonnull),
    }
    if true_avail or active_nonnull:
        report["critical_failures"].append(
            f"IntZ CSV current omega not fully nulled: available_true={len(true_avail)}, active_nonnull={len(active_nonnull)}."
        )

# ---- API health ----
try:
    with urllib.request.urlopen("https://dflynn5656-astro-rag-mcp.hf.space/health", timeout=15) as r:
        body = r.read().decode("utf-8", errors="replace")
    report["api"]["health"] = {"ok": True, "body": body}
except Exception as e:
    report["api"]["health"] = {"ok": False, "error": str(e)}
    report["warnings"].append(f"API health check failed: {e}")

# ---- Human-readable summary ----
print("=" * 78)
print("EPS ASTRO-RAG OMEGA REMEDIATION AUDIT — LOCAL NODE")
print("=" * 78)
print(f"Root: {ROOT}")
print(f"Git HEAD: {report['git']['head']['stdout']}")
print(f"Branch:   {report['git']['branch']['stdout']}")
status = report["git"]["status"]["stdout"]
print(f"Git status: {'CLEAN' if not status else 'DIRTY'}")
if status:
    print(status)

print("\nKnown buggy Eq.6 hits:", len(report["bug_formula_hits"]))
for h in report["bug_formula_hits"][:30]:
    print(f"  FAIL {h['file']}:{h['line']}  {h['text']}")

if report.get("z1", {}).get("csv"):
    z = report["z1"]["csv"]
    print("\nZ1 CSV:")
    print(f"  N={z['n']}  positive={z['n_positive']}  negative={z['n_negative']}")
    print(f"  TRUE median={z['median']:.6f}  mean={z['mean']:.6f}")
    print("  NOTE: with N=8, median is the average of the 4th and 5th sorted values.")

if report.get("intz", {}).get("json"):
    i = report["intz"]["json"]
    print("\nIntZ JSON:")
    print(f"  galaxies={i['galaxies']}  omega_available_true={i['omega_available_true']}  "
          f"active_omega_nonnull={i['active_omega_nonnull']}  legacy={i['legacy_omega_values']}")

print("\nZenodo MD5 comparisons:")
for name, x in report["zenodo_md5"].items():
    if not x.get("found"):
        print(f"  MISSING {name}")
    else:
        for e in x["files"]:
            print(f"  {'PASS' if e['match'] else 'DIFF'} {e['path']}")

print("\nCritical failures:", len(report["critical_failures"]))
for x in report["critical_failures"]:
    print("  FAIL:", x)
print("Warnings:", len(report["warnings"]))
for x in report["warnings"]:
    print("  WARN:", x)

out = ROOT / f"audit_results_omega_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nJSON report written: {out}")
print("=" * 78)

sys.exit(1 if report["critical_failures"] else 0)
