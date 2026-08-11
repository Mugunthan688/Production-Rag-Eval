import re
from enum import Enum
from typing import Dict, Any


class QueryType(str, Enum):
    DEFINITION = "definition"
    MECHANISM = "mechanism"
    WHY = "why"
    COMPARISON = "comparison"
    EVALUATION = "evaluation"
    IMPLEMENTATION = "implementation"
    RESEARCH_PAPER_SPECIFIC = "research_paper_specific"
    MULTI_PART = "multi_part"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class QueryClassifier:
    """Classifies user queries into 9 intent types to guide retrieval and response structuring."""

    @staticmethod
    def classify(query: str) -> QueryType:
        q_lower = query.lower().strip()

        # 1. Multi-part detection
        if (" and " in q_lower or "?" in q_lower[:-1]) and (
            "what is" in q_lower and "how does" in q_lower
        ):
            return QueryType.MULTI_PART

        # 2. Comparison
        if any(k in q_lower for k in [" vs ", " vs. ", "compare", "difference between", "versus"]):
            return QueryType.COMPARISON

        # 3. Evaluation
        if any(k in q_lower for k in ["evaluate", "evaluation", "benchmark", "reliability", "metric", "measure", "score"]):
            return QueryType.EVALUATION

        # 4. Mechanism
        if any(k in q_lower for k in ["how does", "how do", "how work", "mechanism", "workflow", "process", "step"]):
            return QueryType.MECHANISM

        # 5. Why
        if any(k in q_lower for k in ["why does", "why do", "why is", "reason for", "benefit of"]):
            return QueryType.WHY

        # 6. Definition
        if any(k in q_lower for k in ["what is", "define", "definition", "overview of", "explain"]):
            return QueryType.DEFINITION

        # 7. Implementation
        if any(k in q_lower for k in ["how to build", "how to implement", "architecture code", "implementation"]):
            return QueryType.IMPLEMENTATION

        # 8. Research paper specific
        if re.search(r"\b\d{4}\.\d{4,5}\b", query) or "paper" in q_lower:
            return QueryType.RESEARCH_PAPER_SPECIFIC

        return QueryType.DEFINITION
