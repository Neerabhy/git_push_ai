import faiss
import numpy as np
import os
import pickle

class VectorStore:
    def __init__(self, dim=None, db_path="vector_db"):
        self.db_path = db_path
        self.dim = dim
        self.texts = []
        self.metadatas = []

        # If index exists, load it
        if os.path.exists(self.db_path + "_index.faiss") and os.path.exists(self.db_path + "_texts.pkl"):
            self.load()
        else:
            if dim is None:
                raise ValueError("dim must be provided for new FAISS index")
            # HNSW index with 32 neighbors
            self.index = faiss.IndexHNSWFlat(dim, 32)

    def add(self, embeddings, texts, metadatas=None):
        embeddings = np.array(embeddings).astype('float32')
        self.index.add(embeddings)
        self.texts.extend(texts)
        if metadatas:
            self.metadatas.extend(metadatas)
        else:
            self.metadatas.extend([{}] * len(texts))
        self.save()

    def search(self, query_embedding, top_k=3):
        query_embedding = np.array([query_embedding]).astype('float32')
        D, I = self.index.search(query_embedding, top_k)
        results = []
        for i in I[0]:
            results.append({
                "text": self.texts[i],
                "metadata": self.metadatas[i]
            })
        return results

    def save(self):
        faiss.write_index(self.index, self.db_path + "_index.faiss")
        with open(self.db_path + "_texts.pkl", "wb") as f:
            pickle.dump((self.texts, self.metadatas), f)

    def load(self):
        self.index = faiss.read_index(self.db_path + "_index.faiss")
        with open(self.db_path + "_texts.pkl", "rb") as f:
            self.texts, self.metadatas = pickle.load(f)
