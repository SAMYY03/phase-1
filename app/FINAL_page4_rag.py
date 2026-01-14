import requests
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

 # FUNCTION: to call local Ollama LLM \\\\\\\\\\

def ollama_generate(prompt, model_name="deepseek-r1:1.5b"):
    url = "http://127.0.0.1:11434/api/generate"

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False, 
        "options": {
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["response"]

    # Main program \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

def main():
    #  Embedding model for indexing and retrieval
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    Settings.llm = None

    #  Load docs and build index 
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)

    #  Ask questions in a loop
    while True:
        question = input("\nEnter your question (or type 'exit'): ")

        
        if question.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        #  Retrieve relevant chunks
        retriever = index.as_retriever(similarity_top_k=2)
        nodes = retriever.retrieve(question)

        #  Build context
        if nodes:
            context_parts = []
            for node in nodes:
                context_parts.append(node.get_content())
            context = "\n\n".join(context_parts)
        else:
            context = "No context found."

        #  Build prompt
        prompt = (
            "You are a strict QA assistant.\n"
            "Use ONLY the context below to answer.\n"
            "If the context is not enough, say: I don't know.\n\n"
            "Context:\n" + context + "\n\n"
            "Question: " + question + "\n"
            "Answer:"
        )

        #  Generate answer
        answer = ollama_generate(prompt)

        #  Print result
        print("\n ANSWER: \n")
        print(answer)


if __name__ == "__main__":
    main()
