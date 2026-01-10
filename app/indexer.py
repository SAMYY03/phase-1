from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def preprocess(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks: List[str] = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == n:
            break
        start = max(0, end - overlap)

    return chunks


def load_dataset(data_dir: str = "data") -> List[Dict[str, str]]:
    p = Path(data_dir)
    if not p.exists():
        raise FileNotFoundError(f"'{data_dir}' folder not found. Create it and add .txt files.")

    files = sorted([f for f in p.glob("*.txt") if f.is_file()])
    if not files:
        raise FileNotFoundError(f"No .txt files found in '{data_dir}'. Add doc1.txt, doc2.txt, ...")

    docs: List[Dict[str, str]] = []
    for f in files:
        raw = f.read_text(encoding="utf-8", errors="ignore")
        docs.append({"source": f.name, "text": preprocess(raw)})
    return docs


def build_faiss_index(
    data_dir: str = "data",
    model_name: str = DEFAULT_MODEL,
    chunk_size: int = 500,
    overlap: int = 50,
) -> Tuple[faiss.Index, Dict[str, Any]]:
    dataset = load_dataset(data_dir)

    chunks: List[Dict[str, str]] = []
    for doc in dataset:
        for ch in chunk_text(doc["text"], chunk_size=chunk_size, overlap=overlap):
            chunks.append({"source": doc["source"], "text": ch})

    model = SentenceTransformer(model_name)
    embeddings = model.encode([c["text"] for c in chunks], normalize_embeddings=True)

    vectors = np.array(embeddings, dtype=np.float32)
    dim = vectors.shape[1]

    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    meta: Dict[str, Any] = {
        "model_name": model_name,
        "dim": dim,
        "items": [{"id": i, "source": chunks[i]["source"], "text": chunks[i]["text"]} for i in range(len(chunks))],
    }
    return index, meta


def search_faiss(index: faiss.Index, meta: Dict[str, Any], query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    model = SentenceTransformer(meta["model_name"])
    q_vec = model.encode([query], normalize_embeddings=True)
    q = np.array(q_vec, dtype=np.float32)

    scores, ids = index.search(q, top_k)

    results: List[Dict[str, Any]] = []
    for score, idx in zip(scores[0].tolist(), ids[0].tolist()):
        if idx == -1:
            continue
        item = meta["items"][idx]
        results.append({"source": item["source"], "score": float(score), "text": item["text"]})
    return results
