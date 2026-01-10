# AI Training – Phase 1

## Python Basics Summary

- Variables store data such as numbers and text.
- Lists store multiple values in order.
- Dictionaries store key–value pairs.
- Conditions control logic flow.
- Loops iterate over data.
- Functions encapsulate reusable logic.
- Classes group data and behavior together.

## Phase 1 – Page 4: Retrieval-Augmented Generation (RAG)

This milestone demonstrates a basic RAG pipeline implemented locally.

### What was implemented
- Local document loading from the `data/` directory
- Semantic indexing using LlamaIndex (VectorStoreIndex)
- Retrieval of relevant document chunks
- Context injection into a local LLM
- Text generation using a local DeepSeek model via Ollama

### Key Concepts
- Separation of retriever and generator
- Indexing performed once, retrieval performed per query
- Grounding LLM responses in retrieved context

### Files
- `app/FINAL_page4_rag.py`
- `data/doc1.txt`, `data/doc2.txt`

## Milestone 3 (Page 5): FastAPI Embeddings + Vector Search (FAISS)

### Learning Objectives
- Preprocess text data, create embeddings, and index documents.
- Expose these operations via FastAPI endpoints.

### Activities
- Prepare dataset (text files) under the `data/` folder.
- Generate embeddings locally using `sentence-transformers/all-MiniLM-L6-v2`.
- Build a vector index using FAISS (cosine similarity via normalized vectors).
- Build a FastAPI service with endpoints:
  - `POST /index` → preprocess + embed + index documents
  - `POST /search` → accept a query and return relevant document chunks

### Project Structure
- `app/api.py` — FastAPI endpoints (`/index`, `/search`)
- `app/indexer.py` — preprocessing, chunking, embeddings, FAISS indexing/search
- `app/store.py` — saving/loading FAISS index + metadata to/from `storage/`
- `data/` — dataset documents (`.txt` files)
- `storage/` — generated FAISS index + metadata (created after indexing)

### Setup
Activate your venv first, then install dependencies:

```bash
py -m pip install fastapi uvicorn sentence-transformers faiss-cpu

