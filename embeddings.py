import pickle
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class EmbeddingModel:

    def __init__(self, model_path="tfidf.pkl"):

        self.model_path = model_path

        if os.path.exists(self.model_path):
            self.load()
        else:
            self.vectorizer = TfidfVectorizer()

    def embed_texts(self, texts):

        
        if not hasattr(self.vectorizer, "vocabulary_"):
            embeddings = self.vectorizer.fit_transform(texts)
            self.save()
        else:
            embeddings = self.vectorizer.transform(texts)

        return embeddings.toarray().astype(float)

    def embed_query(self, query):

        if not hasattr(self.vectorizer, "vocabulary_"):
            raise ValueError(
                "Vectorizer not "
            )

        embedding = self.vectorizer.transform([query])

        return embedding.toarray()[0].astype(float)

    def save(self):

        with open(self.model_path, "wb") as f:
            pickle.dump(self.vectorizer, f)

    def load(self):

        with open(self.model_path, "rb") as f:
            self.vectorizer = pickle.load(f)
