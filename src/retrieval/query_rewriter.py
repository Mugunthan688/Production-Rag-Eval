import logging
from typing import List
from openai import OpenAI

from config.settings import settings

logger = logging.getLogger(__name__)


class QueryRewriter:
    """LLM query rewriter & multi-query sub-question decomposer."""

    def __init__(self, api_key: str | None = settings.OPENAI_API_KEY):
        self.client = OpenAI(api_key=api_key) if api_key else None

    def rewrite_and_decompose(self, query: str) -> List[str]:
        if not self.client:
            logger.warning("OpenAI API key missing for query rewriting. Returning original query.")
            return [query]

        prompt = f"""You are an expert search query optimization assistant.
Given a user query, perform two actions:
1. Clarify vague terms and rewrite into a precise academic search query.
2. Decompose complex multi-part questions into 2-3 specific sub-queries.

Output ONLY the queries separated by newlines, with no extra text or numbering.

User Query: "{query}"
Sub-Queries:"""

        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            raw = response.choices[0].message.content.strip()
            queries = [q.strip() for q in raw.split("\n") if q.strip()]
            return queries if queries else [query]
        except Exception as e:
            logger.error(f"Error in query rewriter: {e}")
            return [query]
