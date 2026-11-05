"""Embedding engine using SentenceTransformers with model caching."""

import os
import numpy as np
from typing import List, Union

# Set offline mode if cached model is available to prevent slow network handshakes
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from sentence_transformers import SentenceTransformer
from config import DEFAULT_EMBEDDING_MODEL
from utils.logging_config import logger

class EmbeddingEngine:
    """Singleton-style wrapper for SentenceTransformer embeddings."""

    _instance = None
    _model = None
    _model_name = None

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        if EmbeddingEngine._model is None or EmbeddingEngine._model_name != model_name:
            logger.info(f"Loading SentenceTransformer embedding model: {model_name}")
            try:
                # First attempt with local_files_only for maximum speed and zero network latency
                EmbeddingEngine._model = SentenceTransformer(model_name, local_files_only=True)
            except Exception:
                # Fallback to standard loading if not yet in cache
                EmbeddingEngine._model = SentenceTransformer(model_name)
            EmbeddingEngine._model_name = model_name

    @property
    def model(self) -> SentenceTransformer:
        return EmbeddingEngine._model

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embeds a list of text strings into normalized numpy vectors (float32).
        Cosine similarity equals inner product for normalized vectors.
        """
        if not texts:
            return np.empty((0, self.get_dimension()), dtype="float32")
        embeddings = self.model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embeddings.astype("float32")

    def embed_query(self, query: str) -> np.ndarray:
        """Embeds a single query string into a normalized 1D numpy vector (float32)."""
        embedding = self.model.encode(
            query,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding.astype("float32")

    def get_dimension(self) -> int:
        """Returns the embedding vector dimension."""
        if hasattr(self.model, "get_embedding_dimension"):
            return self.model.get_embedding_dimension()
        return self.model.get_sentence_embedding_dimension()
