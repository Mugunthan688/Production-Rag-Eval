import re
from typing import List, Tuple
from rank_bm25 import BM25Okapi
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import ChunkORM


class BM25Store:
    """Keyword search using rank-bm25 over database chunks."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())

    async def search(
        self, query: str, top_k: int = 20, strategy: str = "recursive"
    ) -> List[Tuple[ChunkORM, float]]:
        stmt = select(ChunkORM).where(ChunkORM.chunking_strategy == strategy)
        result = await self.session.execute(stmt)
        chunks = list(result.scalars().all())

        if not chunks:
            return []

        corpus = [self._tokenize(chunk.text) for chunk in chunks]
        bm25 = BM25Okapi(corpus)

        tokenized_query = self._tokenize(query)
        scores = bm25.get_scores(tokenized_query)

        scored_chunks = list(zip(chunks, scores))
        scored_chunks.sort(key=lambda x: x[1], reverse=True)

        return scored_chunks[:top_k]
