import logging
from typing import List, Tuple

from src.db.models import ChunkORM
from config.settings import settings

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """Reranks retrieved chunks using a cross-encoder model with memory-safe fallback for low-RAM instances."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None
        self._disable_heavy_model = False

    @property
    def model(self):
        if self._disable_heavy_model:
            return None
        if self._model is None:
            # Check available RAM — if on constrained environment (e.g. Render Free 512MB), skip heavy PyTorch model
            try:
                import psutil
                mem = psutil.virtual_memory()
                if mem.total < 1024 * 1024 * 1024:  # System RAM < 1GB
                    logger.info("Constrained RAM environment detected (<1GB). Enabling lightweight zero-RAM reranker.")
                    self._disable_heavy_model = True
                    return None
            except Exception:
                pass

            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(self.model_name)
            except Exception as e:
                logger.warning(f"Could not load heavy CrossEncoder model: {e}. Using lightweight reranker fallback.")
                self._disable_heavy_model = True
                return None
        return self._model

    def rerank(
        self, query: str, chunks: List[Tuple[ChunkORM, float]], top_k: int = settings.TOP_K_RERANK
    ) -> List[Tuple[ChunkORM, float]]:
        if not chunks:
            return []

        # 1. Use heavy PyTorch CrossEncoder if memory permits
        if self.model is not None:
            try:
                pairs = [[query, chunk.text] for chunk, _ in chunks]
                scores = self.model.predict(pairs)
                reranked = [(chunks[i][0], float(scores[i])) for i in range(len(chunks))]
                reranked.sort(key=lambda x: x[1], reverse=True)
                return reranked[:top_k]
            except Exception as e:
                logger.warning(f"CrossEncoder prediction failed: {e}. Using lightweight fallback.")

        # 2. Memory-Safe Lightweight Reranker (0 MB RAM footprint for 512MB Render instances)
        query_terms = set(query.lower().split())
        scored: List[Tuple[ChunkORM, float]] = []

        for chunk, base_score in chunks:
            text_lower = chunk.text.lower()
            match_count = sum(1 for t in query_terms if len(t) > 2 and t in text_lower)
            overlap_ratio = match_count / max(len(query_terms), 1)
            
            # Blend initial hybrid RRF score with exact lexical term overlap
            combined_score = (base_score * 0.6) + (overlap_ratio * 0.4)
            scored.append((chunk, combined_score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

