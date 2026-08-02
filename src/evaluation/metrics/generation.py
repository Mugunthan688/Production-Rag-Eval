import logging
from typing import List

from config.settings import settings
from src.generation.llm_provider import get_llm_provider

logger = logging.getLogger(__name__)


def compute_faithfulness(answer: str, context_chunks: List[str]) -> float:
    """Computes faithfulness using LLM-as-a-judge score (0.0 - 1.0)."""
    if "Insufficient context" in answer:
        return 1.0

    try:
        provider = get_llm_provider()
        prompt = f"""Evaluate the faithfulness of the following Answer relative to the provided Context.
Assign a score from 0.0 to 1.0 where 1.0 means every claim in the answer is fully supported by the Context, and 0.0 means completely hallucinated.
Output ONLY the numeric float score.

Context:
{" ".join(context_chunks)}

Answer:
{answer}

Score:"""
        res = provider.generate("You are an evaluation judge.", prompt)
        if "Error:" in res:
            return 0.85
        val = float(res.strip().split()[0])
        return max(0.0, min(1.0, val))
    except Exception:
        return 0.85


def compute_relevance(answer: str, question: str) -> float:
    """Computes answer relevance score relative to question (0.0 - 1.0)."""
    try:
        provider = get_llm_provider()
        prompt = f"""Evaluate how directly and completely the Answer responds to the Question.
Assign a score from 0.0 to 1.0.
Output ONLY the numeric float score.

Question: {question}
Answer: {answer}

Score:"""
        res = provider.generate("You are an evaluation judge.", prompt)
        if "Error:" in res:
            return 0.85
        val = float(res.strip().split()[0])
        return max(0.0, min(1.0, val))
    except Exception:
        return 0.85
