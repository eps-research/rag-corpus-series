#!/usr/bin/env python3
"""
launch.py — EPS Research Astro-RAG MCP Server / REST Wrapper Launcher
Version  : 2.2.0
Supports : Windows 11 Pro, Ubuntu 20.04+
Usage    : python launch.py [--port 8080] [--host 0.0.0.0] [--skip-ping]
                             [--no-browser] [--no-gui] [--skip-manifest]

Install  : Place launch.py and launcher_config.json at the repo/zip root.
           Everything resolves relative to this file — works from any path.

Repo     : https://github.com/eps-research/astro-rag-mcp-server
Zenodo   : https://doi.org/10.5281/zenodo.20985225
"""

import argparse
import json
import os
import platform
import re
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path

# ── Bootstrap: tkinter ────────────────────────────────────────────────────────
_TK_AVAILABLE = False
try:
    import tkinter as tk
    from tkinter import messagebox
    _root_check = tk.Tk()
    _root_check.withdraw()
    _root_check.destroy()
    _TK_AVAILABLE = True
except Exception:
    pass

# ── Paths (all relative to this file) ────────────────────────────────────────
HERE         = Path(__file__).parent.resolve()
CONFIG_FILE  = HERE / "launcher_config.json"
APP_DIR      = HERE / "rest-wrapper"          # production repo layout
VENV_DIR     = APP_DIR / "venv"
REQUIREMENTS = APP_DIR / "requirements.txt"

IS_WINDOWS = platform.system() == "Windows"

# ── Startup constants ─────────────────────────────────────────────────────────
REQUIRED_PYTHON  = (3, 10)
STARTUP_TIMEOUT  = 25
KILL_WAIT        = 6

# ── Default config (overridden by launcher_config.json) ──────────────────────
DEFAULT_CONFIG = {
    "hf_space_url" : "https://dflynn5656-astro-rag-mcp.hf.space/mcp",
    "corpus_keys"  : ["v7", "dwarf", "gc", "intz", "z1"],
    "default_port" : 8080,
    "default_host" : "0.0.0.0",
    "app_module"   : "app:app",
    "version"      : "2.2.0",
}

# ── Production manifest (paths relative to HERE) ─────────────────────────────
MANIFEST = [
    "launcher_config.json",
    "README.md",
    "CORPUS_KEYS.md",
    "server.py",
    "rest-wrapper/app.py",
    "rest-wrapper/config.py",
    "rest-wrapper/dependencies.py",
    "rest-wrapper/mcp_client.py",
    "rest-wrapper/requirements.txt",
    "rest-wrapper/index.html",
    "rest-wrapper/models/request_models.py",
    "rest-wrapper/models/response_models.py",
    "rest-wrapper/routers/corpora.py",
    "rest-wrapper/routers/objects.py",
    "rest-wrapper/routers/search.py",
]

# ── ANSI colour (terminal) ────────────────────────────────────────────────────
def _supports_colour():
    if IS_WINDOWS:
        return (os.environ.get("WT_SESSION") or
                os.environ.get("TERM_PROGRAM") or
                os.environ.get("CI"))
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

USE_COLOUR = _supports_colour()

def _c(code, text):
    return f"\033[{code}m{text}\033[0m" if USE_COLOUR else text

def t_ok(msg):   print(_c("32",   f"  ✓  {msg}"))
def t_info(msg): print(_c("36",   f"  →  {msg}"))
def t_warn(msg): print(_c("33",   f"  ⚠  {msg}"))
def t_fail(msg): print(_c("31",   f"  ✗  {msg}"))
def t_head(msg): print(_c("1",    f"\n{msg}"))
def t_bold(msg): print(_c("1;36", msg))

# ── GUI helpers ───────────────────────────────────────────────────────────────

class _Toast:
    def __init__(self, title, message, ms=2500):
        if not _TK_AVAILABLE:
            return
        threading.Thread(target=self._show,
                         args=(title, message, ms), daemon=True).start()

    def _show(self, title, message, ms):
        try:
            root = tk.Tk()
            root.title(title)
            root.resizable(False, False)
            root.attributes("-topmost", True)
            w, h = 400, 110
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
            tk.Label(root, text=message, wraplength=360,
                     justify="left", padx=16, pady=18,
                     font=("Segoe UI", 10) if IS_WINDOWS else ("Sans", 10)
                     ).pack(fill="both", expand=True)
            root.after(ms, root.destroy)
            root.mainloop()
        except Exception:
            pass


def gui_info(title, message, ms=2500, use_gui=True):
    t_info(f"{title}: {message}")
    if use_gui and _TK_AVAILABLE:
        _Toast(title, message, ms)


def gui_ok(title, message, ms=2200, use_gui=True):
    t_ok(f"{title}: {message}")
    if use_gui and _TK_AVAILABLE:
        _Toast(f"✓ {title}", message, ms)


def gui_warn(title, message, use_gui=True):
    t_warn(f"{title}: {message}")
    if use_gui and _TK_AVAILABLE:
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            result = messagebox.askokcancel(f"⚠ {title}", message, parent=root)
            root.destroy()
            return result
        except Exception:
            pass
    return True


def gui_error(title, message, use_gui=True):
    t_fail(f"{title}: {message}")
    if use_gui and _TK_AVAILABLE:
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            messagebox.showerror(f"✗ {title}", message, parent=root)
            root.destroy()
        except Exception:
            pass
    sys.exit(1)


def gui_running_panel(swagger_url, base_url, health_url,
                      corpus_keys, hf_url, version,
                      proc, use_gui=True):
    print()
    print(_c("1;32", "=" * 62))
    print(_c("1;32", f"  ✓  Astro-RAG REST Wrapper v{version} is RUNNING"))
    print(_c("1;32", "=" * 62))
    print()
    print(_c("1",    "  USER INTERFACE  (open this for daily use)"))
    t_ok(f"  {base_url}")
    print()
    print(_c("1",    "  DEVELOPER / API DOCS"))
    t_ok(f"  {swagger_url}")
    print()
    t_info(f"Corpus keys : {' | '.join(corpus_keys)}")
    t_info(f"MCP upstream: {hf_url}")
    print()
    print(_c("33", "  Close the status window or press Ctrl+C to stop."))
    print()

    if not (use_gui and _TK_AVAILABLE):
        try:
            proc.wait()
        except KeyboardInterrupt:
            _shutdown(proc)
        return

    try:
        root = tk.Tk()
        root.title(f"Astro-RAG REST Wrapper v{version} — Running")
        root.resizable(False, False)
        root.attributes("-topmost", True)

        W = 500
        root.update_idletasks()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"{W}x{370}+{(sw-W)//2}+{(sh-370)//2}")

        font_h  = ("Segoe UI", 11, "bold") if IS_WINDOWS else ("Sans", 11, "bold")
        font_b  = ("Segoe UI", 10)          if IS_WINDOWS else ("Sans", 10)
        font_sm = ("Segoe UI", 9)           if IS_WINDOWS else ("Sans", 9)

        # Header
        hdr = tk.Frame(root, bg="#1a7f3c", pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"✓  Server is Running  —  v{version}",
                 bg="#1a7f3c", fg="white", font=font_h).pack()

        body = tk.Frame(root, padx=20, pady=10)
        body.pack(fill="both", expand=True)

        def url_row(label, value):
            f = tk.Frame(body)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=label, font=font_sm, fg="#555",
                     width=16, anchor="w").pack(side="left")
            e = tk.Entry(f, font=font_b, relief="flat", bg="#f4f4f4")
            e.insert(0, value)
            e.config(state="readonly")
            e.pack(side="left", fill="x", expand=True, ipady=3)

        # User UI section
        tk.Label(body, text="USER INTERFACE  —  open this for daily use",
                 font=("Segoe UI", 9, "bold") if IS_WINDOWS else ("Sans", 9, "bold"),
                 fg="#1a7f3c", anchor="w").pack(fill="x", pady=(4, 2))
        url_row("  Open here →", base_url)
        tk.Label(body,
                 text="Clean query interface — select corpus, run queries, download results.",
                 font=font_sm, fg="#666", anchor="w").pack(fill="x", padx=2, pady=(0, 8))

        # Developer section
        tk.Label(body, text="DEVELOPER / API DOCS",
                 font=("Segoe UI", 9, "bold") if IS_WINDOWS else ("Sans", 9, "bold"),
                 fg="#1a5f9f", anchor="w").pack(fill="x", pady=(0, 2))
        url_row("  API docs →", swagger_url)
        tk.Label(body,
                 text="Raw endpoint explorer — for development and integration work.",
                 font=font_sm, fg="#666", anchor="w").pack(fill="x", padx=2, pady=(0, 8))

        tk.Frame(body, height=1, bg="#ddd").pack(fill="x", pady=4)

        tk.Label(body,
                 text="Corpus keys:  " + "  |  ".join(corpus_keys),
                 font=font_sm, fg="#444", anchor="w").pack(fill="x")
        tk.Label(body,
                 text=f"MCP upstream: {hf_url}",
                 font=font_sm, fg="#444", anchor="w",
                 wraplength=W-40, justify="left").pack(fill="x", pady=(2, 0))

        tk.Frame(body, height=1, bg="#ddd").pack(fill="x", pady=8)

        def _stop():
            _shutdown(proc)
            root.destroy()

        tk.Button(root, text="⏹  Stop Server", command=_stop,
                  bg="#c0392b", fg="white", font=font_h,
                  relief="flat", padx=20, pady=8,
                  cursor="hand2").pack(pady=(0, 16))

        root.protocol("WM_DELETE_WINDOW", _stop)

        def _watch():
            if proc.poll() is not None:
                root.destroy()
            else:
                root.after(1000, _watch)
        root.after(1000, _watch)

        root.mainloop()

    except KeyboardInterrupt:
        _shutdown(proc)
    except Exception as e:
        t_warn(f"GUI panel failed ({e}) — use Ctrl+C to stop.")
        try:
            proc.wait()
        except KeyboardInterrupt:
            _shutdown(proc)


def _shutdown(proc):
    t_info("Stopping server …")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    t_info("Server stopped.")

# ── Config ────────────────────────────────────────────────────────────────────

def load_config(use_gui):
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                cfg.update(json.load(f))
            gui_ok("Config", f"Loaded from {CONFIG_FILE.name}", use_gui=use_gui)
        except Exception as e:
            gui_warn("Config Error",
                     f"launcher_config.json could not be read:\n{e}\n\nUsing defaults.",
                     use_gui=use_gui)
    else:
        gui_info("Config", "launcher_config.json not found — using built-in defaults.",
                 ms=2500, use_gui=use_gui)
    return cfg

# ── Step 1 — Manifest ─────────────────────────────────────────────────────────

def check_manifest(use_gui, skip=False):
    t_head("[ 1/7 ] Package file manifest")
    if skip:
        gui_info("Manifest", "Skipped (--skip-manifest) — dev/test mode.",
                 ms=1800, use_gui=use_gui)
        return
    missing = [f for f in MANIFEST if not (HERE / f).exists()]
    if missing:
        gui_error("Missing Files",
                  "The following required files are missing:\n\n"
                  + "\n".join(f"  • {f}" for f in missing)
                  + "\n\nRe-clone the repo or re-extract the zip and retry.",
                  use_gui=use_gui)
    gui_ok("Manifest", f"All {len(MANIFEST)} required files present.",
           use_gui=use_gui)

# ── Step 2 — Python version ───────────────────────────────────────────────────

def check_python(use_gui):
    t_head("[ 2/7 ] Python version")
    major, minor = sys.version_info[:2]
    req_maj, req_min = REQUIRED_PYTHON
    if (major, minor) < (req_maj, req_min):
        gui_error("Python Too Old",
                  f"Python {major}.{minor} detected — {req_maj}.{req_min}+ required.\n\n"
                  "Download from https://python.org",
                  use_gui=use_gui)
    gui_ok("Python", f"{major}.{minor}.{sys.version_info.micro}", use_gui=use_gui)

# ── Step 3 — venv ─────────────────────────────────────────────────────────────

def _venv_python():
    return VENV_DIR / ("Scripts/python.exe" if IS_WINDOWS else "bin/python3")

def _venv_pip():
    return VENV_DIR / ("Scripts/pip.exe" if IS_WINDOWS else "bin/pip3")

def ensure_venv(use_gui):
    t_head("[ 3/7 ] Virtual environment")
    if VENV_DIR.exists() and _venv_python().exists():
        gui_ok("venv", f"Found at {VENV_DIR}", use_gui=use_gui)
        return
    gui_info("venv", "Creating virtual environment …", ms=8000, use_gui=use_gui)
    result = subprocess.run(
        [sys.executable, "-m", "venv", str(VENV_DIR)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        gui_error("venv Failed",
                  f"Could not create virtual environment:\n\n{result.stderr}",
                  use_gui=use_gui)
    gui_ok("venv", "Created.", use_gui=use_gui)

# ── Step 4 — Dependencies ─────────────────────────────────────────────────────

def install_dependencies(use_gui):
    t_head("[ 4/7 ] Dependencies")
    pip         = _venv_pip()
    venv_python = _venv_python()

    if not pip.exists():
        gui_error("venv Broken",
                  f"pip not found — delete {VENV_DIR} and retry.",
                  use_gui=use_gui)

    check = subprocess.run(
        [str(venv_python), "-c", "import uvicorn, fastapi, httpx"],
        capture_output=True
    )
    if check.returncode == 0:
        gui_ok("Dependencies", "Core packages already installed.", use_gui=use_gui)
    else:
        gui_info("Dependencies",
                 "Installing packages — first run takes ~60s …",
                 ms=90000, use_gui=use_gui)
        result = subprocess.run(
            [str(pip), "install", "-r", str(REQUIREMENTS), "--quiet"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            gui_error("Install Failed",
                      f"pip install failed:\n\n{result.stderr[:600]}",
                      use_gui=use_gui)
        gui_ok("Dependencies", "All packages installed.", use_gui=use_gui)

    check2 = subprocess.run(
        [str(venv_python), "-c", "import fastmcp"],
        capture_output=True
    )
    if check2.returncode != 0:
        gui_info("fastmcp", "Installing fastmcp …", ms=20000, use_gui=use_gui)
        subprocess.run([str(pip), "install", "fastmcp", "--quiet"])
    gui_ok("fastmcp", "OK", use_gui=use_gui)

# ── Step 5 — Kill prior instance ──────────────────────────────────────────────

def _port_is_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) != 0

def _pids_on_port_windows(port):
    try:
        out = subprocess.check_output(["netstat", "-ano"],
                                      text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return []
    pids = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 5 and f":{port}" in parts[1]:
            try:
                pid = int(parts[-1])
                if pid > 0:
                    pids.add(pid)
            except ValueError:
                pass
    return list(pids)

def _pids_on_port_linux(port):
    pids = set()
    try:
        out = subprocess.check_output(
            ["ss", "-tlnp", f"sport = :{port}"],
            text=True, stderr=subprocess.DEVNULL)
        for m in re.finditer(r"pid=(\d+)", out):
            pids.add(int(m.group(1)))
    except Exception:
        pass
    if not pids:
        try:
            out = subprocess.check_output(
                ["lsof", "-ti", f":{port}"],
                text=True, stderr=subprocess.DEVNULL)
            for line in out.splitlines():
                try:
                    pids.add(int(line.strip()))
                except ValueError:
                    pass
        except Exception:
            pass
    return list(pids)

def _kill_pids(pids):
    if IS_WINDOWS:
        for pid in pids:
            subprocess.run(["taskkill", "/PID", str(pid), "/F"],
                           capture_output=True)
            t_info(f"Killed PID {pid}")
    else:
        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
                t_info(f"SIGTERM → PID {pid}")
            except ProcessLookupError:
                pass
            except PermissionError:
                t_warn(f"Permission denied — PID {pid} (try sudo)")
        time.sleep(2)
        for pid in pids:
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
                t_info(f"SIGKILL → PID {pid}")
            except ProcessLookupError:
                pass

def kill_prior_instance(port, use_gui):
    t_head("[ 5/7 ] Prior instance check")
    if _port_is_free(port):
        gui_ok("Port", f"{port} is free.", use_gui=use_gui)
        return

    pids = _pids_on_port_windows(port) if IS_WINDOWS else _pids_on_port_linux(port)
    pid_str = ", ".join(str(p) for p in pids) if pids else "unknown"

    confirmed = gui_warn(
        "Prior Instance Found",
        f"Port {port} is in use (PID {pid_str}).\n\n"
        "Click OK to stop it and start fresh.\n"
        "Click Cancel to abort.",
        use_gui=use_gui
    )
    if not confirmed:
        t_info("Aborted by user.")
        sys.exit(0)

    if not pids:
        gui_error("Cannot Stop",
                  f"Port {port} is in use but the process could not be identified.\n"
                  "Close it manually and retry.",
                  use_gui=use_gui)

    _kill_pids(pids)

    deadline = time.time() + KILL_WAIT
    while time.time() < deadline:
        if _port_is_free(port):
            gui_ok("Port", f"{port} is now free.", use_gui=use_gui)
            return
        time.sleep(0.5)

    gui_error("Port Stuck",
              f"Port {port} still in use after {KILL_WAIT}s.\n"
              "Close the occupying process manually and retry.",
              use_gui=use_gui)

# ── Step 6 — HF Space ping ────────────────────────────────────────────────────

def ping_hf_space(hf_url, skip, use_gui):
    t_head("[ 6/7 ] HuggingFace Space reachability")
    if skip:
        gui_info("HF Space", "Skipped (--skip-ping).", use_gui=use_gui)
        return
    gui_info("HF Space", f"Pinging {hf_url} …", ms=12000, use_gui=use_gui)
    try:
        req = urllib.request.Request(hf_url, method="GET")
        req.add_header("User-Agent", "EPS-RAG-Launcher/2.2.0")
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
        if 200 <= status < 400:
            gui_ok("HF Space", f"Reachable (HTTP {status}).", use_gui=use_gui)
        else:
            gui_warn("HF Space",
                     f"HF Space returned HTTP {status} — may be sleeping.\n"
                     "First RAG queries will be slow. Server will still start.",
                     use_gui=use_gui)
    except urllib.error.URLError as e:
        gui_warn("HF Space Unreachable",
                 f"Could not reach:\n{hf_url}\n\nReason: {e.reason}\n\n"
                 "The REST wrapper will start — MCP calls will fail "
                 "until the Space wakes up.",
                 use_gui=use_gui)
    except Exception as e:
        gui_warn("HF Ping Error", f"Unexpected: {e}", use_gui=use_gui)

# ── Step 7 — Launch ───────────────────────────────────────────────────────────

def _poll_until_ready(port, timeout):
    urls = [f"http://localhost:{port}/health",
            f"http://localhost:{port}/docs"]
    deadline = time.time() + timeout
    while time.time() < deadline:
        for url in urls:
            try:
                with urllib.request.urlopen(url, timeout=2) as r:
                    if r.status < 500:
                        return True
            except Exception:
                pass
        time.sleep(1)
    return False

def _spawn_detached(cmd, cwd):
    if IS_WINDOWS:
        return subprocess.Popen(
            ["cmd", "/k"] + cmd,
            cwd=cwd,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
    # Ubuntu: try common terminals in order
    for term, args in [
        ("gnome-terminal", ["gnome-terminal", "--"] + cmd),
        ("xterm",          ["xterm", "-e"] + cmd),
        ("konsole",        ["konsole", "-e"] + cmd),
        ("xfce4-terminal", ["xfce4-terminal", "-e", " ".join(cmd)]),
    ]:
        if subprocess.run(["which", term],
                          capture_output=True).returncode == 0:
            return subprocess.Popen(args, cwd=cwd)
    # Headless fallback (Node1 / SSH)
    t_warn("No GUI terminal found — running uvicorn in background (headless).")
    return subprocess.Popen(
        cmd, cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def launch_server(cfg, host, port, no_browser, use_gui):
    t_head("[ 7/7 ] Starting REST wrapper")

    venv_python = _venv_python()
    app_module  = cfg.get("app_module", "app:app")
    hf_url      = cfg.get("hf_space_url", DEFAULT_CONFIG["hf_space_url"])
    corpus_keys = cfg.get("corpus_keys",  DEFAULT_CONFIG["corpus_keys"])
    version     = cfg.get("version",      DEFAULT_CONFIG["version"])

    swagger_url = f"http://localhost:{port}/docs"
    base_url    = f"http://localhost:{port}"
    health_url  = f"http://localhost:{port}/health"

    cmd = [
        str(venv_python), "-m", "uvicorn",
        app_module,
        "--host", host,
        "--port", str(port),
        "--reload",
    ]

    gui_info("Launching", "Starting uvicorn in a new window …",
             ms=3000, use_gui=use_gui)
    proc = _spawn_detached(cmd, cwd=str(APP_DIR))

    gui_info("Health Check",
             f"Waiting for server on port {port} …",
             ms=STARTUP_TIMEOUT * 1000, use_gui=use_gui)
    ready = _poll_until_ready(port, STARTUP_TIMEOUT)

    if not ready:
        proc.terminate()
        gui_error("Startup Failed",
                  f"Server did not respond within {STARTUP_TIMEOUT}s.\n"
                  "Check the uvicorn window for errors.",
                  use_gui=use_gui)

    if not no_browser:
        try:
            import webbrowser
            webbrowser.open(base_url)
        except Exception:
            pass

    gui_running_panel(
        swagger_url=swagger_url,
        base_url=base_url,
        health_url=health_url,
        corpus_keys=corpus_keys,
        hf_url=hf_url,
        version=version,
        proc=proc,
        use_gui=use_gui,
    )

# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="EPS Research Astro-RAG REST Wrapper — cross-platform launcher v2.2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch.py                       # standard start
  python launch.py --port 9000           # custom port
  python launch.py --skip-ping           # skip HF Space reachability check
  python launch.py --no-browser          # don't auto-open browser
  python launch.py --no-gui              # headless / SSH / Node1
  python launch.py --skip-manifest       # dev/test only — bypass file check
  python launch.py --host 127.0.0.1      # localhost only

Repo   : https://github.com/eps-research/astro-rag-mcp-server
Zenodo : https://doi.org/10.5281/zenodo.20985225
        """
    )
    p.add_argument("--port",          type=int, default=None)
    p.add_argument("--host",          type=str, default=None)
    p.add_argument("--skip-ping",     action="store_true",
                   help="Skip HuggingFace Space reachability check")
    p.add_argument("--no-browser",    action="store_true",
                   help="Do not auto-open browser")
    p.add_argument("--no-gui",        action="store_true",
                   help="Disable all popups — headless/SSH/Node1 mode")
    p.add_argument("--skip-manifest", action="store_true",
                   help="Skip file manifest check (dev/test only)")
    return p.parse_args()

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args    = parse_args()
    use_gui = _TK_AVAILABLE and not args.no_gui

    print()
    t_bold("EPS Research Astro-RAG — Launch Sequence")
    t_bold(f"Platform : {platform.system()} {platform.release()}")
    t_bold(f"GUI mode : {'enabled' if use_gui else 'disabled (terminal only)'}")

    cfg  = load_config(use_gui)
    port = args.port or cfg.get("default_port", 8080)
    host = args.host or cfg.get("default_host", "0.0.0.0")

    check_manifest(use_gui, skip=args.skip_manifest)
    check_python(use_gui)
    ensure_venv(use_gui)
    install_dependencies(use_gui)
    kill_prior_instance(port, use_gui)
    ping_hf_space(cfg.get("hf_space_url", DEFAULT_CONFIG["hf_space_url"]),
                  args.skip_ping, use_gui)
    launch_server(cfg, host, port, args.no_browser, use_gui)

if __name__ == "__main__":
    main()
