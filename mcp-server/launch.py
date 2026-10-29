#!/usr/bin/env python3
"""
launch.py — set up and run the EPS Research Astro-RAG MCP Server locally.

Works on Windows 11 and Ubuntu (Python 3.10–3.13). Runs entirely on this
machine: the corpora and FAISS indexes are read from local files; nothing is
proxied to the Hugging Face deployment.

    python launch.py                  # set up (first run) and serve on http://127.0.0.1:8080
    python launch.py --port 9000      # another port
    python launch.py --no-semantic    # skip PyTorch / embedding model (6 tools, no semantic_search)
    python launch.py --check          # set up, verify, run the tests, then exit
    python launch.py --print-config   # print MCP client configuration (Claude Desktop, LM Studio, ...)
    python launch.py --stdio          # serve MCP over stdio (used by client configs; see INSTALL.md)

Steps: 1 Python version · 2 file manifest · 3 virtual environment (.venv) ·
4 dependencies · 5 data verification · 6 serve.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENV = HERE / ".venv"
IS_WINDOWS = platform.system() == "Windows"
MIN_PY = (3, 10)
STAMP = VENV / ".astro_rag_installed"


def say(msg: str) -> None:
    print(msg, flush=True)


def fail(msg: str, hint: str = "") -> None:
    print(f"\nERROR: {msg}", file=sys.stderr)
    if hint:
        print(f"HINT:  {hint}", file=sys.stderr)
    print("See TROUBLESHOOTING.md.", file=sys.stderr)
    sys.exit(1)


def venv_python() -> Path:
    return VENV / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")


def run(cmd: list, **kw) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in cmd], **kw)


# 1 ─ Python ───────────────────────────────────────────────────────────────────
def check_python() -> None:
    say(f"[1/6] Python {platform.python_version()} ({sys.executable})")
    if sys.version_info[:2] < MIN_PY:
        fail(f"Python {MIN_PY[0]}.{MIN_PY[1]} or newer is required.",
             "Install Python 3.12 from https://www.python.org/downloads/ "
             "(Windows: tick 'Add python.exe to PATH').")
    if sys.version_info[:2] > (3, 13):
        say("      note: tested on 3.10–3.13; newer versions may lack binary wheels for faiss/torch.")


# 2 ─ Manifest ─────────────────────────────────────────────────────────────────
def check_manifest() -> None:
    say("[2/6] Checking files")
    manifest = HERE / "MANIFEST.txt"
    if not manifest.is_file():
        fail("MANIFEST.txt is missing; the download is incomplete.",
             "Download the release ZIP again, or clone the full repository.")
    missing = [ln.strip() for ln in manifest.read_text(encoding="utf-8").splitlines()
               if ln.strip() and not ln.startswith("#") and not (HERE / ln.strip()).is_file()]
    if missing:
        fail(f"{len(missing)} required file(s) missing: " + ", ".join(missing[:8]),
             "Re-extract the release ZIP with its folder structure intact, or re-clone the repository.")
    say("      all program files present")


# 3 ─ venv ─────────────────────────────────────────────────────────────────────
def ensure_venv() -> None:
    say(f"[3/6] Virtual environment: {VENV}")
    if venv_python().is_file():
        return
    r = run([sys.executable, "-m", "venv", VENV], capture_output=True, text=True)
    if r.returncode != 0:
        hint = ("On Ubuntu: sudo apt install python3-venv" if not IS_WINDOWS
                else "Reinstall Python from python.org with default options.")
        fail(f"Could not create the virtual environment:\n{r.stderr.strip()}", hint)


# 4 ─ Dependencies ─────────────────────────────────────────────────────────────
def pip(args: list) -> None:
    r = run([venv_python(), "-m", "pip", *args, "--disable-pip-version-check"])
    if r.returncode != 0:
        fail("pip install failed (see the messages above).",
             "Check your internet connection or proxy, then run launch.py again.")


def torch_pin() -> str:
    for ln in (HERE / "requirements-full.lock.txt").read_text(encoding="utf-8").splitlines():
        if ln.startswith("torch=="):
            return ln.split(";")[0].strip()
    return "torch"


def install(semantic: bool, dev: bool, locked: bool = False) -> None:
    want = {"core": True, "semantic": semantic, "dev": dev, "locked": locked}
    have = json.loads(STAMP.read_text(encoding="utf-8")) if STAMP.is_file() else {}
    req_hash = {n: (HERE / n).read_text(encoding="utf-8") for n in
                ("requirements.txt", "requirements-semantic.txt", "requirements-dev.txt",
                 "requirements.lock.txt", "requirements-full.lock.txt")}
    if have.get("reqs") == req_hash and all(have.get(k) for k, v in want.items() if v):
        say("[4/6] Dependencies already installed")
        return
    say("[4/6] Installing dependencies (first run: ~1 min core, several minutes with semantic search)")
    pip(["install", "--upgrade", "pip", "-q"])
    core_req = "requirements.lock.txt" if locked else "requirements.txt"
    if not (locked and semantic):
        pip(["install", "-r", HERE / core_req])
    if dev:
        pip(["install", "-r", HERE / "requirements-dev.txt"])
    if semantic:
        if platform.system() in ("Windows", "Linux"):
            # CPU-only PyTorch: ~200 MB instead of multi-GB CUDA wheels.
            r = run([venv_python(), "-m", "pip", "install", torch_pin() if locked else "torch",
                     "--index-url", "https://download.pytorch.org/whl/cpu",
                     "--disable-pip-version-check"])
            if r.returncode != 0:
                say("      CPU PyTorch index unavailable; installing PyTorch from PyPI instead")
        pip(["install", "-r", HERE / ("requirements-full.lock.txt" if locked else "requirements-semantic.txt")])
    STAMP.write_text(encoding="utf-8", data=json.dumps({**{k: v or have.get(k, False) for k, v in want.items()},
                                 "reqs": req_hash}))


# 5 ─ Verify ───────────────────────────────────────────────────────────────────
def verify(semantic: bool, with_model: bool) -> None:
    say("[5/6] Verifying corpora, checksums and FAISS indexes"
        + (" (and downloading/self-testing the embedding model)" if with_model else ""))
    # -X faulthandler: a native crash (e.g. in faiss or PyTorch) prints a Python stack.
    cmd = [venv_python(), "-X", "faulthandler", "-m", "astro_rag_mcp", "verify", "--log-level", "WARNING"]
    if not semantic:
        cmd.append("--no-semantic")
    if with_model:
        cmd.append("--with-model")
    r = run(cmd, cwd=HERE, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout[-3000:] + r.stderr[-3000:])
        sys.stderr.write(f"\nverify exited with code {r.returncode}"
                         + (" (killed by a signal: native crash)" if r.returncode < 0 else "") + "\n")
        fail("Data verification failed.", "Re-download the release; do not edit files under data/.")
    rep = json.loads(r.stdout)
    sem = rep["semantic_search"]
    say(f"      {rep['n_total']} objects in {len(rep['corpora'])} corpora; "
        f"checksums {'verified' if rep['checksums'].get('checked') else 'not applicable (repository layout)'}; "
        f"FAISS: " + (", ".join(f"{k} {v['state']}" for k, v in sem.get("indexes", {}).items())
                      or "not loaded (--no-semantic)"))
    for k, v in sem.get("indexes", {}).items():
        if v["state"] == "stale":
            say(f"      WARNING: semantic index '{k}' predates a corpus correction; semantic_search "
                f"on '{k}' is disabled until it is rebuilt (the other tools are unaffected).")
    if with_model:
        say(f"      embedding model: {sem.get('state')}"
            + (f" — {sem.get('model_error')}" if sem.get("model_error") else ""))


def port_free(host: str, port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1" if host in ("0.0.0.0", "::") else host, port)) != 0


def client_config() -> dict:
    py = str(venv_python())
    return {
        "stdio (Claude Desktop, LM Studio, other clients that start the server)": {
            "mcpServers": {"astro-rag": {
                "command": py,
                "args": ["-m", "astro_rag_mcp", "serve", "--transport", "stdio"],
                "cwd": str(HERE),
                "env": {"PYTHONPATH": str(HERE)},
            }}
        },
        "http (clients that connect to a running server, e.g. LM Studio)": {
            "mcpServers": {"astro-rag": {"url": "http://127.0.0.1:8080/mcp"}}
        },
        "hosted (no installation)": {
            "mcpServers": {"astro-rag": {"url": "https://dflynn5656-astro-rag-mcp.hf.space/mcp"}}
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--no-semantic", action="store_true")
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--check", action="store_true", help="set up, verify and run the test suite, then exit")
    ap.add_argument("--locked", action="store_true",
                    help="install the exact versions in the lock files (the release-tested set)")
    ap.add_argument("--print-config", action="store_true")
    ap.add_argument("--stdio", action="store_true", help="serve MCP over stdio (no setup output)")
    a = ap.parse_args()
    semantic = not a.no_semantic

    if a.stdio:   # launched by an MCP client: stdout belongs to the protocol
        if not venv_python().is_file():
            print("Run 'python launch.py' once to install before using --stdio.", file=sys.stderr)
            sys.exit(1)
        args = ["-m", "astro_rag_mcp", "serve", "--transport", "stdio"] + (["--no-semantic"] if not semantic else [])
        env = {**os.environ, "PYTHONPATH": str(HERE)}
        sys.exit(subprocess.call([str(venv_python()), *args], cwd=HERE, env=env))

    if a.print_config:   # no setup: just print paths for this folder
        if not venv_python().is_file():
            print("note: run 'python launch.py' once first; the .venv path below is created then.",
                  file=sys.stderr)
        print(json.dumps(client_config(), indent=2))
        return

    say(f"EPS Research Astro-RAG MCP Server — local setup ({platform.system()} {platform.release()})")
    check_python()
    check_manifest()
    ensure_venv()
    install(semantic, dev=a.check, locked=a.locked)
    verify(semantic, with_model=semantic and a.check)

    if a.check:
        say("[6/6] Running test suite")
        r = run([venv_python(), "-m", "pytest", "-q", "tests"], cwd=HERE)
        if r.returncode != 0:
            fail("Tests failed (see above).")
        say("\nCHECK PASSED")
        return

    if not port_free(a.host, a.port):
        fail(f"Port {a.port} is already in use.",
             f"Stop the other program, or run: python launch.py --port {a.port + 1}")

    shown = "127.0.0.1" if a.host in ("0.0.0.0", "::") else a.host
    base = f"http://{shown}:{a.port}"
    say(f"[6/6] Starting server — press Ctrl+C to stop\n"
        f"      Browser UI : {base}/\n      REST docs  : {base}/docs\n"
        f"      MCP        : {base}/mcp\n      Client configuration: python launch.py --print-config\n")
    if not a.no_browser:
        def _open():
            time.sleep(4)
            webbrowser.open(base + "/")
        import threading
        threading.Thread(target=_open, daemon=True).start()
    cmd = [venv_python(), "-m", "astro_rag_mcp", "serve", "--host", a.host, "--port", str(a.port)]
    if not semantic:
        cmd.append("--no-semantic")
    try:
        sys.exit(subprocess.call([str(c) for c in cmd], cwd=HERE, env={**os.environ, "PYTHONPATH": str(HERE)}))
    except KeyboardInterrupt:
        say("\nStopped.")


if __name__ == "__main__":
    main()
