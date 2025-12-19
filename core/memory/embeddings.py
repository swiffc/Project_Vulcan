"""
Embedding Model Wrapper

Thin adapter around sentence-transformers for generating embeddings.
Default model: all-MiniLM-L6-v2 (22MB, fast, good quality)
"""

from typing import List
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings


class SentenceTransformerEmbedding(EmbeddingFunction):
    """Custom embedding function using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        """Lazy load the model to avoid startup delay."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def __call__(self, input: Documents) -> Embeddings:
        """Generate embeddings for a list of documents."""
        embeddings = self.model.encode(input, convert_to_numpy=True)
        return embeddings.tolist()


def get_embedding_function(model_name: str = "all-MiniLM-L6-v2") -> EmbeddingFunction:
    """Get an embedding function for use with Chroma.

    Args:
        model_name: Name of the sentence-transformers model.
                   Default is all-MiniLM-L6-v2 (22MB, fast).

    Returns:
        EmbeddingFunction compatible with Chroma.
    """
    return SentenceTransformerEmbedding(model_name)
