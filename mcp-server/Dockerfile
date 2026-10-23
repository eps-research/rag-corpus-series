# EPS Research Astro-RAG MCP Server — container image (Hugging Face Space)
#
# Build from an extracted release directory, which contains data/ with SHA256SUMS:
#   python tools/build_release.py            # -> dist/astro-rag-mcp-server-<version>/
#   docker build -t astro-rag-mcp dist/astro-rag-mcp-server-<version>
#   docker run -p 7860:7860 astro-rag-mcp
#
# The image bundles the corpora, the FAISS indexes and the embedding model, and
# the build fails unless `verify --with-model --strict` passes (checksums, FAISS
# integrity, index text consistent with the corpora, re-embedding self-test). The running container needs no network access.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/hf-cache TRANSFORMERS_OFFLINE=0

WORKDIR /app
COPY requirements-full.lock.txt ./
# Exact, locked versions; CPU-only PyTorch at the locked version.
RUN pip install "$(grep -E '^torch==' requirements-full.lock.txt | cut -d';' -f1)" \
        --index-url https://download.pytorch.org/whl/cpu \
 && pip install -r requirements-full.lock.txt

COPY . .
# Download the model into the image, then verify everything with it.
RUN python -m astro_rag_mcp verify --with-model --strict --log-level WARNING > /app/verify-report.json \
 && chmod -R a+rX /opt/hf-cache /app

# Hugging Face Spaces run as uid 1000 and expect port 7860.
RUN useradd -m -u 1000 user
USER user
ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
EXPOSE 7860
CMD ["python", "-m", "astro_rag_mcp", "serve", "--host", "0.0.0.0", "--port", "7860"]
