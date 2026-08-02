import logging
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import ChunkORM
from src.embeddings.factory import get_embedding_provider
from src.retrieval.vector_store import VectorStore
from src.retrieval.bm25_store import BM25Store
from src.retrieval.hybrid import reciprocal_rank_fusion
from src.retrieval.reranker import CrossEncoderReranker
from src.retrieval.query_rewriter import QueryRewriter
from config.settings import settings

logger = logging.getLogger(__name__)


class RetrievalPipeline:
    def __init__(
        self,
        session: AsyncSession,
        hybrid_enabled: bool = settings.HYBRID_SEARCH_ENABLED,
        reranker_enabled: bool = settings.RERANKER_ENABLED,
        query_rewriting_enabled: bool = settings.QUERY_REWRITING_ENABLED,
        embedding_provider: str = settings.EMBEDDING_PROVIDER,
    ):
        self.session = session
        self.hybrid_enabled = hybrid_enabled
        self.reranker_enabled = reranker_enabled
        self.query_rewriting_enabled = query_rewriting_enabled

        self.embedder = get_embedding_provider(embedding_provider)
        self.vector_store = VectorStore(session, self.embedder)
        self.bm25_store = BM25Store(session)
        self.reranker = CrossEncoderReranker() if reranker_enabled else None
        self.query_rewriter = QueryRewriter() if query_rewriting_enabled else None

    async def search(
        self,
        query: str,
        top_k: int = settings.TOP_K_RETRIEVAL,
        top_k_rerank: int = settings.TOP_K_RERANK,
        strategy: str = settings.DEFAULT_CHUNKING_STRATEGY,
    ) -> List[Tuple[ChunkORM, float]]:
        # 1. Optional Query Rewriting & Decomposition
        queries = [query]
        if self.query_rewriting_enabled and self.query_rewriter:
            queries = self.query_rewriter.rewrite_and_decompose(query)
            logger.info(f"Query rewritten into {len(queries)} sub-queries: {queries}")

        aggregated_results: List[Tuple[ChunkORM, float]] = []

        for q in queries:
            # 2. Vector & BM25 retrieval
            dense_res = await self.vector_store.search(q, top_k=top_k, strategy=strategy)

            if self.hybrid_enabled:
                sparse_res = await self.bm25_store.search(q, top_k=top_k, strategy=strategy)
                fused = reciprocal_rank_fusion(dense_res, sparse_res, top_k=top_k)
                aggregated_results.extend(fused)
            else:
                aggregated_results.extend(dense_res)

        # Deduplicate candidates across sub-queries
        seen = set()
        deduped: List[Tuple[ChunkORM, float]] = []
        for chunk, score in aggregated_results:
            if chunk.id not in seen:
                seen.add(chunk.id)
                deduped.append((chunk, score))

        # 3. Optional Reranking
        if self.reranker_enabled and self.reranker:
            return self.reranker.rerank(query, deduped, top_k=top_k_rerank)

        return deduped[:top_k_rerank]
