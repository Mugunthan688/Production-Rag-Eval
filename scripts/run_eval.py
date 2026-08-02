import argparse
import asyncio
import yaml
import logging
import sys
from pathlib import Path

# Add project root to sys.path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db.engine import AsyncSessionLocal, init_db
from src.evaluation.experiment_runner import ExperimentRunner

logging.basicConfig(level=logging.INFO)


async def main():
    parser = argparse.ArgumentParser(description="Run RAG experiment evaluation")
    parser.add_argument("--config", type=str, default="config/experiments/baseline.yaml")
    parser.add_argument("--eval-file", type=str, default="data/eval_set.json")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    await init_db()

    async with AsyncSessionLocal() as session:
        runner = ExperimentRunner(session)
        res = await runner.run_experiment(config=config, eval_file=args.eval_file)
        print(f"\n=== Experiment '{res.experiment_name}' Results ===")
        print(f"Precision@5: {res.mean_precision_at_k:.3f}")
        print(f"Recall@5:    {res.mean_recall_at_k:.3f}")
        print(f"MRR:         {res.mean_mrr:.3f}")
        print(f"Faithfulness:{res.mean_faithfulness:.3f}")
        print(f"Relevance:   {res.mean_relevance:.3f}")
        print(f"p50 Latency: {res.p50_latency_ms:.1f} ms")


if __name__ == "__main__":
    asyncio.run(main())
