"""
Phase 1 RAG reused in Phase 2 (extracted from Phase 1 FastAPI).

This module provides programmatic functions that can be called by agents:
- index_docs()
- retrieve()
- answer()
- chat() (optional)
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import faiss
import requests
from sentence_transformers import SentenceTransformer

# If you want to keep chat history, you can later rewire these to Phase 2 DB.
# For now, we keep them optional to avoid import conflicts.
try:
    from app.db import ensure_session, save_message, get_history, save_retrieval_log
    from app.prompts import build_chat_prompt
    HISTORY_ENABLED = True
except Exception:
    HISTORY_ENABLED = False


# Embedding model (same as Phase 1)
_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Global index state
_faiss_index: Optional[faiss.IndexFlatIP] = None
_chunks: List[str] = []


def read_files(data_dir: str = "data") -> List[str]:
    """Read all .txt files from data folder."""
    texts: List[str] = []
    if not os.path.isdir(data_dir):
        return texts

    for f in os.listdir(data_dir):
        if f.endswith(".txt"):
            path = os.path.join(data_dir, f)
            with open(path, "r", encoding="utf-8") as file:
                texts.append(file.read())
    return texts


def chunk_text(text: str, size: int = 500) -> List[str]:
    """Split text into fixed-size chunks."""
    return [text[i : i + size] for i in range(0, len(text), size)]


def embed(texts: List[str]):
    """Create normalized embeddings for texts."""
    return _model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")


def ask_llm(prompt: str) -> str:
    """Call local Ollama model (DeepSeek) to generate an answer."""
    response = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={"model": "deepseek-r1:1.5b", "prompt": prompt, "stream": False},
        timeout=300,
    )
    response.raise_for_status()
    return response.json()["response"]


def index_docs(data_dir: str = "data") -> Dict[str, Any]:
    """Index all docs from data folder into FAISS (Phase 1 /index logic)."""
    global _faiss_index, _chunks

    docs = read_files(data_dir=data_dir)
    _chunks = []
    for d in docs:
        _chunks.extend(chunk_text(d))

    if not _chunks:
        _faiss_index = None
        return {"status": "no_docs", "chunks": 0}

    vectors = embed(_chunks)

    _faiss_index = faiss.IndexFlatIP(vectors.shape[1])
    _faiss_index.add(vectors)

    return {"status": "indexed", "chunks": len(_chunks)}


def retrieve(query: str, top_k: int = 2) -> Tuple[str, List[Dict[str, Any]], float]:
    """Retrieve relevant chunks with scores (Phase 1 retrieve_with_scores)."""
    if _faiss_index is None or not _chunks:
        return "", [], 0.0

    q_vec = embed([query])
    scores, ids = _faiss_index.search(q_vec, top_k)

    retrieved: List[Dict[str, Any]] = []
    context_parts: List[str] = []

    best_score = float(scores[0][0]) if len(scores[0]) > 0 else 0.0

    for rank, idx in enumerate(ids[0]):
        if idx == -1:
            continue
        text = _chunks[idx]
        score = float(scores[0][rank])

        retrieved.append({"rank": rank + 1, "score": score, "text": text})
        context_parts.append(text)

    context = "\n\n".join(context_parts)
    return context, retrieved, best_score


def answer(query: str, top_k: int = 2, strict: bool = True) -> Dict[str, Any]:
    """Answer a query using RAG (Phase 1 /ask logic)."""
    context, retrieved, best_score = retrieve(query, top_k=top_k)

    prompt = (
        "You are a strict QA assistant.\n"
        "Use ONLY the context below to answer.\n"
        "If the context is not enough, say: I don't know.\n\n"
        "Context:\n" + context + "\n\n"
        "Question: " + query + "\n"
        "Answer:"
    )

    llm_answer = ask_llm(prompt).strip()
    return {
        "query": query,
        "answer": llm_answer,
        "best_score": best_score,
        "results": retrieved,
    }


def chat(
    message: str,
    session_id: Optional[str] = None,
    top_k: int = 2,
    strict: bool = True,
) -> Dict[str, Any]:
    """Chat using history + RAG (Phase 1 /chat logic).

    Note: requires Phase 1 DB + prompts modules. If not available, raises.
    """
    if not HISTORY_ENABLED:
        raise RuntimeError("Chat history modules not wired in Phase 2 yet.")

    if not session_id:
        session_id = str(uuid.uuid4())

    ensure_session(session_id)
    user_msg_id = save_message(session_id, "user", message)
    history = get_history(session_id, limit=8)

    context, retrieved, best_score = retrieve(message, top_k=top_k)

    prompt = build_chat_prompt(history, context, message, strict=strict)
    llm_answer = ask_llm(prompt).strip()

    save_message(session_id, "assistant", llm_answer)
    save_retrieval_log(session_id, user_msg_id, top_k, best_score, retrieved)

    return {
        "session_id": session_id,
        "answer": llm_answer,
        "best_score": best_score,
        "retrieved": retrieved,
    }
