import re
import logging
from typing import List, Tuple, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import ChunkORM
from src.embeddings.factory import get_embedding_provider
from src.retrieval.vector_store import VectorStore
from src.retrieval.bm25_store import BM25Store
from src.retrieval.hybrid import reciprocal_rank_fusion
from src.retrieval.reranker import CrossEncoderReranker
from src.retrieval.query_rewriter import QueryRewriter
from src.retrieval.diagnostics import RetrievalDiagnostics, STATUS_SUCCESS, STATUS_RETRIEVAL_FAILURE, STATUS_CORPUS_MISSING_INFO
from src.ingestion.paper_selector import PRIMARY_FOUNDATIONAL_PAPERS
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
        self.query_rewriter = QueryRewriter()
        self.last_diagnostics: Optional[RetrievalDiagnostics] = None

    async def _check_corpus_for_exact_terms(self, exact_terms: List[str], strategy: str) -> bool:
        """Direct database check to determine if corpus genuinely contains exact technical terms."""
        if not exact_terms:
            return False

        for term in exact_terms:
            stmt = select(func.count(ChunkORM.id)).where(
                ChunkORM.chunking_strategy == strategy,
                func.lower(ChunkORM.text).contains(term.lower())
            )
            res = await self.session.execute(stmt)
            count = res.scalar() or 0
            if count > 0:
                return True
        return False

    def _contains_term(self, text: str, terms: List[str]) -> bool:
        for t in terms:
            if re.search(r"\b" + re.escape(t) + r"\b", text, re.IGNORECASE) or t.lower() in text.lower():
                return True
        return False

    async def search(
        self,
        query: str,
        top_k: int = settings.TOP_K_RETRIEVAL,
        top_k_rerank: int = settings.TOP_K_RERANK,
        strategy: str = settings.DEFAULT_CHUNKING_STRATEGY,
    ) -> List[Tuple[ChunkORM, float]]:
        # Initialize diagnostics tracker
        diag = RetrievalDiagnostics(query=query)

        # 1. Concept Expansion & Rewriting
        queries = [query]
        exact_terms = self.query_rewriter.extract_exact_terms(query)
        if self.query_rewriting_enabled and self.query_rewriter:
            queries, extracted_exact = self.query_rewriter.rewrite_and_decompose(query)
            exact_terms = list(set(exact_terms + extracted_exact))
            logger.info(f"Query expanded into {len(queries)} sub-queries: {queries}")

        diag.expanded_queries = queries
        diag.exact_terms_checked = exact_terms

        # Check if corpus contains exact terms
        diag.exact_term_in_corpus = await self._check_corpus_for_exact_terms(exact_terms, strategy)

        all_dense_results: List[Tuple[ChunkORM, float]] = []
        all_sparse_results: List[Tuple[ChunkORM, float]] = []
        aggregated_results: List[Tuple[ChunkORM, float]] = []

        for q in queries:
            # 2. Dense Vector retrieval
            dense_res = await self.vector_store.search(q, top_k=top_k, strategy=strategy)
            all_dense_results.extend(dense_res)

            # 3. Sparse BM25 retrieval with exact term boosting
            if self.hybrid_enabled:
                sparse_res = await self.bm25_store.search(q, top_k=top_k, strategy=strategy, exact_terms=exact_terms)
                all_sparse_results.extend(sparse_res)
                fused = reciprocal_rank_fusion(dense_res, sparse_res, top_k=top_k)
                aggregated_results.extend(fused)
            else:
                aggregated_results.extend(dense_res)

        # Update diagnostic tracking for initial stages
        diag.vector_candidates_count = len(all_dense_results)
        diag.exact_term_in_vector = any(self._contains_term(c.text, exact_terms) for c, _ in all_dense_results)

        diag.bm25_candidates_count = len(all_sparse_results)
        diag.exact_term_in_bm25 = any(self._contains_term(c.text, exact_terms) for c, _ in all_sparse_results)

        # Deduplicate candidates across sub-queries
        seen = set()
        deduped: List[Tuple[ChunkORM, float]] = []
        for chunk, score in aggregated_results:
            if chunk.id not in seen:
                seen.add(chunk.id)
                deduped.append((chunk, score))

        diag.rrf_fused_count = len(deduped)
        diag.exact_term_in_rrf = any(self._contains_term(c.text, exact_terms) for c, _ in deduped)

        # 4. Optional Reranking with exact term preservation
        final_results: List[Tuple[ChunkORM, float]] = []
        if self.reranker_enabled and self.reranker and deduped:
            reranked = self.reranker.rerank(query, deduped, top_k=top_k_rerank * 2)
            
            # Ensure exact term candidates are preserved if available in candidate pool
            exact_matches = [item for item in reranked if self._contains_term(item[0].text, exact_terms)]
            non_exact_matches = [item for item in reranked if not self._contains_term(item[0].text, exact_terms)]
            
            # Prioritize top exact matches, filled with top reranked items
            combined = exact_matches + non_exact_matches
            seen_ids = set()
            for chunk, score in combined:
                if chunk.id not in seen_ids:
                    seen_ids.add(chunk.id)
                    final_results.append((chunk, score))
                if len(final_results) >= top_k_rerank:
                    break
        else:
            final_results = deduped[:top_k_rerank]

        # Primary-Source-First Prioritization: Ensure chunks from primary foundational papers are placed first
        primary_ids = set(PRIMARY_FOUNDATIONAL_PAPERS.keys())
        primary_chunks = [item for item in final_results if str(item[0].paper_id).strip() in primary_ids or any(pid in str(item[0].id) for pid in primary_ids)]
        secondary_chunks = [item for item in final_results if item not in primary_chunks]
        if primary_chunks:
            final_results = primary_chunks + secondary_chunks

        diag.reranked_count = len(final_results)
        diag.exact_term_in_reranked = any(self._contains_term(c.text, exact_terms) for c, _ in final_results)

        # Classify final retrieval diagnostics
        final_texts = [c.text for c, _ in final_results]
        diag.classify(final_texts)
        self.last_diagnostics = diag

        # Log internal report string for debugging
        logger.info(diag.to_report_string())

        return final_results
