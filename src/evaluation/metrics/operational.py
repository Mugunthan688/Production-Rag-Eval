from typing import List, Tuple
import numpy as np


def compute_latency_percentiles(latencies_ms: List[float]) -> Tuple[float, float]:
    if not latencies_ms:
        return 0.0, 0.0
    p50 = float(np.percentile(latencies_ms, 50))
    p95 = float(np.percentile(latencies_ms, 95))
    return p50, p95


def estimate_query_cost(
    prompt_tokens: int, completion_tokens: int, model: str = "gpt-4o-mini"
) -> float:
    # Standard pricing approximations per 1k tokens
    pricing = {
        "gpt-4o-mini": {"prompt": 0.00015 / 1000, "completion": 0.0006 / 1000},
        "gpt-4o": {"prompt": 0.005 / 1000, "completion": 0.015 / 1000},
    }
    rates = pricing.get(model, pricing["gpt-4o-mini"])
    return (prompt_tokens * rates["prompt"]) + (completion_tokens * rates["completion"])
