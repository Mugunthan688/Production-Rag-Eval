import json
import logging
from typing import Dict, Any
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from .loader import load_eval_dataset
from .schemas import QuestionEvalResult, ExperimentRunResult
from .metrics.retrieval import compute_precision_at_k, compute_recall_at_k, compute_mrr
from .metrics.generation import compute_faithfulness, compute_relevance
from .metrics.operational import compute_latency_percentiles
from ..generation.pipeline import GenerationPipeline
from ..retrieval.pipeline import RetrievalPipeline
from ..db.models import EvalRunORM

logger = logging.getLogger(__name__)


class ExperimentRunner:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def run_experiment(
        self, config: Dict[str, Any], eval_file: str = "data/eval_set.json"
    ) -> ExperimentRunResult:
        exp_name = config.get("experiment_name", "unnamed_experiment")
        questions = load_eval_dataset(eval_file)

        retrieval_pipe = RetrievalPipeline(
            session=self.session,
            hybrid_enabled=config.get("hybrid_search", True),
            reranker_enabled=config.get("reranker", True),
            query_rewriting_enabled=config.get("query_rewriting", True),
        )
        gen_pipe = GenerationPipeline(self.session, retrieval_pipeline=retrieval_pipe)

        results: list[QuestionEvalResult] = []
        latencies: list[float] = []

        logger.info(f"Starting experiment '{exp_name}' over {len(questions)} evaluation questions.")

        for q in questions:
            res = await gen_pipe.answer_query(
                query=q.question, strategy=config.get("chunking_strategy", "recursive")
            )
            latencies.append(res["latency_ms"])

            retrieved_paper_ids = list(set([c["paper_id"] for c in res["chunks_used"]]))
            retrieved_chunk_ids = [c["chunk_id"] for c in res["chunks_used"]]

            p_at_k = compute_precision_at_k(retrieved_paper_ids, q.ground_truth_source_papers, k=5)
            r_at_k = compute_recall_at_k(retrieved_paper_ids, q.ground_truth_source_papers, k=5)
            mrr_val = compute_mrr(retrieved_paper_ids, q.ground_truth_source_papers)

            context_texts = [c["text"] for c in res["chunks_used"]]
            faithfulness = compute_faithfulness(res["answer"], context_texts)
            relevance = compute_relevance(res["answer"], q.question)

            results.append(
                QuestionEvalResult(
                    question=q.question,
                    generated_answer=res["answer"],
                    retrieved_paper_ids=retrieved_paper_ids,
                    retrieved_chunk_ids=retrieved_chunk_ids,
                    precision_at_k=p_at_k,
                    recall_at_k=r_at_k,
                    mrr=mrr_val,
                    faithfulness_score=faithfulness,
                    relevance_score=relevance,
                    latency_ms=res["latency_ms"],
                    estimated_cost_usd=0.001,
                )
            )

        p50, p95 = compute_latency_percentiles(latencies)

        mean_p_at_k = sum(r.precision_at_k for r in results) / len(results) if results else 0.0
        mean_r_at_k = sum(r.recall_at_k for r in results) / len(results) if results else 0.0
        mean_mrr_val = sum(r.mrr for r in results) / len(results) if results else 0.0
        mean_faith = sum(r.faithfulness_score for r in results) / len(results) if results else 0.0
        mean_rel = sum(r.relevance_score for r in results) / len(results) if results else 0.0

        exp_result = ExperimentRunResult(
            experiment_name=exp_name,
            config=config,
            total_questions=len(questions),
            mean_precision_at_k=mean_p_at_k,
            mean_recall_at_k=mean_r_at_k,
            mean_mrr=mean_mrr_val,
            mean_faithfulness=mean_faith,
            mean_relevance=mean_rel,
            p50_latency_ms=p50,
            p95_latency_ms=p95,
            total_cost_usd=len(questions) * 0.001,
            per_question_results=results,
        )

        # Save result JSON to results/
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        out_file = results_dir / f"{exp_name}_result.json"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(exp_result.model_dump_json(indent=2))

        # Save to DB
        eval_orm = EvalRunORM(
            id=exp_name,
            experiment_name=exp_name,
            config_json=config,
            metrics_json=exp_result.model_dump(),
        )
        self.session.add(eval_orm)
        await self.session.commit()

        logger.info(f"Experiment '{exp_name}' finished. Saved to {out_file}")
        return exp_result
