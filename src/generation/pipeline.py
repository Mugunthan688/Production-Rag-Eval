import time
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from ..retrieval.pipeline import RetrievalPipeline
from .generator import AnswerGenerator
from ..db.models import ChunkORM


class GenerationPipeline:
    def __init__(self, session: AsyncSession, retrieval_pipeline: RetrievalPipeline | None = None):
        self.session = session
        self.retrieval_pipeline = retrieval_pipeline or RetrievalPipeline(session)
        self.generator = AnswerGenerator()

    async def answer_query(self, query: str, strategy: str = "recursive") -> Dict[str, Any]:
        start_time = time.time()

        # 1. Retrieve chunks
        retrieved_results = await self.retrieval_pipeline.search(query=query, strategy=strategy)

        # 2. Generate answer
        answer = self.generator.generate_answer(query, retrieved_results)

        latency_ms = (time.time() - start_time) * 1000

        chunks_used = [
            {
                "chunk_id": chunk.id,
                "paper_id": chunk.paper_id,
                "score": score,
                "text": chunk.text,
            }
            for chunk, score in retrieved_results
        ]

        return {
            "query": query,
            "answer": answer,
            "chunks_used": chunks_used,
            "latency_ms": latency_ms,
        }
