import json
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd


def load_all_experiment_results(results_dir: str = "results") -> List[Dict[str, Any]]:
    path = Path(results_dir)
    results: List[Dict[str, Any]] = []
    if not path.exists():
        return results

    for p in path.glob("*_result.json"):
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            results.append(data)
    return results


def build_comparison_dataframe(results: List[Dict[str, Any]] | None = None) -> pd.DataFrame:
    if results is None:
        results = load_all_experiment_results()

    if not results:
        return pd.DataFrame()

    rows = []
    for r in results:
        rows.append(
            {
                "Experiment": r.get("experiment_name"),
                "Chunking": r.get("config", {}).get("chunking_strategy"),
                "Hybrid": r.get("config", {}).get("hybrid_search"),
                "Reranker": r.get("config", {}).get("reranker"),
                "QueryRewrite": r.get("config", {}).get("query_rewriting"),
                "Precision@5": round(r.get("mean_precision_at_k", 0.0), 3),
                "Recall@5": round(r.get("mean_recall_at_k", 0.0), 3),
                "MRR": round(r.get("mean_mrr", 0.0), 3),
                "Faithfulness": round(r.get("mean_faithfulness", 0.0), 3),
                "Relevance": round(r.get("mean_relevance", 0.0), 3),
                "p50 Latency (ms)": round(r.get("p50_latency_ms", 0.0), 1),
                "p95 Latency (ms)": round(r.get("p95_latency_ms", 0.0), 1),
            }
        )

    return pd.DataFrame(rows)
