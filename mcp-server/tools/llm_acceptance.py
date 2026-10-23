#!/usr/bin/env python3
"""
Recorded acceptance test: a real local LLM using the Astro-RAG MCP server.

Runs a fixed set of questions through a tool-calling model (Ollama, LM
Studio, llama.cpp, vLLM — any OpenAI-compatible endpoint), records every tool
call and answer, applies machine-checked pass criteria, and writes a JSON
evidence report with the model, server version and environment.

    python launch.py                                   # terminal 1
    # terminal 2 (from mcp-server/):
    .venv/bin/python tools/llm_acceptance.py --model qwen3:8b                         # Ollama
    .venv/bin/python tools/llm_acceptance.py --llm http://localhost:1234/v1 --model qwen3-8b   # LM Studio API

Each case passes only if the model called the expected tool successfully AND
its answer contains the expected values (and none of the forbidden ones).
Case 'withdrawn_omega' checks correction propagation: the model must report
the IntZ omega as withdrawn rather than quote the legacy value.

Run each case several times (--repeats) to report a pass rate; LLM tool use is
not deterministic even at temperature 0 on some servers.
"""

from __future__ import annotations

import argparse
import datetime
import json
import platform
import re
import sys
from pathlib import Path

import anyio

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "clients"))
from local_llm_chat import SYSTEM, Bridge, add_common, open_bridge  # noqa: E402

CASES = [
    {
        "id": "ngc0024",
        "question": "Using the astro-rag tools, what are the distance and the mean rotation "
                    "velocity of the galaxy NGC0024 in the v7 corpus?",
        "tool": "get_object",
        "must_contain": [r"7\.3\b", r"84\.6[56]"],
        "must_not_contain": [],
    },
    {
        "id": "intz_redshift_count",
        "question": "Using the astro-rag tools, how many galaxies in the intz corpus have a "
                    "spectroscopic redshift z_spec between 0.5 and 1.0?",
        "tool": "filter_objects",
        "must_contain": [r"\b822\b"],
        "must_not_contain": [],
    },
    {
        "id": "ambiguous_name",
        "question": "Using the astro-rag tools, what is the distance of NGC3198 according to "
                    "the THINGS survey record in the v7 corpus?",
        "tool": "get_object",
        "must_contain": [r"13\.8\b"],
        "must_not_contain": [],
    },
    {
        "id": "z1_omega_ready",
        "question": "Using the astro-rag tools, how many galaxies in the z1 corpus have a "
                    "currently valid omega value?",
        "tool": "filter_objects",
        "must_contain": [r"\b8\b|\beight\b"],
        "must_not_contain": [],
    },
    {
        "id": "withdrawn_omega",
        "question": "Using the astro-rag tools, what is the omega value of the intz galaxy "
                    "C-HiZ_z1_111?",
        "tool": "get_object",
        "must_contain": [r"withdraw"],
        "must_not_contain": [r"-5\.87"],
    },
]


def judge(case: dict, result: dict) -> dict:
    answer = result["answer"] or ""
    called = [c for c in result["tool_calls"] if c["tool"] == case["tool"] and c["success"]]
    missing = [p for p in case["must_contain"] if not re.search(p, answer, re.I)]
    forbidden = [p for p in case["must_not_contain"] if re.search(p, answer, re.I)]
    ok = bool(called) and not missing and not forbidden
    return {"passed": ok, "expected_tool_called": bool(called),
            "missing_patterns": missing, "forbidden_patterns_found": forbidden}


async def run(args) -> int:
    cases = [c for c in CASES if not args.cases or c["id"] in args.cases]
    report = {
        "harness": "tools/llm_acceptance.py",
        "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "llm_endpoint": args.llm, "model": args.model, "mcp_endpoint": args.mcp,
        "platform": f"{platform.system()} {platform.release()} / Python {platform.python_version()}",
        "repeats": args.repeats, "cases": [],
    }

    async def body(bridge: Bridge, init):
        report["mcp_server"] = {"name": init.serverInfo.name, "version": init.serverInfo.version}
        for case in cases:
            runs = []
            for k in range(args.repeats):
                try:
                    res = await bridge.ask(case["question"], [{"role": "system", "content": SYSTEM}])
                except Exception as e:
                    res = {"answer": "", "tool_calls": [], "seconds": None, "stopped": f"error: {e}"}
                runs.append({**res, **judge(case, res)})
                print(f"[{case['id']} {k + 1}/{args.repeats}] "
                      f"{'PASS' if runs[-1]['passed'] else 'FAIL'}", file=sys.stderr)
            report["cases"].append({**case, "runs": runs,
                                    "pass_rate": sum(r["passed"] for r in runs) / len(runs)})

    await open_bridge(args, body)
    total = [r["passed"] for c in report["cases"] for r in c["runs"]]
    report["overall_pass_rate"] = sum(total) / len(total) if total else 0.0
    report["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    out = Path(args.out or f"llm_acceptance_{re.sub(r'[^A-Za-z0-9.]+', '_', args.model)}.json")
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n{args.model}: overall pass rate {report['overall_pass_rate']:.0%} "
          f"({sum(total)}/{len(total)}); evidence written to {out}")
    for c in report["cases"]:
        print(f"  {c['id']:22s} {c['pass_rate']:.0%}")
    return 0 if report["overall_pass_rate"] == 1.0 else 1


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common(ap)
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--cases", nargs="*", default=None, help="subset of case ids")
    ap.add_argument("--out", default=None, help="evidence JSON path")
    raise SystemExit(anyio.run(run, ap.parse_args()))


if __name__ == "__main__":
    main()
