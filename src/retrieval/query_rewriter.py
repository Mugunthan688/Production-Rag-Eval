import logging
import re
from typing import List, Tuple, Set
from openai import OpenAI

from config.settings import settings

logger = logging.getLogger(__name__)

# Known technical concept expansions for named research frameworks
TECHNICAL_CONCEPT_MAP = {
    "self-rag": [
        "Self-RAG",
        "Self-Reflective Retrieval-Augmented Generation",
        "Self-Reflective RAG",
        "retrieval and reflection",
        "retrieval decision",
        "critique reflection tokens",
        "Self-RAG architecture",
        "Self-RAG training",
        "adaptive retrieval",
    ],
    "graphrag": [
        "GraphRAG",
        "Graph Retrieval-Augmented Generation",
        "knowledge graph RAG",
        "subgraph retrieval",
        "entity relation graph retrieval",
    ],
    "crag": [
        "CRAG",
        "Corrective Retrieval-Augmented Generation",
        "retrieval evaluator",
        "web search correction",
    ],
    "raptor": [
        "RAPTOR",
        "Recursive Abstractive Processing for Tree-Organized Retrieval",
        "tree organized retrieval",
        "hierarchical summary retrieval",
    ],
    "hyde": [
        "HyDE",
        "Hypothetical Document Embeddings",
        "hypothetical document generation",
    ],
    "agentic rag": [
        "Agentic RAG",
        "Agent-based Retrieval-Augmented Generation",
        "autonomous RAG workflow",
        "agentic retrieval planning",
    ],
    "layerrag": [
        "LayerRAG",
        "LayerRAG-Bench",
        "cross-layer reliability",
        "agentic RAG evaluation",
    ],
    "dualg-mrag": [
        "DualG-MRAG",
        "Decoupling Macro-Reasoning and Micro-Matching",
        "macro-reasoning micro-matching",
        "dual graph multimodal RAG",
        "macro reasoning graph",
        "micro matching graph",
    ],
    "dualg": [
        "DualG-MRAG",
        "macro-reasoning micro-matching",
        "dual graph multimodal RAG",
    ],
    "knowledge graph": [
        "knowledge graph RAG",
        "KG-enhanced RAG",
        "entity relation graph retrieval",
        "subgraph retrieval",
        "multi-hop graph reasoning",
    ],
}


class QueryRewriter:
    """LLM & Concept-aware query expander and multi-query decomposer."""

    def __init__(self, api_key: str | None = settings.OPENAI_API_KEY):
        self.client = OpenAI(api_key=api_key) if api_key else None

    def extract_exact_terms(self, query: str) -> List[str]:
        """Extract exact technical terms, acronyms, or hyphenated concept names from query."""
        terms: Set[str] = set()
        
        # 1. Match known concept map keys
        lower_q = query.lower()
        for key in TECHNICAL_CONCEPT_MAP:
            if key in lower_q or key.replace("-", "") in lower_q.replace("-", ""):
                # Find original casing or use standard format
                terms.add(TECHNICAL_CONCEPT_MAP[key][0])

        # 2. Match acronyms / camelCase / hyphenated terms like Self-RAG, GraphRAG, CRAG, HyDE
        regex_matches = re.findall(r"\b[A-Z][a-zA-Za-z0-9-]{2,}\b", query)
        for m in regex_matches:
            if m.lower() not in {"what", "how", "does", "this", "that", "from", "with", "when", "where", "have"}:
                terms.add(m)

        return list(terms)

    def expand_concepts(self, query: str) -> List[str]:
        """Generate deterministic expanded concept queries for named technical terms."""
        expanded: Set[str] = {query}
        lower_q = query.lower()

        for key, variants in TECHNICAL_CONCEPT_MAP.items():
            key_clean = key.replace("-", "")
            lower_clean = lower_q.replace("-", "")
            if key in lower_q or key_clean in lower_clean:
                for variant in variants:
                    expanded.add(variant)

        return list(expanded)

    def rewrite_and_decompose(self, query: str) -> Tuple[List[str], List[str]]:
        """
        Returns:
          - List[str]: List of expanded search queries (deterministic concepts + LLM sub-queries)
          - List[str]: List of exact terms to monitor for diagnostic tracking
        """
        exact_terms = self.extract_exact_terms(query)
        queries = self.expand_concepts(query)

        if not self.client:
            logger.info(f"Using rule-based concept expansion ({len(queries)} queries) for: {query}")
            return queries, exact_terms

        prompt = f"""You are an expert search query optimization assistant for AI research papers.
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
                temperature=0.2,
            )
            content = response.choices[0].message.content
            raw = content.strip() if content else ""
            llm_queries = [q.strip() for q in raw.split("\n") if q.strip()]
            
            # Combine concept variants and LLM sub-queries, keeping unique
            seen = set()
            final_queries = []
            for q in queries + llm_queries:
                if q not in seen:
                    seen.add(q)
                    final_queries.append(q)

            return final_queries, exact_terms
        except Exception as e:
            logger.error(f"Error in LLM query rewriter: {e}")
            return queries, exact_terms
