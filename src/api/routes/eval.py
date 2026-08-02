from typing import Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db_session
from ...evaluation.experiment_runner import ExperimentRunner

router = APIRouter(tags=["Evaluation"])


class EvalRunRequest(BaseModel):
    config: Dict[str, Any]
    eval_file: str = "data/eval_set.json"


@router.post("/eval/run")
async def run_evaluation_experiment(req: EvalRunRequest, session: AsyncSession = Depends(get_db_session)):
    runner = ExperimentRunner(session)
    result = await runner.run_experiment(config=req.config, eval_file=req.eval_file)
    return result.model_dump()
