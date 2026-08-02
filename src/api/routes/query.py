from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db_session
from ...generation.pipeline import GenerationPipeline
from ...retrieval.pipeline import RetrievalPipeline

router = APIRouter(tags=["Query"])


class QueryRequest(BaseModel):
    query: str
    chunking_strategy: str = "recursive"
    hybrid_search: bool = True
    reranker: bool = True
    query_rewriting: bool = True


@router.post("/query")
async def execute_query(req: QueryRequest, session: AsyncSession = Depends(get_db_session)):
    retrieval_pipe = RetrievalPipeline(
        session=session,
        hybrid_enabled=req.hybrid_search,
        reranker_enabled=req.reranker,
        query_rewriting_enabled=req.query_rewriting,
    )
    gen_pipe = GenerationPipeline(session, retrieval_pipeline=retrieval_pipe)
    res = await gen_pipe.answer_query(query=req.query, strategy=req.chunking_strategy)
    return res
