# Installing and using the Astro-RAG MCP Server

There are two ways to use the server. Neither needs an API key.

| | What you need | Endpoints |
|---|---|---|
| **A. Hosted** (Hugging Face) | nothing to install | `https://dflynn5656-astro-rag-mcp.hf.space` |
| **B. Local** (your machine) | Python 3.10–3.13 | `http://127.0.0.1:8080` |

Both run the same code and serve the same data; each exposes

* `/` — browser query interface
* `/docs` — REST API documentation (Swagger), with a "Try it out" button per endpoint
* `/api/<tool>` — REST endpoints
* `/mcp` — the MCP endpoint (Streamable HTTP, JSON-RPC 2.0; there is no separate SSE endpoint)
* `/health` — status, data versions, checksums and semantic-search state

The local server also speaks MCP over **stdio**, which is how desktop clients
such as Claude Desktop launch servers themselves.

---

## A. Hosted server (no installation)

The free Hugging Face tier puts the Space to sleep when idle; the first request
after a pause can take 15–30 s (or show a "starting" page in the browser).

**Browser:** open `https://dflynn5656-astro-rag-mcp.hf.space`, choose a corpus and
an operation, press *Run*.

**REST (any language):**

```bash
curl "https://dflynn5656-astro-rag-mcp.hf.space/api/get_object?corpus=v7&object_id=NGC0024"
curl "https://dflynn5656-astro-rag-mcp.hf.space/api/filter_objects?corpus=v7&field=distance_mpc&min=1&max=10"
curl "https://dflynn5656-astro-rag-mcp.hf.space/api/semantic_search?corpus=z1&query=confirmed%20rotator&top_k=5"
```

```python
import requests
r = requests.get("https://dflynn5656-astro-rag-mcp.hf.space/api/get_object",
                 params={"corpus": "v7", "object_id": "NGC0024"}).json()
print(r["data"]["record"]["vrot_mean_kms"], r["data"]["record"]["distance_mpc"])   # 84.659 7.3
```

**MCP:** give your client the URL `https://dflynn5656-astro-rag-mcp.hf.space/mcp`.
For example, in LM Studio's `mcp.json` or any client that accepts remote servers:

```json
{ "mcpServers": { "astro-rag": { "url": "https://dflynn5656-astro-rag-mcp.hf.space/mcp" } } }
```

In Claude (web or desktop), add it under *Settings → Connectors → Add custom connector*.

---

## B. Local installation

### 1. Get the files

Either download and **extract** the release ZIP
(`astro-rag-mcp-server-2.4.0.zip`, Zenodo), or clone the repository:

```bash
git clone https://github.com/eps-research/rag-corpus-series.git
cd rag-corpus-series/mcp-server
```

The ZIP is self-contained (program, corpora, FAISS indexes, checksums). In a
clone, the server reads the corpora from `../examples/` and the indexes from
`../faiss/`, so keep the repository intact. Do not copy `mcp-server/` out of
the clone on its own — use the ZIP for that.

### 2. Install Python (once)

* **Windows 11:** install Python 3.12 from <https://www.python.org/downloads/>.
  In the installer tick **"Add python.exe to PATH"**. Then open *PowerShell*.
* **Ubuntu 22.04 / 24.04:** `sudo apt install python3 python3-venv python3-pip`

Check with `python --version` (Windows) or `python3 --version` (Ubuntu).

### 3. Run the launcher

From the `mcp-server` folder (the one containing `launch.py`):

```powershell
# Windows (PowerShell)
cd C:\path\to\astro-rag-mcp-server-2.4.0
python launch.py
```

```bash
# Ubuntu
cd ~/astro-rag-mcp-server-2.4.0
python3 launch.py
```

The launcher

1. checks the Python version and that all program files are present;
2. creates a private virtual environment in `.venv/` (nothing is installed system-wide);
3. installs the dependencies — about 1 minute for the core, a few more minutes
   the first time for the semantic-search model stack (PyTorch CPU, ~200 MB);
4. verifies the corpora (2,064 objects), their SHA-256 checksums and the FAISS indexes;
5. starts the server on `http://127.0.0.1:8080` and opens the browser.

Press **Ctrl+C** to stop. The next start skips installation and takes a few seconds.
On first use of `semantic_search` the embedding model (~90 MB) is downloaded
from huggingface.co once and cached.

Options:

| Command | Purpose |
|---|---|
| `python launch.py --port 9000` | use another port |
| `python launch.py --no-semantic` | skip PyTorch; six tools, no `semantic_search` |
| `python launch.py --no-browser` | do not open a browser (servers, SSH) |
| `python launch.py --host 0.0.0.0` | allow other machines on your network to connect |
| `python launch.py --check` | install, verify, run the test suite, exit |
| `python launch.py --locked` | install the exact dependency versions the release was tested with (`requirements*.lock.txt`) |
| `python launch.py --print-config` | print MCP client configuration with your paths |

**Manual alternative** (no launcher):

```bash
python3 -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-semantic.txt
python -m astro_rag_mcp verify
python -m astro_rag_mcp serve     # --transport stdio for stdio
```

### 4. Check that it works

Open <http://127.0.0.1:8080/health> — it should report `"status": "ok"` and
`"n_total": 2064`. Then <http://127.0.0.1:8080/api/get_object?corpus=v7&object_id=NGC0024>
should return `vrot_mean_kms` 84.659 and `distance_mpc` 7.3.

---

## C. Connecting an LLM

The server is an ordinary MCP server; any MCP-capable client can use it. Run
`python launch.py --print-config` to get configuration blocks with your
absolute paths filled in.

### Claude Desktop (stdio)

Settings → Developer → Edit Config, merge (paths from `--print-config`):

```json
{
  "mcpServers": {
    "astro-rag": {
      "command": "C:\\path\\to\\mcp-server\\.venv\\Scripts\\python.exe",
      "args": ["-m", "astro_rag_mcp", "serve", "--transport", "stdio"],
      "cwd": "C:\\path\\to\\mcp-server",
      "env": { "PYTHONPATH": "C:\\path\\to\\mcp-server" }
    }
  }
}
```

Restart Claude Desktop; the seven tools appear under the tools icon.

### LM Studio (local models, e.g. Qwen)

1. Start the server: `python launch.py`.
2. In LM Studio open the **Program** tab → **Install → Edit mcp.json** and add
   `"astro-rag": { "url": "http://127.0.0.1:8080/mcp" }` inside `mcpServers`
   (see `clients/lmstudio_mcp.example.json`).
3. Load a model that supports tool calling (Qwen 3 / Qwen 2.5 Instruct, 7B or larger
   recommended), open a chat, enable the astro-rag tools, and ask, e.g.
   *"Using the astro-rag tools, what are the distance and mean rotation velocity of NGC0024?"*

### Ollama (and other OpenAI-compatible local servers)

Ollama has no built-in MCP client, so use the included bridge, which offers the
MCP tools to the model through Ollama's OpenAI-compatible API and executes the
model's tool calls:

```bash
ollama pull qwen3:8b                 # any tool-calling model
python launch.py                     # terminal 1: the MCP server
# terminal 2, from mcp-server/:
.venv/bin/python clients/local_llm_chat.py --model qwen3:8b            # Ubuntu
.venv\Scripts\python clients\local_llm_chat.py --model qwen3:8b        # Windows
```

The same bridge works with LM Studio (`--llm http://localhost:1234/v1`),
llama.cpp's server and vLLM. Add `-q "your question"` for a single question.
Tool calling with models below ~7B parameters is often unreliable.

To record whether a given model actually works with the server, run the
acceptance harness. It asks five fixed questions (including one about a
withdrawn ω value that the model must report as withdrawn), checks the tool
calls and answers automatically, and writes a JSON evidence file:

```bash
.venv/bin/python tools/llm_acceptance.py --model qwen3:8b                              # Ollama
.venv/bin/python tools/llm_acceptance.py --llm http://localhost:1234/v1 --model qwen3-8b  # LM Studio
```

### Python, without an LLM

```python
import anyio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client("http://127.0.0.1:8080/mcp") as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print([t.name for t in (await s.list_tools()).tools])
            res = await s.call_tool("filter_objects",
                                    {"corpus": "intz", "field": "z_spec", "min_val": 0.5, "max_val": 1.0})
            print(res.content[0].text[:300])

anyio.run(main)
```

---

## D. Network use and offline operation

What needs the network, and when:

| Step | Network | Source |
|---|---|---|
| Installing dependencies (first run) | yes | pypi.org; download.pytorch.org (CPU PyTorch) |
| Corpora and FAISS indexes | **no** | bundled in the release / repository |
| Embedding model (first `semantic_search` only) | yes, once | huggingface.co, ~90 MB, cached in `~/.cache/huggingface` |
| Running the server and all seven tools afterwards | **no** | — |

To run fully offline (e.g. an air-gapped analysis node): on a connected
machine run `python launch.py --check`, which installs everything and
downloads the model; copy the `mcp-server` folder (including `.venv` if the
OS and Python version match, otherwise reinstall from a local wheel cache) and
`~/.cache/huggingface` (Windows: `%USERPROFILE%\.cache\huggingface`) to the
offline machine, and set `HF_HUB_OFFLINE=1`. Without the model, the server
still runs and the other six tools work; `semantic_search` returns
`SEMANTIC_UNAVAILABLE`.

At every start the server re-embeds one stored record per corpus and refuses
semantic search for that corpus if the result differs from the stored vector,
so a different model or model revision cannot silently change rankings. When
`faiss/index_manifest.json` records the model revision used to build the
indexes, the server loads exactly that revision.

## E. Semantic index status

`/health` (and `list_corpora`) report a state for each corpus's semantic index:
`ok`, `stale` (the index was built from an earlier version of the corpus;
semantic search on that corpus is refused, other tools are unaffected) or
`failed`. In this 2.4.0 pre-release the **v7** index is `stale`: it was built
from HI corpus v7.0, while the server serves v7.3. It is rebuilt with
`build_scripts/build_faiss_indexes.py` (see `RELEASING.md`).

See `TROUBLESHOOTING.md` for common problems.
