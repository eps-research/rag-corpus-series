import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp_client import close_session
from fastapi.responses import FileResponse
import os
from routers import corpora, objects, search

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_session()

app = FastAPI(
    title="Astro-RAG REST API",
    description="REST wrapper around the EPS Research Astro-RAG MCP server.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(corpora.router)
app.include_router(objects.router)
app.include_router(search.router)

@app.get("/", tags=["UI"], include_in_schema=False)
async def root():
    ui = os.path.join(os.path.dirname(__file__), "index.html")
    return FileResponse(ui)

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
