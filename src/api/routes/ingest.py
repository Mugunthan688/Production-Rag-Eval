from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db_session
from ...ingestion.pipeline import IngestionPipeline

router = APIRouter(tags=["Ingest"])


class IngestRequest(BaseModel):
    query: str = 'all:"retrieval augmented generation"'
    max_results: int = 200
    chunking_strategy: str = "recursive"


@router.post("/ingest")
async def trigger_ingestion(
    req: IngestRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
):
    pipeline = IngestionPipeline(session, chunking_strategy=req.chunking_strategy)
    total_chunks = await pipeline.run(query=req.query, max_results=req.max_results)

    return {
        "status": "success",
        "message": f"Successfully ingested arXiv papers for query '{req.query}'",
        "total_chunks": total_chunks,
    }
