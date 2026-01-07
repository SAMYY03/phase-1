from transformers import pipeline
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def main() -> None:
    print(">>> RUNNING FINAL PAGE 4 RAG SCRIPT <<<")

    # 1) Local embeddings
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    Settings.llm = None  # disable LlamaIndex LLM

    # 2) Load documents
    documents = SimpleDirectoryReader("data").load_data()
    print(f">>> Loaded {len(documents)} documents")
    print("\n>>> RAW DOCUMENT TEXT <<<")
    
    for i, d in enumerate(documents):
        # d.text may exist depending on version; fallback to str(d)
        text = getattr(d, "text", None) or str(d)
        print(f"\n--- Doc {i+1} raw ---")
        print(text[:500])


    # 3) Build index
    index = VectorStoreIndex.from_documents(documents)

    # 4) Retrieve REAL content
    question = "What is RAG?"
    retriever = index.as_retriever(similarity_top_k=2)
    nodes = retriever.retrieve(question)

    print(">>> RETRIEVED CONTENT <<<")
    for i, node in enumerate(nodes):
        print(f"\n--- Chunk {i+1} ---")
        print(node.get_content())

    context = "\n\n".join(node.get_content() for node in nodes)

    # 5) Local LLM
    llm = pipeline("text-generation", model="distilgpt2")

    prompt = (
        "You are a strict QA assistant.\n"
        "Use ONLY the context below to answer.\n"
        "If the context is not enough, say: I don't know.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )

    result = llm(prompt, max_new_tokens=80, truncation=True)

    print("\n>>> FINAL ANSWER <<<\n")
    print(result[0]["generated_text"])


if __name__ == "__main__":
    main()
