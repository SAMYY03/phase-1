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
