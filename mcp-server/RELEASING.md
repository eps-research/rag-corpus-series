# Releasing the MCP server (maintainer procedure)

The release builder refuses to package a stale semantic index, and the
Docker build refuses to build without passing `verify --with-model --strict`.
Run the steps in order on a machine that can reach pypi.org, the PyTorch CPU
index and huggingface.co (e.g. Node1). Paths are relative to the repository root.

## 1. Environment

```bash
cd mcp-server
python3 launch.py --check --locked --no-browser     # installs the locked stack, runs the tests
. .venv/bin/activate                                # Windows: .venv\Scripts\activate
```

## 2. Rebuild the stale v7 semantic index (HI v7.0 -> v7.3)

```bash
cd ..
python -c "from sentence_transformers import SentenceTransformer as S; S('sentence-transformers/all-MiniLM-L6-v2')"   # cache the model
python build_scripts/build_faiss_indexes.py --only v7 --out-dir /tmp/faiss_v7 --install
```

The builder regenerates the 438 v7 texts from the v7.3 records (values
substituted in the legacy grammar, caveats taken from the record, the
untraceable `omega ready` clause removed), refuses to embed if any text
disagrees with its record, embeds with explicit L2 normalisation, and writes
`faiss/index_manifest.json` with the corpus SHA-256, model revision and
artifact hashes. It prints the model revision; keep it.

Only v7 is rebuilt. The dwarf, gc, intz and z1 texts regenerate byte-identically
(`--text-only` proves this), so their vectors, and the manuscript's Z1
example, do not change.

## 3. Verify with the real model

```bash
cd mcp-server
python -m astro_rag_mcp verify --with-model --strict        # must print VERIFY: PASS
ASTRO_RAG_TEST_REAL_MODEL=1 python -m pytest -q -rs tests  # expect no skips
python tools/make_evidence.py --with-model                  # evidence/<host>-<time>.zip
```

`test_real_model_self_test_and_manuscript_z1_query` checks the manuscript's
Z1 top five; `test_real_model_is_normalised_natively` records whether MiniLM
outputs unit vectors without explicit normalisation.

## 4. Local-LLM acceptance (Ollama and LM Studio)

```bash
python launch.py --no-browser &                                     # the server
python tools/llm_acceptance.py --model qwen3:8b --repeats 3         # Ollama
python tools/llm_acceptance.py --llm http://localhost:1234/v1 --model <lmstudio-model-id> --repeats 3
```

Keep the `llm_acceptance_*.json` files; add them to the evidence with
`python tools/make_evidence.py --with-model --include llm_acceptance_*.json`.
LM Studio's own MCP integration (mcp.json, GUI) is checked by hand: connect to
`http://127.0.0.1:8080/mcp`, ask the NGC0024 question, record a screenshot.

## 5. Windows 11

On a Windows machine: extract the release ZIP, `python launch.py --check --locked`,
then `.venv\Scripts\python tools\make_evidence.py --with-model`.

## 6. Commit, release, deploy

```bash
git add faiss/v7_sparc.faiss faiss/v7_sparc_texts.json faiss/v7_sparc_ids.json faiss/index_manifest.json
git add -f faiss/*.json            # the root .gitignore ignores *.json
git commit -m "Rebuild v7 semantic index from HI v7.3"
cd mcp-server && python tools/build_release.py       # refuses if any index is stale
docker build -t astro-rag-mcp dist/astro-rag-mcp-server-2.4.0   # Space image; verifies with the model
```

Upload `dist/astro-rag-mcp-server-2.4.0.zip` to Zenodo (new version of the
2.3.0 record); add the version DOI to `CITATION.cff`, the README and the
manuscript; deploy the same directory to the Hugging Face Space.
