from src.evaluation.metrics.retrieval import compute_precision_at_k, compute_recall_at_k, compute_mrr
from src.evaluation.metrics.operational import compute_latency_percentiles, estimate_query_cost


def test_retrieval_metrics():
    retrieved = ["p1", "p2", "p3", "p4", "p5"]
    ground_truth = ["p2", "p5"]

    assert compute_precision_at_k(retrieved, ground_truth, k=5) == 2 / 5
    assert compute_recall_at_k(retrieved, ground_truth, k=5) == 2 / 2
    assert compute_mrr(retrieved, ground_truth) == 1 / 2  # First match at rank 2


def test_operational_metrics():
    latencies = [10.0, 20.0, 30.0, 40.0, 50.0]
    p50, p95 = compute_latency_percentiles(latencies)
    assert p50 == 30.0
    assert p95 == 48.0

    cost = estimate_query_cost(1000, 500)
    assert cost > 0.0
