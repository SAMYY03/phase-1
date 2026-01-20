import os
import requests
from fastapi import FastAPI, Body
import faiss
from sentence_transformers import SentenceTransformer

# Create API
app = FastAPI()

# Load embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


faiss_index = None   # search engine
chunks = []          # text pieces


# Read files \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

def read_files():
    texts = []
    for f in os.listdir("data"):
        if f.endswith(".txt"):
            with open("data/" + f, "r", encoding="utf-8") as file:
                texts.append(file.read())
    return texts


# chunk

def chunk_text(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]


# Embedding\\\\\\\\\\\\\\\\\\\\\\\\\\\\

def embed(texts):
    return model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")



# Ollama

def ask_llm(prompt):
    response = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={
            "model": "deepseek-r1:1.5b",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]


# Retrieval\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

def retrieve(query, top_k=2):
    """
    Retrieval:
      Convert query into vector
     Search FAISS index
     Return matching text chunks
    """
    q_vec = embed([query])                 # query into vector
    scores, ids = faiss_index.search(q_vec, top_k)  # FAISS search

    results = []
    for idx in ids[0]:
        if idx != -1:
            results.append(chunks[idx])    # vector id to text chunk

    return results



# /index\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

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


# /search \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@app.post("/search")
def search(query: str = Body(...)):
    retrieved_chunks = retrieve(query, top_k=2)

    return {
        "query": query,
        "results": retrieved_chunks
    }


# /ask \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@app.post("/ask")
def ask(query: str = Body(...)):
    retrieved_chunks = retrieve(query, top_k=2)

    context = "\n\n".join(retrieved_chunks)

    prompt = (
        "You are a strict QA assistant.\n"
        "Use ONLY the context below to answer.\n"
        "If the context is not enough, say: I don't know.\n\n"
        "Context:\n" + context + "\n\n"
        "Question: " + query + "\n"
        "Answer:"
    )

    answer = ask_llm(prompt)
    return {"query": query, "answer": answer}
