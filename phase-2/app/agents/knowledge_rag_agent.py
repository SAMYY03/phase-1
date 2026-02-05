"""Knowledge RAG agent (Phase 1 RAG reused)."""

from __future__ import annotations

from app.rag.phase1_rag import index_docs, answer


class KnowledgeRagAgent:
    """Agent that answers company knowledge questions using Phase 1 RAG."""

    def __init__(self) -> None:
        # Build index once at startup
        index_docs()

    def answer(self, query: str) -> str:
        result = answer(query=query, top_k=2, strict=True)
        return result["answer"]
