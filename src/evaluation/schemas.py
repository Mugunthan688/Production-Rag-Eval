from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EvalQuestion(BaseModel):
    id: Optional[str] = None
    question: str
    ground_truth_answer: str
    ground_truth_source_papers: List[str]
    category: str


class QuestionEvalResult(BaseModel):
    question: str
    generated_answer: str
    retrieved_paper_ids: List[str]
    retrieved_chunk_ids: List[str]
    precision_at_k: float
    recall_at_k: float
    mrr: float
    faithfulness_score: float
    relevance_score: float
    latency_ms: float
    estimated_cost_usd: float


class ExperimentRunResult(BaseModel):
    experiment_name: str
    config: Dict[str, Any]
    total_questions: int
    mean_precision_at_k: float
    mean_recall_at_k: float
    mean_mrr: float
    mean_faithfulness: float
    mean_relevance: float
    p50_latency_ms: float
    p95_latency_ms: float
    total_cost_usd: float
    per_question_results: List[QuestionEvalResult]
