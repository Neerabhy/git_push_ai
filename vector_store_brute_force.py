import numpy as np
import pickle
import os


class VectorStore:
    def __init__(self, db_path="vector_db.pkl"):
        self.db_path = db_path
        self.embeddings = []
        self.texts = []
        self.metadatas = []

        if os.path.exists(self.db_path):
            self.load()

    def add(self, embeddings, texts, metadatas=None):

        embeddings = np.array(embeddings, dtype=float)

        if metadatas is None:
            metadatas = [{} for _ in texts]

        self.embeddings.extend(embeddings)
        self.texts.extend(texts)
        self.metadatas.extend(metadatas)

        self.save()

    def search(self, query_embedding, top_k=3):
        similarities = []

        for emb in self.embeddings:
            sim = self.cosine_similarity(query_embedding, emb)
            similarities.append(sim)

        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []

        for i in top_indices:
            results.append({
                "text": self.texts[i],
                "metadata": self.metadatas[i],
                "score": similarities[i]
            })

        return results


    def cosine_similarity(self, a, b):
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return np.dot(a, b) / denom


    def save(self):
        with open(self.db_path, "wb") as f:
            pickle.dump(
                (self.embeddings, self.texts, self.metadatas),
                f
            )

    def load(self):
        with open(self.db_path, "rb") as f:
            self.embeddings, self.texts, self.metadatas = pickle.load(f)
