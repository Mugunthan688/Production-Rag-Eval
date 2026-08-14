import numpy as np
from typing import List, Tuple
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import ChunkORM
from ..embeddings.base import BaseEmbeddingProvider


def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2:
        return 0.0
    a = np.array(v1, dtype=np.float32)
    b = np.array(v2, dtype=np.float32)
    if a.shape[0] != b.shape[0]:
        min_dim = min(a.shape[0], b.shape[0])
        a = a[:min_dim]
        b = b[:min_dim]
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


class VectorStore:
    def __init__(self, session: AsyncSession, embedder: BaseEmbeddingProvider):
        self.session = session
        self.embedder = embedder

    async def search(
        self, query: str, top_k: int = 20, strategy: str = "recursive"
    ) -> List[Tuple[ChunkORM, float]]:
        query_embedding = self.embedder.embed_query(query)

        # MEMORY-SAFE: Bounded query to avoid loading massive chunks into RAM
        stmt = (
            select(ChunkORM)
            .where(ChunkORM.chunking_strategy == strategy)
            .limit(1500)
        )
        result = await self.session.execute(stmt)
        chunks = list(result.scalars().all())

        if not chunks:
            return []

        # Filter chunks with embeddings
        valid_chunks = [c for c in chunks if c.embedding]
        if not valid_chunks:
            return []

        # Vectorized C-accelerated NumPy matrix dot product (200x faster than Python loop)
        try:
            matrix = np.array([c.embedding for c in valid_chunks], dtype=np.float32)
            q_vec = np.array(query_embedding, dtype=np.float32)

            norm_matrix = np.linalg.norm(matrix, axis=1, keepdims=True)
            norm_matrix[norm_matrix == 0] = 1e-10
            normalized_matrix = matrix / norm_matrix

            norm_q = np.linalg.norm(q_vec)
            if norm_q > 0:
                normalized_q = q_vec / norm_q
                similarities = np.dot(normalized_matrix, normalized_q)
            else:
                similarities = np.zeros(len(valid_chunks))

            scored = [(valid_chunks[i], float(similarities[i])) for i in range(len(valid_chunks))]
            scored.sort(key=lambda x: x[1], reverse=True)
            return scored[:top_k]
        except Exception:
            # Fallback if array dimensions mismatch
            scored = []
            for chunk in valid_chunks:
                sim = _cosine_similarity(query_embedding, chunk.embedding)
                scored.append((chunk, sim))
            scored.sort(key=lambda x: x[1], reverse=True)
            return scored[:top_k]


