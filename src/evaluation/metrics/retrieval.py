from typing import List


def compute_precision_at_k(retrieved_papers: List[str], ground_truth_papers: List[str], k: int = 5) -> float:
    if not retrieved_papers or not ground_truth_papers:
        return 0.0
    top_k_retrieved = retrieved_papers[:k]
    relevant_retrieved = [p for p in top_k_retrieved if p in ground_truth_papers]
    return len(relevant_retrieved) / min(k, len(top_k_retrieved))


def compute_recall_at_k(retrieved_papers: List[str], ground_truth_papers: List[str], k: int = 5) -> float:
    if not ground_truth_papers:
        return 0.0
    top_k_retrieved = retrieved_papers[:k]
    relevant_retrieved = [p for p in top_k_retrieved if p in ground_truth_papers]
    return len(relevant_retrieved) / len(ground_truth_papers)


def compute_mrr(retrieved_papers: List[str], ground_truth_papers: List[str]) -> float:
    if not retrieved_papers or not ground_truth_papers:
        return 0.0
    for rank, paper in enumerate(retrieved_papers, start=1):
        if paper in ground_truth_papers:
            return 1.0 / rank
    return 0.0
