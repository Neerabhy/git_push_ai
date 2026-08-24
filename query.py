import requests
from embeddings import EmbeddingModel
from vector_store_brute_force import VectorStore

OLLAMA_URL = "http://localhost:11434/api/generate"


def ask_llm(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"].strip()


def build_prompt(context, question):
    return f"""
You are a helpful assistant.

Use the provided context to answer the question if it is relevant.
If the context is insufficient, you may use your general knowledge.

Context:
{context}

Question:
{question}

Answer clearly and concisely:
"""


def main():
    embedder = EmbeddingModel()
    
    
    store = VectorStore()

    print("📚 RAG system ready! Type 'exit' to quit.\n")

    while True:
        query = input("You: ")

        if query.lower() in ["exit", "quit"]:
            break

       
        query_embedding = embedder.embed_query(query)

        
        docs = store.search(query_embedding, top_k=8)

        
        context = "\n".join(doc["text"] for doc in docs if "text" in doc)

        
        if not context.strip():
            context = "No relevant document context found."

        
        prompt = build_prompt(context, query)
        answer = ask_llm(prompt)

        print(f"\nAssistant: {answer}\n")


if __name__ == "__main__":
    main()
