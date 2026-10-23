#!/usr/bin/env python3
"""
Chat with the Astro-RAG corpora through a *local* LLM.

Connects any model served behind an OpenAI-compatible chat API that supports
tool calling (Ollama, LM Studio, llama.cpp server, vLLM) to the Astro-RAG MCP
server. The script lists the MCP tools, offers them to the model as functions,
executes the model's tool calls against the MCP server, and feeds the results
back until the model answers.

Examples (start the MCP server first: python launch.py):

  # Ollama (ollama pull qwen3:8b)
  python clients/local_llm_chat.py --llm http://localhost:11434/v1 --model qwen3:8b

  # LM Studio (load a model, start the local server on port 1234)
  python clients/local_llm_chat.py --llm http://localhost:1234/v1 --model qwen3-8b

  # one-shot question, against the hosted server
  python clients/local_llm_chat.py --model qwen3:8b \
      --mcp https://dflynn5656-astro-rag-mcp.hf.space/mcp \
      -q "What is the distance and mean rotation velocity of NGC0024?"

Use a model that supports tool calling (Qwen 2.5/3, Llama 3.1+, Mistral, ...).
Small models (<7B) often fail to call tools reliably. For a recorded,
pass/fail acceptance run see tools/llm_acceptance.py.
Requires only the packages in requirements.txt (mcp, httpx).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any, Optional

import anyio
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SYSTEM = (
    "You answer questions about astrophysical corpora using the provided tools. "
    "Always call a tool to obtain values; never guess numbers. Quote the object_id, "
    "corpus version and DOI from the tool result. If a tool returns an error with "
    "candidates or suggestions, retry with one of them. Report any warnings or "
    "correction notices that the tool returns."
)


def to_openai_tools(tools) -> list[dict]:
    return [{
        "type": "function",
        "function": {
            "name": t.name,
            "description": t.description or "",
            "parameters": t.inputSchema or {"type": "object", "properties": {}},
        },
    } for t in tools]


def envelope(res) -> Any:
    """Decode an MCP tool result into the server's JSON envelope (or text)."""
    env = getattr(res, "structuredContent", None)
    if env and set(env) == {"result"}:
        env = env["result"]
    if env:
        return env
    text = "\n".join(getattr(c, "text", "") for c in res.content)
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return text


def result_text(env: Any) -> str:
    """Tool result as compact JSON text for the model's context."""
    if not isinstance(env, dict):
        return str(env)[:12000]
    # Keep the model's context small: drop the bulky rotation-curve table.
    data = env.get("data")
    rec = data.get("record") if isinstance(data, dict) else None
    if isinstance(rec, dict) and ("data" in rec or "columns" in rec or "model_iso_oh2015" in rec):
        rec = {k: v for k, v in rec.items() if k not in ("data", "columns", "model_iso_oh2015")}
        env = {**env, "data": {**data, "record": rec,
                               "note": "rotation-curve table omitted here; call get_object over REST/MCP for it"}}
    return json.dumps(env)[:12000]


class Bridge:
    """One MCP session + one OpenAI-compatible LLM endpoint."""

    def __init__(self, session: ClientSession, llm: httpx.AsyncClient, model: str,
                 tools: list, max_steps: int = 8, temperature: float = 0.0, verbose: bool = True):
        self.session, self.llm, self.model = session, llm, model
        self.oa_tools = to_openai_tools(tools)
        self.max_steps, self.temperature, self.verbose = max_steps, temperature, verbose

    async def ask(self, question: str, history: Optional[list] = None) -> dict:
        """Answer one question. Returns answer, tool-call trace and timings."""
        messages = history if history is not None else [{"role": "system", "content": SYSTEM}]
        messages.append({"role": "user", "content": question})
        trace: list[dict] = []
        t0 = time.time()
        for _ in range(self.max_steps):
            resp = await self.llm.post("/chat/completions", json={
                "model": self.model, "messages": messages,
                "tools": self.oa_tools, "tool_choice": "auto", "temperature": self.temperature,
            })
            if resp.status_code != 200:
                raise RuntimeError(f"LLM server returned {resp.status_code}: {resp.text[:500]}")
            msg = resp.json()["choices"][0]["message"]
            calls = msg.get("tool_calls") or []
            messages.append({"role": "assistant", "content": msg.get("content") or "",
                             **({"tool_calls": calls} if calls else {})})
            if not calls:
                return {"answer": msg.get("content") or "", "tool_calls": trace,
                        "seconds": round(time.time() - t0, 2), "stopped": None}
            for c in calls:
                name = c["function"]["name"]
                raw = c["function"].get("arguments") or "{}"
                try:
                    fargs = json.loads(raw) if isinstance(raw, str) else raw
                except json.JSONDecodeError:
                    fargs = {}
                if self.verbose:
                    print(f"  -> {name}({json.dumps(fargs)})", file=sys.stderr)
                try:
                    env = envelope(await self.session.call_tool(name, fargs))
                except Exception as e:
                    env = {"success": False, "error": {"code": "CLIENT_ERROR", "message": str(e)}}
                ok = isinstance(env, dict) and env.get("success") is True
                trace.append({"tool": name, "arguments": fargs, "success": ok,
                              "error": None if ok or not isinstance(env, dict) else env.get("error")})
                messages.append({"role": "tool", "tool_call_id": c.get("id", name),
                                 "name": name, "content": result_text(env)})
        return {"answer": "", "tool_calls": trace, "seconds": round(time.time() - t0, 2),
                "stopped": "too many tool steps"}


async def open_bridge(args, body):
    """Run ``body(bridge, tools)`` with a connected MCP session and LLM client."""
    async with streamablehttp_client(args.mcp) as (r, w, _):
        async with ClientSession(r, w) as session:
            init = await session.initialize()
            tools = (await session.list_tools()).tools
            print(f"Connected to {args.mcp} ({init.serverInfo.name} {init.serverInfo.version}): "
                  f"{len(tools)} tools ({', '.join(t.name for t in tools)})", file=sys.stderr)
            headers = {"Authorization": f"Bearer {args.api_key}"} if args.api_key else {}
            async with httpx.AsyncClient(base_url=args.llm.rstrip("/"), timeout=args.timeout,
                                         headers=headers) as llm:
                bridge = Bridge(session, llm, args.model, tools, args.max_steps)
                return await body(bridge, init)


async def chat(args) -> None:
    async def body(bridge: Bridge, _init):
        if args.question:
            print((await bridge.ask(args.question))["answer"])
            return
        history = [{"role": "system", "content": SYSTEM}]
        print("Ask a question (Ctrl+C or empty line to quit).", file=sys.stderr)
        while True:
            try:
                q = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not q:
                break
            print((await bridge.ask(q, history))["answer"])

    await open_bridge(args, body)


def add_common(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--mcp", default="http://127.0.0.1:8080/mcp", help="MCP endpoint URL")
    ap.add_argument("--llm", default="http://localhost:11434/v1",
                    help="OpenAI-compatible base URL (Ollama: :11434/v1, LM Studio: :1234/v1)")
    ap.add_argument("--model", required=True, help="model name as the LLM server knows it")
    ap.add_argument("--api-key", default=None, help="only if your LLM server requires one")
    ap.add_argument("--max-steps", type=int, default=8)
    ap.add_argument("--timeout", type=float, default=300)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common(ap)
    ap.add_argument("-q", "--question", default=None, help="ask one question and exit")
    anyio.run(chat, ap.parse_args())


if __name__ == "__main__":
    main()
