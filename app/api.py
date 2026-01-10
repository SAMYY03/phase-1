"""
api.py
------
FastAPI service for Page 5 (as required by the document).

Endpoints:
- POST /index  -> preprocess + embed + index documents
- POST /search -> embed query + return relevant chunks
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.indexer import build_faiss_index, search_faiss
from app.store import index_exists, load_index, save_index

# IMPORTANT: uvicorn expects a variable named `app`
app = FastAPI(title="Page 5 - Indexing & Search API", version="1.0")


class IndexResponse(BaseModel):
    status: str
    num_chunks: int
    model_name: str
    dim: int


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query text")
    top_k: int = Field(3, ge=1, le=10, description="Number of results to return")


class SearchMatch(BaseModel):
    source: str
    score: float
    text: str


class SearchResponse(BaseModel):
    query: str
    top_k: int
    matches: list[SearchMatch]


@app.post("/index", response_model=IndexResponse)
def index_documents() -> IndexResponse:
    """Build a FAISS index from all .txt files in ./data and save it to ./storage."""
    index, meta = build_faiss_index(data_dir="data")
    save_index(index, meta)

    return IndexResponse(
        status="indexed",
        num_chunks=len(meta["items"]),
        model_name=meta["model_name"],
        dim=meta["dim"],
    )


@app.post("/search", response_model=SearchResponse)
def search_documents(req: SearchRequest) -> SearchResponse:
    """Search the FAISS index and return top_k matching chunks."""
    if not index_exists():
        raise RuntimeError("No index found. Call POST /index first.")

    index, meta = load_index()
    matches = search_faiss(index, meta, req.query, top_k=req.top_k)

    return SearchResponse(query=req.query, top_k=req.top_k, matches=matches)
