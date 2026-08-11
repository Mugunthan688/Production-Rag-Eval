import re
from typing import List, Tuple, Optional
from rank_bm25 import BM25Okapi
from sqlalchemy import select
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
        stmt = select(ChunkORM).where(ChunkORM.chunking_strategy == strategy)
        result = await self.session.execute(stmt)
        chunks = list(result.scalars().all())

        if not chunks:
            return []

        corpus = [self._tokenize(chunk.text) for chunk in chunks]
        bm25 = BM25Okapi(corpus)

        tokenized_query = self._tokenize(query)
        scores = bm25.get_scores(tokenized_query)

        # Exact-term boost for technical terms like "Self-RAG"
        terms_to_boost = exact_terms or []
        query_terms = [t for t in terms_to_boost if len(t) > 2]

        scored_chunks = []
        for i, chunk in enumerate(chunks):
            score = float(scores[i])
            chunk_lower = chunk.text.lower()
            
            # Apply exact string match bonus
            for term in query_terms:
                term_lower = term.lower()
                if term_lower in chunk_lower:
                    score += 5.0  # Strong lexical boost for exact concept match
                if re.search(r"\b" + re.escape(term_lower) + r"\b", chunk_lower):
                    score += 10.0  # Extra word boundary boost

            scored_chunks.append((chunk, score))

        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_k]
