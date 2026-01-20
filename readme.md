# Phase 1

## Phase 1 – Page 4: local LLM + a simple index build.

This milestone demonstrates a **basic local RAG pipeline** implemented using **LlamaIndex** and a **local LLM via Ollama**.

### What was implemented
- Local document loading from the `data/` directory
- Semantic indexing using **LlamaIndex (VectorStoreIndex)**
- Retrieval of the most relevant document chunks
- Context injection into the prompt
- Text generation using a **local LLM (DeepSeek-R1) via Ollama**
- Interactive CLI question-answering loop

### Key Concepts
- Separation of **retriever** and **generator**
- Indexing performed once, retrieval performed per query
- Grounding LLM responses strictly in retrieved context
- Local, offline-friendly RAG architecture

### Files
- `app/FINAL_page4_rag.py`
- `data/doc1.txt`
- `data/doc2.txt`
- `data/rag.txt`
- `data/aiagents.txt`

---------------

## Phase 1 – Page 5: FastAPI RAG Service (FAISS)

This milestone implements a **REST-based RAG system** using **FastAPI**, **FAISS**, and **Sentence Transformers**.

Documents are preprocessed, chunked, embedded using  
`sentence-transformers/all-MiniLM-L6-v2`, and indexed in FAISS for fast similarity search.

### What was implemented
- Document loading from the `data/` directory
- Text chunking for efficient retrieval
- Embedding generation using Sentence Transformers
- Vector indexing using **FAISS**
- REST API built with **FastAPI**
- Local LLM inference via **Ollama**

### Exposed Endpoints
- **POST /index**  
  Preprocess and index documents from the `data/` folder

- **POST /search**  
  Perform semantic search and return relevant text chunks

- **POST /ask**  
  Retrieve context and generate a grounded answer using the local LLM

### Key Concepts
- In-memory vector indexing
- Semantic similarity search
- Retrieval-Augmented Generation via API
- Strict context-only answering

### Files
- `app/fastapi.py`
- `data/*.txt`
