import logging
from typing import List

from src.embeddings.base import BaseEmbeddingProvider
from config.settings import settings

logger = logging.getLogger(__name__)


class LocalEmbeddingProvider(BaseEmbeddingProvider):
    """Open-source local embedding model (e.g., BGE / E5 via sentence-transformers)."""

    def __init__(self, model_name: str = settings.LOCAL_EMBEDDING_MODEL):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode(text, show_progress_bar=False, convert_to_numpy=True)
        return embedding.tolist()

