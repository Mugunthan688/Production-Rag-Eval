import time
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..retrieval.pipeline import RetrievalPipeline
from .generator import AnswerGenerator
from .confidence import ConfidenceScorer
from ..db.models import PaperORM


class GenerationPipeline:
    """Production RAG Generation Pipeline: retrieval, paper enrichment, methodology generation, response validation, confidence scoring."""

    def __init__(self, session: AsyncSession, retrieval_pipeline: RetrievalPipeline | None = None):
        self.session = session
        self.retrieval_pipeline = retrieval_pipeline or RetrievalPipeline(session)
        self.generator = AnswerGenerator()
        self.confidence_scorer = ConfidenceScorer()

    async def answer_query(self, query: str, strategy: str = "recursive") -> Dict[str, Any]:
        start_time = time.time()

        # 1. Retrieve context chunks
        retrieved_results = await self.retrieval_pipeline.search(query=query, strategy=strategy)

        # 2. Enrich chunks with paper metadata BEFORE generation so LLM has title & metadata
        paper_ids = list({chunk.paper_id for chunk, _ in retrieved_results})
        paper_meta: Dict[str, PaperORM] = {}
        if paper_ids:
            result = await self.session.execute(
                select(PaperORM).where(PaperORM.id.in_(paper_ids))
            )
            for p in result.scalars().all():
                paper_meta[p.id] = p

        chunks_used = []
        for chunk, score in retrieved_results:
            paper_obj = paper_meta.get(chunk.paper_id)
            chunks_used.append(
                {
                    "chunk_id": chunk.id,
                    "paper_id": chunk.paper_id,
                    "chunk_index": getattr(chunk, "chunk_index", 0),
                    "score": score,
                    "text": chunk.text,
                    "paper_title": paper_obj.title if paper_obj else "arXiv Paper",
                    "paper_authors": (paper_obj.authors[:3] if paper_obj and paper_obj.authors else []),
                    "paper_categories": (paper_obj.categories[:3] if paper_obj and paper_obj.categories else []),
                    "paper_pdf_url": paper_obj.pdf_url if paper_obj else "",
                }
            )

        # 3. Generate methodology-focused answer using enriched chunks & ResponseValidator
        answer = self.generator.generate_answer(query, chunks_used)

        latency_ms = (time.time() - start_time) * 1000

        # 4. Confidence scoring
        confidence_report = self.confidence_scorer.score(
            query=query, answer=answer, chunks=retrieved_results
        )

        diagnostics_dict = (
            self.retrieval_pipeline.last_diagnostics.to_dict()
            if self.retrieval_pipeline.last_diagnostics
            else {}
        )

        return {
            "query": query,
            "answer": answer,
            "chunks_used": chunks_used,
            "latency_ms": latency_ms,
            "papers_searched": len(paper_ids),
            "confidence": confidence_report,
            "retrieval_diagnostics": diagnostics_dict,
        }
