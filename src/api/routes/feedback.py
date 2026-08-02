from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db_session
from ...feedback.models import FeedbackSubmission
from ...feedback.collector import FeedbackCollector
from ...feedback.analyzer import FeedbackAnalyzer

router = APIRouter(tags=["Feedback"])


@router.post("/feedback")
async def submit_feedback(submission: FeedbackSubmission, session: AsyncSession = Depends(get_db_session)):
    collector = FeedbackCollector(session)
    record = await collector.log_feedback(submission)
    return {"status": "success", "feedback_id": record.id}


@router.get("/feedback/analytics")
async def get_feedback_analytics(session: AsyncSession = Depends(get_db_session)):
    analyzer = FeedbackAnalyzer(session)
    lowest_rated = await analyzer.get_lowest_rated_queries(limit=10)
    bad_chunks = await analyzer.get_problematic_chunks(limit=10)

    return {
        "lowest_rated_queries": [
            {
                "id": f.id,
                "query": f.query,
                "answer": f.answer,
                "rating": f.rating,
                "comments": f.comments,
            }
            for f in lowest_rated
        ],
        "problematic_chunks": bad_chunks,
    }
