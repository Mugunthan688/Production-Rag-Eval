from typing import List, Dict, Any
from collections import Counter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.models import FeedbackORM


class FeedbackAnalyzer:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_lowest_rated_queries(self, limit: int = 10) -> List[FeedbackORM]:
        stmt = select(FeedbackORM).where(FeedbackORM.rating < 0).order_by(FeedbackORM.timestamp.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_problematic_chunks(self, limit: int = 10) -> List[Dict[str, Any]]:
        stmt = select(FeedbackORM).where(FeedbackORM.rating < 0)
        result = await self.session.execute(stmt)
        negative_feedback = result.scalars().all()

        chunk_counter = Counter()
        for fb in negative_feedback:
            for chunk_id in fb.chunks_used:
                chunk_counter[chunk_id] += 1

        most_common = chunk_counter.most_common(limit)
        return [{"chunk_id": cid, "negative_count": count} for cid, count in most_common]
