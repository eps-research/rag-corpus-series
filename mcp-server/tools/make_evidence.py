#!/usr/bin/env python3
"""
Collect reproducibility evidence for an independent audit.

    .venv/bin/python tools/make_evidence.py                 # after: python launch.py --check
    .venv/bin/python tools/make_evidence.py --with-model    # also load MiniLM + real-model tests
    .venv/Scripts/python tools\\make_evidence.py           # Windows

Writes evidence/<host>-<UTC time>/ and a ZIP of it containing:
  environment.json   OS, Python, pip freeze, release identity (RELEASE.json, SHA-256 of
                     every program and data file as found on this machine)
  verify.json        `python -m astro_rag_mcp verify [--with-model]` report
  pytest.xml         JUnit report of the full test suite (real-model tests when --with-model)
  pytest.txt         console output of the test run
  summary.json       pass/fail of each step
Attach any tools/llm_acceptance.py reports with --include.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--with-model", action="store_true")
    ap.add_argument("--include", nargs="*", default=[], help="extra files, e.g. llm_acceptance_*.json")
    a = ap.parse_args()

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = HERE / "evidence" / f"{socket.gethostname()}-{stamp}"
    out.mkdir(parents=True)
    env = {**os.environ, "PYTHONPATH": str(HERE)}
    if a.with_model:
        env["ASTRO_RAG_TEST_REAL_MODEL"] = "1"
    summary = {}

    files = {}
    for p in sorted(HERE.rglob("*")):
        rel = p.relative_to(HERE)
        if p.is_file() and not set(rel.parts) & {".venv", "evidence", "__pycache__", ".pytest_cache", "dist"}:
            files[rel.as_posix()] = sha256(p)
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout
    release = HERE / "RELEASE.json"
    (out / "environment.json").write_text(json.dumps({
        "collected_utc": stamp, "host": socket.gethostname(),
        "os": f"{platform.system()} {platform.release()} {platform.version()}",
        "machine": platform.machine(), "python": sys.version,
        "release": json.loads(release.read_text(encoding="utf-8")) if release.is_file() else None,
        "pip_freeze": freeze.splitlines(), "file_sha256": files,
    }, indent=2), encoding="utf-8")

    v = subprocess.run([sys.executable, "-m", "astro_rag_mcp", "verify", "--strict", "--log-level", "WARNING"]
                       + (["--with-model"] if a.with_model else []),
                       cwd=HERE, env=env, capture_output=True, text=True)
    (out / "verify.json").write_text(v.stdout, encoding="utf-8")
    (out / "verify.stderr.txt").write_text(v.stderr, encoding="utf-8")
    summary["verify_strict"] = "PASS" if v.returncode == 0 else "FAIL"

    t = subprocess.run([sys.executable, "-m", "pytest", "-q", "-rs", "tests",
                        f"--junitxml={out / 'pytest.xml'}"],
                       cwd=HERE, env=env, capture_output=True, text=True)
    (out / "pytest.txt").write_text(t.stdout + t.stderr, encoding="utf-8")
    summary["tests"] = "PASS" if t.returncode == 0 else "FAIL"
    summary["tests_line"] = (t.stdout.strip().splitlines() or [""])[-1]

    for f in a.include:
        shutil.copy2(f, out / Path(f).name)
    summary["included"] = [Path(f).name for f in a.include]
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    archive = shutil.make_archive(str(out), "zip", out.parent, out.name)
    print(json.dumps(summary, indent=2))
    print(f"evidence: {archive}  sha256={sha256(Path(archive))}")
    return 0 if summary["verify_strict"] == summary["tests"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
