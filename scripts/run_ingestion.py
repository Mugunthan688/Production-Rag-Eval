import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to sys.path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db.engine import AsyncSessionLocal, init_db
from src.ingestion.pipeline import IngestionPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(description="Run complete RAG ingestion pipeline")
    parser.add_argument("--query", type=str, default='all:"retrieval augmented generation"')
    parser.add_argument("--max-results", type=int, default=200)
    parser.add_argument("--strategy", type=str, default="recursive")
    args = parser.parse_args()

    await init_db()

    async with AsyncSessionLocal() as session:
        pipeline = IngestionPipeline(session, chunking_strategy=args.strategy)
        total_chunks = await pipeline.run(query=args.query, max_results=args.max_results)
        print(f"Ingestion completed! Inserted {total_chunks} chunks.")


if __name__ == "__main__":
    asyncio.run(main())
