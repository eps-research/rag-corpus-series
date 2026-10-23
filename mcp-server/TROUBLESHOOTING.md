# Troubleshooting

Start with `python launch.py --check` (installs, verifies, runs the tests) and
<http://127.0.0.1:8080/health>. Most problems show up in one of them.

| Symptom | Cause and fix |
|---|---|
| `python` is not recognized (Windows) | Python is not on PATH. Re-run the python.org installer, choose *Modify*, tick *Add Python to environment variables*; or use `py launch.py`. |
| `ensurepip is not available` / venv fails (Ubuntu) | `sudo apt install python3-venv`, then delete `.venv/` and retry. |
| `ERROR: ... required file(s) missing` | The download is incomplete or was extracted without its folders. Re-download the ZIP and extract it whole (Windows: right-click → *Extract All*), then run `launch.py` inside the extracted folder. |
| `No corpus data found` | You copied `mcp-server/` out of the repository. Run it inside the full clone, use the release ZIP, or pass `--data-dir`. |
| `Data checksum verification failed` | A file under `data/` changed after release. Re-extract the ZIP; do not edit `data/`. |
| `ModuleNotFoundError: No module named 'mcp.server.fastmcp'` | An `mcp` 2.x package was installed by hand. Use the launcher, or `pip install "mcp>=1.26,<2"`. (Releases before 2.4.0 had this defect.) |
| `Port 8080 is already in use` | Another program (or an earlier server) uses the port: `python launch.py --port 8081`. |
| `semantic_search` → `SEMANTIC_UNAVAILABLE` "sentence-transformers is not installed" | You used `--no-semantic`. Run `python launch.py` without it. |
| `semantic_search` → `SEMANTIC_UNAVAILABLE` "Could not load embedding model" | The one-time model download from huggingface.co was blocked (proxy/firewall). Allow it once, or see INSTALL.md §D. The other six tools keep working. |
| `semantic_search` → `SEMANTIC_LOADING` | The model is still loading after start-up (up to ~1 min on first run). Retry. |
| `INDEX_STALE` | The semantic index for that corpus was built from an earlier corpus version (in the 2.4.0 pre-release: `v7`). Use `filter_objects`/`search_metadata`, or semantic search on the other corpora, until the index is rebuilt. |
| `data_quality: contains_model_rows` on a `dwarf` record | Dwarf v1.0 LITTLE THINGS curves contain unmarked Oh et al. (2015) model rows. Use the observed curve named in `data_quality.observed_curve` (a `v7` LITTLE_THINGS record). |
| `INDEX_INTEGRITY_FAILED` | A FAISS file does not match its corpus, or your embedding model differs from the one used to build the index. `/health` shows the reason per corpus. |
| PyTorch install fails on Windows | Install the *Microsoft Visual C++ Redistributable* (x64) and retry; or use `--no-semantic`. |
| `AMBIGUOUS_OBJECT_ID` for e.g. `NGC3198` | The galaxy is in two surveys with different data. Use the qualified ID from the error, e.g. `SPARC:NGC3198` or `THINGS:NGC3198`. |
| `UNKNOWN_FIELD` | Check spelling with `get_corpus_schema`; nested fields can be given as dotted paths (`redshift.z_spec`) or by unique name (`z_spec`). |
| Local model never calls tools | Use a tool-calling model of ≥7B parameters (Qwen 3/2.5 Instruct, Llama 3.1+), and mention "use the astro-rag tools" in the question. |
| LM Studio shows no tools | The server must be running before LM Studio connects (`python launch.py`), the URL must end in `/mcp`, and the tools must be enabled in the chat. |
| Claude Desktop shows a server error | Use absolute paths from `python launch.py --print-config`; on Windows double the backslashes in JSON. Claude Desktop's MCP log (Settings → Developer) shows the server's stderr. |
| Hosted server slow or "starting" | The free Hugging Face Space sleeps when idle; the first request wakes it (15–30 s). |
| MCP client gets HTTP 421/403 locally | DNS-rebinding protection rejects unknown `Host` headers on loopback binds. Connect via `127.0.0.1` or `localhost`, or start with `--host 0.0.0.0` behind your own proxy. |

Still stuck? Open an issue at <https://github.com/eps-research/rag-corpus-series/issues>
with the output of `python launch.py --check` and your OS and Python version.
