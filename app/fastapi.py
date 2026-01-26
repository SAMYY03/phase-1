import os
import uuid
import requests
from fastapi import FastAPI, Body
import faiss
from sentence_transformers import SentenceTransformer

from app.db import init_db, ensure_session, save_message, get_history, save_retrieval_log
from app.prompts import build_chat_prompt

app = FastAPI()

# ---------- Init DB ----------
init_db()

# ---------- Embedding model ----------
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ---------- Global memory ----------
faiss_index = None
chunks = []


# ---------- Read files ----------
def read_files():
    texts = []
    for f in os.listdir("data"):
        if f.endswith(".txt"):
            with open("data/" + f, "r", encoding="utf-8") as file:
                texts.append(file.read())
    return texts


# ---------- Chunk text ----------
def chunk_text(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]


# ---------- Embeddings ----------
def embed(texts):
    return model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")


# ---------- Ollama call ----------
def ask_llm(prompt):
    response = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={
            "model": "deepseek-r1:1.5b",
            "prompt": prompt,
            "stream": False
        },
        timeout=300
    )
    response.raise_for_status()
    return response.json()["response"]


# ---------- Retrieval pipeline ----------
def retrieve_with_scores(query, top_k=2):
    """
    Returns:
    - context (string)
    - retrieved (list of dicts: rank, score, text)
    - best_score (float)
    """
    if faiss_index is None or not chunks:
        return "", [], 0.0

    q_vec = embed([query])
    scores, ids = faiss_index.search(q_vec, top_k)

    retrieved = []
    context_parts = []

    best_score = float(scores[0][0]) if len(scores[0]) > 0 else 0.0

    for rank, idx in enumerate(ids[0]):
        if idx == -1:
            continue
        text = chunks[idx]
        score = float(scores[0][rank])

        retrieved.append({"rank": rank + 1, "score": score, "text": text})
        context_parts.append(text)

    context = "\n\n".join(context_parts)
    return context, retrieved, best_score


# =========================
# ENDPOINTS (PAGE 4)
# =========================

@app.post("/index")
def index_docs():
    global faiss_index, chunks

    docs = read_files()
    chunks = []
    for d in docs:
        chunks.extend(chunk_text(d))

    vectors = embed(chunks)

    faiss_index = faiss.IndexFlatIP(vectors.shape[1])
    faiss_index.add(vectors)

    return {"status": "indexed", "chunks": len(chunks)}


@app.post("/search")
def search(query: str = Body(...), top_k: int = 2):
    context, retrieved, best_score = retrieve_with_scores(query, top_k=top_k)
    return {
        "query": query,
        "top_k": top_k,
        "best_score": best_score,
        "results": retrieved
    }


@app.post("/ask")
def ask(query: str = Body(...), top_k: int = 2, strict: bool = True):
    context, retrieved, best_score = retrieve_with_scores(query, top_k=top_k)

    prompt = (
        "You are a strict QA assistant.\n"
        "Use ONLY the context below to answer.\n"
        "If the context is not enough, say: I don't know.\n\n"
        "Context:\n" + context + "\n\n"
        "Question: " + query + "\n"
        "Answer:"
    )

    answer = ask_llm(prompt)
    return {"query": query, "answer": answer.strip(), "best_score": best_score, "results": retrieved}


# =========================
# ENDPOINTS (PAGE 5)
# =========================

@app.post("/chat")
def chat(
    message: str = Body(..., embed=True),
    session_id: str = Body(None, embed=True),
    top_k: int = 2,
    strict: bool = True
):
    # 1) Create session if missing
    if not session_id:
        session_id = str(uuid.uuid4())
    ensure_session(session_id)

    # 2) Save user message
    user_msg_id = save_message(session_id, "user", message)

    # 3) Load recent history (includes the message we just saved)
    history = get_history(session_id, limit=8)

    # 4) Retrieve context from FAISS
    context, retrieved, best_score = retrieve_with_scores(message, top_k=top_k)

    # 5) Build prompt using history + context (prompt engineering)
    prompt = build_chat_prompt(history, context, message, strict=strict)

    # 6) Generate answer (Ollama)
    answer = ask_llm(prompt).strip()

    # 7) Save assistant answer
    save_message(session_id, "assistant", answer)

    # 8) Save retrieval log
    save_retrieval_log(session_id, user_msg_id, top_k, best_score, retrieved)

    return {
        "session_id": session_id,
        "answer": answer,
        "best_score": best_score,
        "retrieved": retrieved
    }


@app.get("/history/{session_id}")
def history(session_id: str):
    messages = get_history(session_id, limit=200)
    return {"session_id": session_id, "messages": messages}
