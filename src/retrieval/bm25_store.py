import re
from typing import List, Tuple, Optional
from rank_bm25 import BM25Okapi
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import ChunkORM


class BM25Store:
    """Keyword search using rank-bm25 over database chunks with exact-term boosting."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize preserving hyphenated terms and word tokens."""
        # Find hyphenated words like self-rag and regular words
        tokens = re.findall(r"[\w-]+|\w+", text.lower())
        # Also split hyphens to match both 'self-rag' and ['self', 'rag']
        split_tokens = []
        for t in tokens:
            split_tokens.append(t)
            if "-" in t:
                split_tokens.extend(t.split("-"))
        return split_tokens

    async def search(
        self,
        query: str,
        top_k: int = 20,
        strategy: str = "recursive",
        exact_terms: Optional[List[str]] = None,
    ) -> List[Tuple[ChunkORM, float]]:
        # MEMORY-SAFE: Load only text columns (NO embedding vectors) and cap at 2000 rows.
        # Full embedding columns are ~1.5KB each × 11755 chunks = 17MB+ just for vectors.
        # Using raw SQL to select only the columns we need avoids loading 384-float blobs.
        raw = await self.session.execute(
            text(
                "SELECT id, text, paper_id, chunking_strategy FROM chunks "
                "WHERE chunking_strategy = :strategy LIMIT 2000"
            ),
            {"strategy": strategy},
        )
        rows = raw.fetchall()  # list of (id, text, paper_id, chunking_strategy)

        if not rows:
            return []

        texts = [row[1] for row in rows]
        corpus = [self._tokenize(t) for t in texts]
        bm25 = BM25Okapi(corpus)

        tokenized_query = self._tokenize(query)
        scores = bm25.get_scores(tokenized_query)

        # Exact-term boost for technical terms like "Self-RAG"
        terms_to_boost = exact_terms or []
        query_terms = [t for t in terms_to_boost if len(t) > 2]

        scored_rows: List[Tuple[int, float]] = []
        for i, row in enumerate(rows):
            score = float(scores[i])
            chunk_lower = row[1].lower()

            for term in query_terms:
                term_lower = term.lower()
                if term_lower in chunk_lower:
                    score += 5.0
                if re.search(r"\b" + re.escape(term_lower) + r"\b", chunk_lower):
                    score += 10.0

            scored_rows.append((row[0], score))  # (chunk_id, score)

        scored_rows.sort(key=lambda x: x[1], reverse=True)
        top_ids = [r[0] for r in scored_rows[:top_k]]

        # Fetch only the top_k winning chunk ORM objects (with embeddings) from DB
        if not top_ids:
            return []
        stmt = select(ChunkORM).where(ChunkORM.id.in_(top_ids))
        result = await self.session.execute(stmt)
        chunks_by_id = {c.id: c for c in result.scalars().all()}

        # Return in sorted order
        final: List[Tuple[ChunkORM, float]] = []
        for chunk_id, score in scored_rows[:top_k]:
            if chunk_id in chunks_by_id:
                final.append((chunks_by_id[chunk_id], score))
        return final
