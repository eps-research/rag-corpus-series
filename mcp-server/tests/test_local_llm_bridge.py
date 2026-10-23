"""clients/local_llm_chat.py and tools/llm_acceptance.py against scripted
OpenAI-compatible LLM servers.

The mocks behave like tool-calling models served by Ollama or LM Studio. They
verify the bridge's protocol handling and that the acceptance harness's pass
criteria discriminate (a model that skips tools, or quotes a withdrawn value,
fails). They say nothing about the quality of any real model; that is what
tools/llm_acceptance.py is for, run against a real one.
"""

import json
import re
import subprocess
import sys
import threading
import time

import uvicorn
from fastapi import FastAPI, Request

from .conftest import SERVER_ROOT, _free_port

PLAN = [   # (question pattern, first tool call)
    (r"NGC0024", ("get_object", {"corpus": "v7", "object_id": "NGC 24"})),
    (r"z_spec", ("filter_objects", {"corpus": "intz", "field": "z_spec", "min_val": 0.5, "max_val": 1.0})),
    (r"NGC3198", ("get_object", {"corpus": "v7", "object_id": "NGC3198"})),
    (r"z1 corpus", ("filter_objects", {"corpus": "z1", "field": "redshift", "omega_ready_only": True})),
    (r"C-HiZ_z1_111", ("get_object", {"corpus": "intz", "object_id": "C-HiZ_z1_111"})),
    (r"Distance and velocity", ("get_object", {"corpus": "v7", "object_id": "NGC 24"})),
]


def call(name, args, n=1):
    return {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": [{
        "id": f"call_{n}", "type": "function",
        "function": {"name": name, "arguments": json.dumps(args)}}]}}]}


def say(text):
    return {"choices": [{"message": {"role": "assistant", "content": text}}]}


def make_mock_llm(seen: list, behaviour: str):
    app = FastAPI()

    @app.post("/v1/chat/completions")
    async def completions(req: Request):
        body = await req.json()
        seen.append(body)
        user = [m for m in body["messages"] if m["role"] == "user"][-1]["content"]
        tools = [m for m in body["messages"] if m["role"] == "tool"]
        if behaviour == "no_tools":
            return say("NGC0024 is about 8 Mpc away.")
        if not tools:
            name, args = next(c for p, c in PLAN if re.search(p, user))
            return call(name, args)
        env = json.loads(tools[-1]["content"])
        if not env["success"] and env["error"]["code"] == "AMBIGUOUS_OBJECT_ID":
            pick = next(c for c in env["error"]["candidates"] if c.startswith("THINGS:"))
            return call("get_object", {"corpus": "v7", "object_id": pick}, n=2)
        if behaviour == "quotes_legacy" and "C-HiZ_z1_111" in user:
            om = env["data"]["record"]["omega"]
            return say(f"The omega value is {om['legacy_omega_value']} rad/Gyr.")
        rec = (env.get("data") or {}).get("record") or {}
        if "Distance and velocity" in user:
            return say(f"{env['data']['object_id']}: D={rec['distance_mpc']} Mpc, "
                       f"Vmean={rec['vrot_mean_kms']} km/s")
        return say(env["human_text"] + " " + " ".join(env.get("warnings", [])))

    return app


def serve(app):
    port = _free_port()
    srv = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=srv.run, daemon=True).start()
    while not srv.started:
        time.sleep(0.05)
    return srv, f"http://127.0.0.1:{port}/v1"


def test_bridge_round_trip(live_server):
    seen = []
    srv, url = serve(make_mock_llm(seen, "good"))
    try:
        out = subprocess.run(
            [sys.executable, str(SERVER_ROOT / "clients" / "local_llm_chat.py"),
             "--mcp", f"{live_server}/mcp", "--llm", url,
             "--model", "qwen3:8b", "-q", "Distance and velocity of NGC 24?"],
            capture_output=True, text=True, timeout=120)
    finally:
        srv.should_exit = True
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "SPARC:NGC0024: D=7.3 Mpc, Vmean=84.659 km/s"
    assert "get_object" in out.stderr and "7 tools" in out.stderr
    tool_msg = [m for m in seen[-1]["messages"] if m["role"] == "tool"][0]
    assert '"data": [' not in tool_msg["content"]          # curve table not sent to the model


def _acceptance(live_server, tmp_path, behaviour):
    srv, url = serve(make_mock_llm([], behaviour))
    report = tmp_path / f"{behaviour}.json"
    try:
        out = subprocess.run(
            [sys.executable, str(SERVER_ROOT / "tools" / "llm_acceptance.py"),
             "--mcp", f"{live_server}/mcp", "--llm", url, "--model", f"mock-{behaviour}",
             "--repeats", "1", "--out", str(report)],
            capture_output=True, text=True, timeout=300)
    finally:
        srv.should_exit = True
    return out, json.loads(report.read_text())


def test_acceptance_harness_passes_a_tool_using_model(live_server, tmp_path):
    out, rep = _acceptance(live_server, tmp_path, "good")
    assert out.returncode == 0, out.stdout + out.stderr
    assert rep["overall_pass_rate"] == 1.0
    assert rep["mcp_server"]["name"] == "eps-astro-rag-mcp"
    amb = next(c for c in rep["cases"] if c["id"] == "ambiguous_name")["runs"][0]
    assert [t["success"] for t in amb["tool_calls"]] == [False, True]   # retried with candidate


def test_acceptance_harness_fails_a_model_that_skips_tools(live_server, tmp_path):
    out, rep = _acceptance(live_server, tmp_path, "no_tools")
    assert out.returncode == 1 and rep["overall_pass_rate"] == 0.0


def test_acceptance_harness_catches_withdrawn_value(live_server, tmp_path):
    out, rep = _acceptance(live_server, tmp_path, "quotes_legacy")
    rates = {c["id"]: c["pass_rate"] for c in rep["cases"]}
    assert rates["withdrawn_omega"] == 0.0
    assert all(v == 1.0 for k, v in rates.items() if k != "withdrawn_omega")
