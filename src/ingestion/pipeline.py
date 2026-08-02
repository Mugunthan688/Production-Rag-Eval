import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from .arxiv_client import ArxivClient
from .chunking.factory import get_chunker
from .models import PaperMetadata, Chunk
from ..db.models import PaperORM, ChunkORM
from ..db.repositories import PaperRepository, ChunkRepository
from ..embeddings.factory import get_embedding_provider

from config.settings import settings

logger = logging.getLogger(__name__)


class IngestionPipeline:
    def __init__(
        self,
        db_session: AsyncSession,
        chunking_strategy: str = "recursive",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        embedding_provider: str = settings.EMBEDDING_PROVIDER,
    ):
        self.session = db_session
        self.arxiv_client = ArxivClient()
        self.chunker = get_chunker(strategy=chunking_strategy, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.embedder = get_embedding_provider(provider_type=embedding_provider)
        self.paper_repo = PaperRepository(db_session)
        self.chunk_repo = ChunkRepository(db_session)

    async def run(self, query: str = 'all:"retrieval augmented generation"', max_results: int = 200) -> int:
        papers = self.arxiv_client.fetch_papers(search_query=query, max_results=max_results)
        logger.info(f"Processing {len(papers)} fetched papers...")

        total_chunks = 0
        for paper in papers:
            # 1. Save Paper metadata
            paper_orm = PaperORM(
                id=paper.id,
                title=paper.title,
                abstract=paper.abstract,
                authors=paper.authors,
                categories=paper.categories,
                submitted_date=paper.submitted_date,
                pdf_url=paper.pdf_url,
                full_text=paper.full_text,
            )
            await self.paper_repo.upsert_paper(paper_orm)

            # 2. Chunk paper
            chunks: List[Chunk] = self.chunker.chunk_paper(paper)

            # 3. Delete existing chunks for this paper & strategy to ensure idempotency
            await self.chunk_repo.delete_chunks_by_strategy(paper.id, chunks[0].chunking_strategy if chunks else "recursive")

            # 4. Save Chunks
            if chunks:
                chunk_texts = [c.text for c in chunks]
                embeddings = self.embedder.embed_documents(chunk_texts)
                for chunk, emb in zip(chunks, embeddings):
                    chunk.embedding = emb

                chunk_orms = [
                    ChunkORM(
                        id=chunk.id,
                        paper_id=chunk.paper_id,
                        chunk_index=chunk.chunk_index,
                        text=chunk.text,
                        chunking_strategy=chunk.chunking_strategy,
                        embedding=chunk.embedding,
                        metadata_json=chunk.metadata,
                    )
                    for chunk in chunks
                ]
                await self.chunk_repo.save_chunks(chunk_orms)
                total_chunks += len(chunks)

        logger.info(f"Ingestion complete: Processed {len(papers)} papers, saved {total_chunks} chunks.")
        return total_chunks
