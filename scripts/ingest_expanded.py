"""
Multi-topic arXiv ingestion script.
Fetches 30+ new papers across advanced RAG research topics:
  GraphRAG, Self-RAG, Corrective RAG, Speculative RAG,
  Agentic RAG, Long-Context RAG, Multimodal RAG
"""
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db.engine import AsyncSessionLocal, init_db
from src.ingestion.pipeline import IngestionPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Each query targets a specific advanced RAG research topic
EXPANDED_QUERIES = [
    {
        "query": 'all:"GraphRAG"',
        "max_results": 8,
        "topic": "Graph-enhanced RAG",
    },
    {
        "query": 'all:"Self-RAG"',
        "max_results": 8,
        "topic": "Self-reflective RAG",
    },
    {
        "query": 'all:"Corrective RAG"',
        "max_results": 5,
        "topic": "Self-correcting retrieval",
    },
    {
        "query": 'all:"Speculative RAG"',
        "max_results": 5,
        "topic": "Speculative decoding in RAG",
    },
    {
        "query": 'all:"agentic RAG"',
        "max_results": 8,
        "topic": "Agent-based RAG systems",
    },
    {
        "query": 'all:"long context" AND all:"retrieval augmented"',
        "max_results": 8,
        "topic": "Long-context RAG",
    },
    {
        "query": 'all:"multimodal RAG"',
        "max_results": 5,
        "topic": "Multi-modal RAG",
    },
]


async def main():
    await init_db()

    total_new_chunks = 0
    total_new_papers = 0

    for entry in EXPANDED_QUERIES:
        topic = entry["topic"]
        query = entry["query"]
        max_results = entry["max_results"]

        logger.info(f"\n{'='*60}")
        logger.info(f"TOPIC: {topic}")
        logger.info(f"QUERY: {query} (max {max_results} papers)")
        logger.info(f"{'='*60}")

        try:
            async with AsyncSessionLocal() as session:
                pipeline = IngestionPipeline(session, chunking_strategy="recursive")
                chunks = await pipeline.run(query=query, max_results=max_results)
                total_new_chunks += chunks
                total_new_papers += max_results
                logger.info(f"  ✓ {topic}: Ingested {chunks} chunks")
        except Exception as e:
            logger.error(f"  ✗ {topic}: Failed — {e}")
            continue

    logger.info(f"\n{'='*60}")
    logger.info(f"EXPANSION COMPLETE")
    logger.info(f"  Total topics:  {len(EXPANDED_QUERIES)}")
    logger.info(f"  Total chunks:  {total_new_chunks}")
    logger.info(f"{'='*60}")

    # Verify final counts
    from sqlalchemy import select, func
    from src.db.models import PaperORM, ChunkORM

    async with AsyncSessionLocal() as session:
        paper_count = (await session.execute(select(func.count(PaperORM.id)))).scalar()
        chunk_count = (await session.execute(select(func.count(ChunkORM.id)))).scalar()
        logger.info(f"  DB Papers:  {paper_count}")
        logger.info(f"  DB Chunks:  {chunk_count}")


if __name__ == "__main__":
    asyncio.run(main())
