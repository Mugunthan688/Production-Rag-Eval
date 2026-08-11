"""
Confidence-Calibrated RAG: Retrieval Quality & Answer Grounding Scorer

This module differentiates the RAG system by computing a structured
confidence report for every query response. It measures:

  1. Retrieval Confidence  — Are the retrieved chunks relevant and coherent?
  2. Source Diversity       — Does the answer draw from multiple independent papers?
  3. Score Distribution     — Is there a clear "winner" chunk or noisy results?
  4. Answer Grounding       — How well is the generated answer supported by evidence?
  5. Hallucination Risk     — Probability the answer contains unsupported claims.

Most RAG systems return just an answer. This one returns a calibrated
confidence report that explains *why* you should (or shouldn't) trust it.
"""

import logging
import math
from typing import Dict, Any, List, Tuple
from collections import Counter

from src.db.models import ChunkORM

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """Computes multi-dimensional confidence metrics for RAG responses."""

    # ── Retrieval signal thresholds ──────────────────────────────
    HIGH_RELEVANCE_THRESHOLD = 0.75   # chunk score above this = strong hit
    LOW_RELEVANCE_THRESHOLD = 0.30    # below this = noise
    MIN_CHUNKS_FOR_CONFIDENCE = 2     # need at least N good chunks

    def score(
        self,
        query: str,
        answer: str,
        chunks: List[Tuple[ChunkORM, float]],
    ) -> Dict[str, Any]:
        """
        Compute a full confidence report for a single query response.

        Returns a dict with:
          - retrieval_confidence: float [0-1]
          - source_diversity: float [0-1]
          - score_distribution: {"mean", "std", "top1_gap", "entropy"}
          - answer_grounding: float [0-1]
          - hallucination_risk: "low" | "medium" | "high"
          - confidence_label: "HIGH" | "MEDIUM" | "LOW"
          - explanation: human-readable summary
        """

        if not chunks or "Insufficient context" in answer:
            return self._empty_report("Insufficient context in indexed paper corpus.")

        scores = [s for _, s in chunks]
        paper_ids = [c.paper_id for c, _ in chunks]

        # ── 1. Retrieval Confidence ─────────────────────────────
        retrieval_conf = self._retrieval_confidence(scores)

        # ── 2. Source Diversity (Shannon entropy over paper IDs) ─
        diversity = self._source_diversity(paper_ids)

        # ── 3. Score Distribution Analysis ──────────────────────
        dist = self._score_distribution(scores)

        # ── 4. Answer Grounding ─────────────────────────────────
        grounding = self._answer_grounding(answer, chunks)

        # ── 5. Composite Confidence ─────────────────────────────
        raw_composite = (
            0.35 * retrieval_conf
            + 0.20 * diversity
            + 0.15 * dist["normalized_entropy"]
            + 0.30 * grounding
        )
        composite = max(0.0, min(1.0, raw_composite))

        # ── 6. Hallucination Risk ───────────────────────────────
        if composite >= 0.70 and grounding >= 0.60:
            risk = "low"
        elif composite >= 0.45:
            risk = "medium"
        else:
            risk = "high"

        # ── 7. Confidence Label ─────────────────────────────────
        if composite >= 0.70:
            label = "HIGH"
        elif composite >= 0.45:
            label = "MEDIUM"
        else:
            label = "LOW"

        explanation = self._build_explanation(
            retrieval_conf, diversity, grounding, risk, len(chunks), len(set(paper_ids))
        )

        return {
            "retrieval_confidence": round(retrieval_conf, 3),
            "source_diversity": round(diversity, 3),
            "score_distribution": {
                "mean": round(dist["mean"], 4),
                "std": round(dist["std"], 4),
                "top1_gap": round(dist["top1_gap"], 4),
                "entropy": round(dist["entropy"], 4),
                "normalized_entropy": round(dist["normalized_entropy"], 4),
            },
            "answer_grounding": round(grounding, 3),
            "hallucination_risk": risk,
            "composite_confidence": round(composite, 3),
            "confidence_label": label,
            "explanation": explanation,
        }

    # ── Private helpers ──────────────────────────────────────────

    def _retrieval_confidence(self, scores: List[float]) -> float:
        """
        Measures how many chunks are above the relevance threshold
        and penalizes noisy (low-score) retrievals.
        Reranker logits are sigmoid-normalized into [0, 1].
        """
        if not scores:
            return 0.0

        # Sigmoid normalize raw logits if any score is outside [0, 1]
        normalized_scores = []
        for s in scores:
            if s < 0 or s > 1:
                # Sigmoid transform: 1 / (1 + e^-s)
                norm_s = 1.0 / (1.0 + math.exp(-max(-15.0, min(15.0, s))))
            else:
                norm_s = s
            normalized_scores.append(norm_s)

        high_count = sum(1 for s in normalized_scores if s >= self.HIGH_RELEVANCE_THRESHOLD)
        low_count = sum(1 for s in normalized_scores if s < self.LOW_RELEVANCE_THRESHOLD)

        # Proportion of strong hits
        hit_ratio = high_count / len(normalized_scores)

        # Penalty for noise
        noise_penalty = (low_count / len(normalized_scores)) * 0.3

        # Bonus for having at least MIN_CHUNKS_FOR_CONFIDENCE strong hits
        sufficiency_bonus = min(high_count / self.MIN_CHUNKS_FOR_CONFIDENCE, 1.0) * 0.2

        # Mean score contribution
        mean_score = sum(normalized_scores) / len(normalized_scores)

        conf = 0.5 * hit_ratio + 0.3 * mean_score + sufficiency_bonus - noise_penalty
        return max(0.0, min(1.0, conf))

    def _source_diversity(self, paper_ids: List[str]) -> float:
        """
        Shannon entropy over paper sources, normalized to [0, 1].
        Higher = answer draws from more independent sources = more reliable.
        """
        if not paper_ids:
            return 0.0

        n = len(paper_ids)
        unique = len(set(paper_ids))

        if unique <= 1:
            return 0.1  # Single-source answers get minimal diversity

        counts = Counter(paper_ids)
        entropy = -sum(
            (count / n) * math.log2(count / n)
            for count in counts.values()
            if count > 0
        )
        max_entropy = math.log2(unique) if unique > 1 else 1.0

        return min(entropy / max_entropy, 1.0)

    def _score_distribution(self, scores: List[float]) -> Dict[str, float]:
        """Analyze the shape of the score distribution."""
        n = len(scores)
        if n == 0:
            return {"mean": 0, "std": 0, "top1_gap": 0, "entropy": 0, "normalized_entropy": 0}

        # Normalize raw logits into [0, 1] using sigmoid
        norm_scores = []
        for s in scores:
            if s < 0 or s > 1:
                norm_s = 1.0 / (1.0 + math.exp(-max(-15.0, min(15.0, s))))
            else:
                norm_s = s
            norm_scores.append(norm_s)

        mean = sum(norm_scores) / n
        variance = sum((s - mean) ** 2 for s in norm_scores) / n
        std = math.sqrt(variance)

        sorted_scores = sorted(norm_scores, reverse=True)
        top1_gap = (sorted_scores[0] - sorted_scores[1]) if n >= 2 else 0.0

        # Entropy of probability-normalized scores (higher = more uniform = less certain)
        total = sum(norm_scores) if sum(norm_scores) > 0 else 1.0
        probs = [s / total for s in norm_scores]
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        max_entropy = math.log2(n) if n > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        return {
            "mean": mean,
            "std": std,
            "top1_gap": top1_gap,
            "entropy": entropy,
            "normalized_entropy": normalized_entropy,
        }

    def _answer_grounding(
        self, answer: str, chunks: List[Tuple[ChunkORM, float]]
    ) -> float:
        """
        Measures how well the generated answer is grounded in retrieved chunks.

        Uses token-overlap heuristic: what fraction of substantive answer
        tokens also appear in at least one retrieved chunk?
        This is a fast, model-free approximation of faithfulness.
        """
        if not answer or not chunks:
            return 0.0

        # Extract substantive tokens (length >= 4, lowercase, alpha-only)
        answer_tokens = set(
            t.lower() for t in answer.split()
            if len(t) >= 4 and t.isalpha()
        )

        if not answer_tokens:
            return 0.5  # Short/numeric answers — ambiguous grounding

        # Build chunk vocabulary (weighted by score)
        chunk_vocab: set[str] = set()
        for chunk, score in chunks:
            tokens = set(
                t.lower() for t in chunk.text.split()
                if len(t) >= 4 and t.isalpha()
            )
            chunk_vocab.update(tokens)

        # Overlap ratio
        overlap = answer_tokens & chunk_vocab
        grounding = len(overlap) / len(answer_tokens)

        return min(grounding, 1.0)

    def _build_explanation(
        self,
        retrieval_conf: float,
        diversity: float,
        grounding: float,
        risk: str,
        num_chunks: int,
        num_papers: int,
    ) -> str:
        """Build a human-readable confidence explanation."""
        parts: List[str] = []

        parts.append(
            f"Retrieved {num_chunks} chunks from {num_papers} unique paper(s)."
        )

        if retrieval_conf >= 0.7:
            parts.append("Strong retrieval signal — top chunks are highly relevant.")
        elif retrieval_conf >= 0.4:
            parts.append("Moderate retrieval signal — some relevant chunks found.")
        else:
            parts.append("Weak retrieval signal — chunks may not be directly relevant.")

        if diversity >= 0.7:
            parts.append("High source diversity — answer corroborated across papers.")
        elif diversity <= 0.2:
            parts.append("Low source diversity — answer relies on a single paper.")

        if grounding >= 0.7:
            parts.append("Answer is well-grounded in retrieved evidence.")
        elif grounding >= 0.4:
            parts.append("Answer is partially grounded — some claims may extend beyond evidence.")
        else:
            parts.append("Answer has weak grounding — high risk of unsupported claims.")

        if risk == "high":
            parts.append("⚠️ Elevated hallucination risk. Verify claims against source papers.")

        return " ".join(parts)

    def _empty_report(self, reason: str) -> Dict[str, Any]:
        return {
            "retrieval_confidence": 0.0,
            "source_diversity": 0.0,
            "score_distribution": {
                "mean": 0.0, "std": 0.0, "top1_gap": 0.0,
                "entropy": 0.0, "normalized_entropy": 0.0,
            },
            "answer_grounding": 0.0,
            "hallucination_risk": "high",
            "composite_confidence": 0.0,
            "confidence_label": "LOW",
            "explanation": reason,
        }
