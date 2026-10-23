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
Small models (<7B) often fail to call tools reliably.
Requires only the packages in requirements.txt (mcp, httpx).
"""

from __future__ import annotations

import argparse
import json
import sys

import anyio
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SYSTEM = (
    "You answer questions about astrophysical corpora using the provided tools. "
    "Always call a tool to obtain values; never guess numbers. Quote the object_id, "
    "corpus version and DOI from the tool result. If a tool returns an error with "
    "candidates or suggestions, retry with one of them."
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


def result_text(res) -> str:
    """Tool result as compact JSON text for the model's context."""
    env = getattr(res, "structuredContent", None)
    if env and set(env) == {"result"}:
        env = env["result"]
    if not env:
        text = "\n".join(getattr(c, "text", "") for c in res.content)
        try:
            env = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return text[:12000]
    # Keep the model's context small: drop the bulky rotation-curve table.
    data = env.get("data") if isinstance(env, dict) else None
    rec = data.get("record") if isinstance(data, dict) else None
    if isinstance(rec, dict) and ("data" in rec or "columns" in rec):
        rec = {k: v for k, v in rec.items() if k not in ("data", "columns")}
        env = {**env, "data": {**data, "record": rec,
                               "note": "rotation-curve table omitted here; call get_object over REST/MCP for it"}}
    return json.dumps(env)[:12000]


async def chat(args) -> None:
    async with streamablehttp_client(args.mcp) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            oa_tools = to_openai_tools(tools)
            print(f"Connected to {args.mcp}: {len(tools)} tools "
                  f"({', '.join(t.name for t in tools)})", file=sys.stderr)

            messages = [{"role": "system", "content": SYSTEM}]
            headers = {"Authorization": f"Bearer {args.api_key}"} if args.api_key else {}
            async with httpx.AsyncClient(base_url=args.llm.rstrip("/"), timeout=args.timeout,
                                         headers=headers) as llm:

                async def ask(question: str) -> str:
                    messages.append({"role": "user", "content": question})
                    for _ in range(args.max_steps):
                        resp = await llm.post("/chat/completions", json={
                            "model": args.model, "messages": messages,
                            "tools": oa_tools, "tool_choice": "auto", "temperature": 0,
                        })
                        if resp.status_code != 200:
                            raise RuntimeError(f"LLM server returned {resp.status_code}: {resp.text[:500]}")
                        msg = resp.json()["choices"][0]["message"]
                        calls = msg.get("tool_calls") or []
                        messages.append({k: v for k, v in msg.items() if k in ("role", "content", "tool_calls")}
                                        | {"content": msg.get("content") or ""})
                        if not calls:
                            return msg.get("content") or ""
                        for c in calls:
                            name = c["function"]["name"]
                            raw = c["function"].get("arguments") or "{}"
                            try:
                                fargs = json.loads(raw) if isinstance(raw, str) else raw
                            except json.JSONDecodeError:
                                fargs = {}
                            print(f"  -> {name}({json.dumps(fargs)})", file=sys.stderr)
                            try:
                                out = result_text(await session.call_tool(name, fargs))
                            except Exception as e:
                                out = json.dumps({"success": False, "error": str(e)})
                            messages.append({"role": "tool", "tool_call_id": c.get("id", name),
                                             "name": name, "content": out})
                    return "(stopped: too many tool steps)"

                if args.question:
                    print(await ask(args.question))
                    return
                print("Ask a question (Ctrl+C or empty line to quit).", file=sys.stderr)
                while True:
                    try:
                        q = input("\n> ").strip()
                    except (EOFError, KeyboardInterrupt):
                        break
                    if not q:
                        break
                    print(await ask(q))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mcp", default="http://127.0.0.1:8080/mcp", help="MCP endpoint URL")
    ap.add_argument("--llm", default="http://localhost:11434/v1",
                    help="OpenAI-compatible base URL (Ollama: :11434/v1, LM Studio: :1234/v1)")
    ap.add_argument("--model", required=True, help="model name as the LLM server knows it")
    ap.add_argument("--api-key", default=None, help="only if your LLM server requires one")
    ap.add_argument("-q", "--question", default=None, help="ask one question and exit")
    ap.add_argument("--max-steps", type=int, default=8)
    ap.add_argument("--timeout", type=float, default=300)
    anyio.run(chat, ap.parse_args())


if __name__ == "__main__":
    main()
