#  AI Training   
Python Foundations & Retrieval-Augmented Generation (RAG)

##  Overview
This repository contains all deliverables for **Phase 1** of the AI Training Program.  
Phase 1 focuses on Python fundamentals and building a complete **local Retrieval-Augmented Generation (RAG) pipeline** from scratch.

All Phase 1 requirements have been successfully completed.

---

##  Phase 1 Objectives
- Learn Python fundamentals for AI development
- Understand core Generative AI concepts
- Build a local RAG pipeline
- Implement semantic search using embeddings
- Store and reuse chat history
- Expose the system through a FastAPI service

---

##  Topics Covered

### 1- Python Basics
- Variables and data types  
- Lists, dictionaries, tuples  
- Conditions and loops  
- Functions  
- Classes and object-oriented programming  

---

### 2- Core AI Concepts
- Generative AI basics  
- Embeddings and semantic meaning  
- Text chunking and preprocessing  
- Indexing vs retrieval  
- Retriever–Generator separation  

--------------

### 3- Retrieval-Augmented Generation (RAG)
- Local document loading
- Embedding generation using Sentence Transformers
- Vector indexing with FAISS
- Similarity-based retrieval
- Prompt engineering with retrieved context
- Local LLM inference using Ollama

-------------

##  System Architecture

User  
↓  
FastAPI API  
↓  
Chat History (SQLite)  
↓  
Embedding Model (SentenceTransformer)  
↓  
FAISS Vector Index  
↓  
Retrieved Context  
↓  
Prompt Engineering  
↓  
Local LLM (Ollama)  
↓  
Response  




