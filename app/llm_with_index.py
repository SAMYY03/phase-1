from transformers import pipeline
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def main() -> None:
    # 1) Local embeddings (no OpenAI)
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    Settings.llm = None  # keep LlamaIndex LLM disabled

    # 2) Load docs + build index
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)

    # 3) Retrieve top matching chunks (IMPORTANT: get nodes)
    question = "What is RAG?"
    retriever = index.as_retriever(similarity_top_k=2)
    nodes = retriever.retrieve(question)

    # 4) Build context from REAL document text
    context = "\n\n".join(node.get_content() for node in nodes) if nodes else "No context found."

    # 5) Local LLM generation
    llm = pipeline("text-generation", model="distilgpt2")
    prompt = (
        "You are a strict QA assistant.\n"
        "Use ONLY the context below to answer.\n"
        "If the context is not enough, say: I don't know.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )

    out = llm(prompt, max_new_tokens=60, truncation=True, do_sample=True, temperature=0.7)

    print("\n=== CONTEXT USED ===\n")
    print(context)
    print("\n=== MODEL OUTPUT ===\n")
    print(out[0]["generated_text"])


if __name__ == "__main__":
    main()
