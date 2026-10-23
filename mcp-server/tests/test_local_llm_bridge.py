"""clients/local_llm_chat.py against a scripted OpenAI-compatible LLM server.

The mock behaves like a tool-calling model (e.g. Qwen served by Ollama or LM
Studio): it first asks for get_object, then answers using the tool result.
This verifies the bridge's protocol handling end to end; it does not test the
quality of any particular model.
"""

import json
import subprocess
import sys
import threading
import time

import uvicorn
from fastapi import FastAPI, Request

from .conftest import SERVER_ROOT, _free_port


def make_mock_llm(seen: list):
    app = FastAPI()

    @app.post("/v1/chat/completions")
    async def completions(req: Request):
        body = await req.json()
        seen.append(body)
        tool_msgs = [m for m in body["messages"] if m["role"] == "tool"]
        if not tool_msgs:
            assert {t["function"]["name"] for t in body["tools"]} >= {"get_object", "semantic_search"}
            return {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": [{
                "id": "call_1", "type": "function",
                "function": {"name": "get_object",
                             "arguments": json.dumps({"corpus": "v7", "object_id": "NGC 24"})}}]}}]}
        env = json.loads(tool_msgs[-1]["content"])
        rec = env["data"]["record"]
        return {"choices": [{"message": {"role": "assistant", "content":
                f"{env['data']['object_id']}: D={rec['distance_mpc']} Mpc, "
                f"Vmean={rec['vrot_mean_kms']} km/s"}}]}

    return app


def test_bridge_round_trip(live_server):
    seen = []
    port = _free_port()
    srv = uvicorn.Server(uvicorn.Config(make_mock_llm(seen), host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=srv.run, daemon=True).start()
    while not srv.started:
        time.sleep(0.05)
    try:
        out = subprocess.run(
            [sys.executable, str(SERVER_ROOT / "clients" / "local_llm_chat.py"),
             "--mcp", f"{live_server}/mcp", "--llm", f"http://127.0.0.1:{port}/v1",
             "--model", "qwen3:8b", "-q", "Distance and velocity of NGC 24?"],
            capture_output=True, text=True, timeout=120,
        )
    finally:
        srv.should_exit = True
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "SPARC:NGC0024: D=7.3 Mpc, Vmean=84.659 km/s"
    assert "get_object" in out.stderr and "7 tools" in out.stderr
    # the bulky rotation-curve table is not pushed into the model's context
    tool_msg = [m for m in seen[-1]["messages"] if m["role"] == "tool"][0]
    assert '"data": [' not in tool_msg["content"]
