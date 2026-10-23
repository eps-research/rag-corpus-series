"""Command line entry point.

    python -m astro_rag_mcp serve                     # HTTP: /mcp, /api, /docs, / on 127.0.0.1:8080
    python -m astro_rag_mcp serve --transport stdio   # for desktop MCP clients that launch the server
    python -m astro_rag_mcp verify                    # integrity report; non-zero exit on failure
    python -m astro_rag_mcp version

In stdio mode nothing is written to stdout except MCP protocol messages; logs go to stderr.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

from . import __version__


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--data-dir", default=None,
                   help="Directory with corpora/ and faiss/ (default: auto-detect)")
    p.add_argument("--no-semantic", action="store_true",
                   help="Disable semantic_search (no FAISS or embedding model loaded)")
    p.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="astro_rag_mcp",
                                 description=f"EPS Research Astro-RAG MCP Server {__version__}")
    sub = ap.add_subparsers(dest="cmd")

    s = sub.add_parser("serve", help="Run the server")
    _common(s)
    s.add_argument("--transport", choices=["http", "stdio"], default="http")
    s.add_argument("--host", default="127.0.0.1",
                   help="Bind address (default 127.0.0.1; use 0.0.0.0 to expose on the network)")
    s.add_argument("--port", type=int, default=8080)

    v = sub.add_parser("verify", help="Check corpora, checksums and FAISS integrity")
    _common(v)
    v.add_argument("--with-model", action="store_true",
                   help="Also load the embedding model and run the re-embedding self-test")

    sub.add_parser("version", help="Print the version")

    args = ap.parse_args(argv)
    if args.cmd in (None, "version"):
        print(__version__)
        return 0

    logging.basicConfig(level=args.log_level, stream=sys.stderr,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    from .server import build_app, build_mcp, build_service

    try:
        service = build_service(args.data_dir, semantic=not args.no_semantic)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if args.cmd == "verify":
        if args.with_model and service.semantic is not None:
            service.semantic.start_model_load(background=False)
        report = service.health()
        print(json.dumps(report, indent=2))
        sem = report["semantic_search"]
        idx_ok = sem.get("state") == "disabled" or all(
            i["state"] == "ok" for i in sem.get("indexes", {}).values())
        model_ok = (not args.with_model) or sem.get("state") == "ready"
        ok = report["n_total"] == 2064 and idx_ok and model_ok
        print("VERIFY: PASS" if ok else "VERIFY: FAIL", file=sys.stderr)
        return 0 if ok else 1

    if args.transport == "stdio":
        if service.semantic is not None:
            service.semantic.start_model_load(background=True)
        build_mcp(service).run(transport="stdio")
        return 0

    import uvicorn
    app = build_app(service, host=args.host, port=args.port)
    shown = "127.0.0.1" if args.host in ("0.0.0.0", "::") else args.host
    print(f"\nAstro-RAG MCP Server {__version__}\n"
          f"  Browser UI : http://{shown}:{args.port}/\n"
          f"  REST docs  : http://{shown}:{args.port}/docs\n"
          f"  MCP        : http://{shown}:{args.port}/mcp   (Streamable HTTP)\n"
          f"  Health     : http://{shown}:{args.port}/health\n", file=sys.stderr)
    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level.lower())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
