'''import ollama
from embeddings import EmbeddingModel
from vector_store_brute_force import VectorStore

embedder = EmbeddingModel()
store = VectorStore()

while True:
    query = input("\nAsk a question (or 'exit'): ")

    if query.lower() == "exit":
        break

    query_embedding = embedder.embed_query(query)
    docs = store.search(query_embedding)

    context = "\n".join(docs)

    prompt = f"""
        Use the following context to answer the question.

        Context:
        {context}

        Question:
        {query}
    """

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    print("\nAnswer:\n", response["message"]["content"])
'''