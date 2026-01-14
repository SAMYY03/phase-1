# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# FASTAPI / FAISS 
# - Read .txt files from data/
# - Split into chunks
# - Create embeddings locally 
# - Build FAISS index
# - Expose two endpoints: /index and /search
# ///////////////////////////////////////////

import os
from fastapi import FastAPI, Body
import faiss
from sentence_transformers import SentenceTransformer

# Create the FastAPI app
app = FastAPI()

# ///////////////////////////////////////////
# GLOBAL VARIABLES (kept in memory)
# ///////////////////////////////////////////

# Load embedding model once 
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# FAISS index will be created after calling /index
faiss_index = None

# Store chunk texts (same order as vectors added to FAISS)
chunks = []


# ///////////////////////////////////////////
# 1) READ FILES FROM data/
# ///////////////////////////////////////////

def read_txt_files(folder="data"):
    """
    Reads all .txt files from the folder and returns a list of full texts.
    """
    texts = []

    # If folder doesn't exist, return empty list
    if not os.path.exists(folder):
        return texts

    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)

        # Only take .txt files
        if os.path.isfile(filepath) and filename.lower().endswith(".txt"):
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                texts.append(f.read())

    return texts


# ///////////////////////////////////////////
#  SIMPLE CHUNKING
# ///////////////////////////////////////////

def split_into_chunks(text, chunk_size=500, overlap=50):
    """
    Splits a long text into smaller pieces (chunks).
    chunk_size and overlap are character counts (simple and beginner friendly).
    """
    result = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:  # avoid empty chunks
            result.append(chunk)

        # Move start forward, but keep some overlap
        start = end - overlap

        # Safety: if overlap is too big and causes no progress
        if start < 0:
            start = 0

    return result


# ///////////////////////////////////////////
# 3) EMBEDDINGS
# ///////////////////////////////////////////

def make_embeddings(text_list):
    """
    Converts a list of texts into vectors (numbers).
    normalize_embeddings=True means vectors are normalized so we can use cosine similarity.
    """
    vectors = model.encode(text_list, convert_to_numpy=True, normalize_embeddings=True)
    return vectors.astype("float32")  # FAISS likes float32


# ///////////////////////////////////////////
# ENDPOINT 1: POST /index
# ///////////////////////////////////////////

@app.post("/index")
def index_documents():
    """
    Reads files -> chunks -> embeddings -> FAISS index
    """
    global faiss_index, chunks

    #  Load documents from data/
    docs = read_txt_files("data")
    if not docs:
        return {"error": "No .txt files found in data/ folder."}

    #  Chunk all documents
    all_chunks = []
    for doc_text in docs:
        doc_chunks = split_into_chunks(doc_text)
        all_chunks.extend(doc_chunks)

    if not all_chunks:
        return {"error": "No chunks created from the documents."}

    #  Create embeddings
    vectors = make_embeddings(all_chunks)

    #  Build FAISS index (cosine similarity)
    # Because vectors are normalized, cosine similarity = inner product
    dim = vectors.shape[1]               # embedding size (example: 384)
    new_index = faiss.IndexFlatIP(dim)   # IP = Inner Product
    new_index.add(vectors)               # store vectors into FAISS

    #  Save in memory
    faiss_index = new_index
    chunks = all_chunks

    # Return status info
    return {
        "status": "success",
        "documents_loaded": len(docs),
        "chunks_indexed": len(chunks),
        "embedding_dim": dim
    }


# ///////////////////////////////////////////
# ENDPOINT 2: POST /search
#///////////////////////////////////////////

@app.post("/search")
def search_documents(query: str = Body(..., embed=True), top_k: int = 2):
    """
    Accepts a query and returns top_k most relevant chunks.
    Body example: {"query": "What is RAG?"}
    """
    # If user didn't call /index yet, no search can happen
    if faiss_index is None or not chunks:
        return {"error": "Index not created. Call POST /index first."}

    #  Embed the query
    query_vector = make_embeddings([query])  # shape: (1, dim)

    #  Search FAISS
    scores, ids = faiss_index.search(query_vector, top_k)

    #  Convert results to a readable format
    results = []
    for rank, idx in enumerate(ids[0]):
        if idx == -1:
            continue

        results.append({
            "rank": rank + 1,
            "score": float(scores[0][rank]),
            "text": chunks[idx]
        })

    return {
        "query": query,
        "top_k": top_k,
        "results": results
    }
