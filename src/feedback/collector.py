import logging
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.models import FeedbackORM
from .models import FeedbackSubmission

logger = logging.getLogger(__name__)


class FeedbackCollector:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_feedback(self, submission: FeedbackSubmission) -> FeedbackORM:
        record = FeedbackORM(
            query=submission.query,
            answer=submission.answer,
            chunks_used=submission.chunks_used,
            rating=submission.rating,
            comments=submission.comments,
        )
        self.session.add(record)
        await self.session.commit()
        logger.info(f"Feedback logged successfully for query: '{submission.query[:30]}...' with rating={submission.rating}")
        return record
