from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .models import PaperORM, ChunkORM, FeedbackORM, EvalRunORM


class PaperRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_paper(self, paper: PaperORM) -> PaperORM:
        existing = await self.get_by_id(paper.id)
        if existing:
            existing.title = paper.title
            existing.abstract = paper.abstract
            existing.authors = paper.authors
            existing.categories = paper.categories
            existing.submitted_date = paper.submitted_date
            existing.pdf_url = paper.pdf_url
            existing.full_text = paper.full_text
            await self.session.commit()
            return existing
        else:
            self.session.add(paper)
            await self.session.commit()
            return paper

    async def get_by_id(self, paper_id: str) -> Optional[PaperORM]:
        result = await self.session.execute(select(PaperORM).where(PaperORM.id == paper_id))
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 100) -> List[PaperORM]:
        result = await self.session.execute(select(PaperORM).limit(limit))
        return list(result.scalars().all())


class ChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_chunks(self, chunks: List[ChunkORM]) -> None:
        for chunk in chunks:
            self.session.add(chunk)
        await self.session.commit()

    async def delete_chunks_by_strategy(self, paper_id: str, strategy: str) -> None:
        await self.session.execute(
            delete(ChunkORM).where(
                ChunkORM.paper_id == paper_id, ChunkORM.chunking_strategy == strategy
            )
        )
        await self.session.commit()

    async def get_chunks_by_strategy(self, strategy: str, limit: int = 1000) -> List[ChunkORM]:
        result = await self.session.execute(
            select(ChunkORM).where(ChunkORM.chunking_strategy == strategy).limit(limit)
        )
        return list(result.scalars().all())
