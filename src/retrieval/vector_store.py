import numpy as np
from typing import List, Tuple
from sqlalchemy import select
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

        stmt = select(ChunkORM).where(ChunkORM.chunking_strategy == strategy)
        result = await self.session.execute(stmt)
        chunks = list(result.scalars().all())

        if not chunks:
            return []

        scored = []
        for chunk in chunks:
            if chunk.embedding:
                sim = _cosine_similarity(query_embedding, chunk.embedding)
            else:
                sim = 0.0
            scored.append((chunk, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
