import logging
from typing import List, Tuple

from src.db.models import ChunkORM
from config.settings import settings

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """Reranks retrieved chunks using a cross-encoder model."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name)
        return self._model


    def rerank(
        self, query: str, chunks: List[Tuple[ChunkORM, float]], top_k: int = settings.TOP_K_RERANK
    ) -> List[Tuple[ChunkORM, float]]:
        if not chunks:
            return []

        pairs = [[query, chunk.text] for chunk, _ in chunks]
        scores = self.model.predict(pairs)

        reranked = [(chunks[i][0], float(scores[i])) for i in range(len(chunks))]
        reranked.sort(key=lambda x: x[1], reverse=True)

        return reranked[:top_k]
