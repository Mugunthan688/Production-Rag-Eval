import logging
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Set, Tuple
from datetime import datetime

from .models import PaperMetadata

logger = logging.getLogger(__name__)

# Foundational / Primary research papers mapping (ArXiv ID -> Concept)
PRIMARY_FOUNDATIONAL_PAPERS = {
    "2310.11511": "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection",
    "2404.16130": "From Local to Global: A Graph RAG Approach to Query-Focused Summarization",
    "2401.18059": "RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval",
    "2212.10496": "Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE)",
    "2401.15884": "Corrective Retrieval Augmented Generation (CRAG)",
    "2607.27353": "LayerRAG-Bench: Evaluating Cross-Layer Reliability in Agentic RAG",
    "2305.06983": "Active Retrieval Augmented Generation (FLARE)",
    "2309.15217": "RAGAS: Automated Evaluation of Retrieval Augmented Generation",
    "2305.14283": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
    "2303.11366": "Reflexion: Language Agents with Verbal Reinforcement Learning",
    "2402.19473": "Agentic RAG: A Survey of Agentic Retrieval-Augmented Generation",
    "2607.28580": "DualG-MRAG: Decoupling Macro-Reasoning and Micro-Matching for Multimodal RAG",
}

TOPIC_PRIORITIES = {
    "RAG Core": {
        "queries": [
            'all:"retrieval augmented generation"',
            'all:"RAG evaluation" OR "RAG hallucination"',
            'all:"RAG faithfulness" OR "RAG reliability"',
            'all:"corrective RAG" OR "adaptive RAG"',
            'all:"agentic RAG" OR "multimodal RAG"',
        ],
        "quota_ratio": 0.30,
        "keywords": ["retrieval-augmented generation", "retrieval augmented", "rag", "hallucination", "faithfulness"],
    },
    "Retrieval & Reranking": {
        "queries": [
            'all:"dense retrieval" AND "vector search"',
            'all:"sparse retrieval" AND "BM25"',
            'all:"hybrid search" AND "reranking"',
            'all:"cross-encoder" OR "multi-vector retrieval"',
            'all:"query expansion" OR "query rewriting"',
        ],
        "quota_ratio": 0.25,
        "keywords": ["dense retrieval", "sparse retrieval", "bm25", "hybrid retrieval", "reranking", "cross-encoder", "query expansion"],
    },
    "Advanced RAG": {
        "queries": [
            'all:"GraphRAG" OR "knowledge graph RAG"',
            'all:"Self-RAG" OR "Self-Reflective RAG"',
            'all:"CRAG" OR "Corrective Retrieval"',
            'all:"RAPTOR" OR "tree-organized retrieval"',
            'all:"HyDE" OR "hypothetical document embeddings"',
        ],
        "quota_ratio": 0.20,
        "keywords": ["graphrag", "self-rag", "crag", "raptor", "hyde", "active rag", "hierarchical rag"],
    },
    "LLM & Agent Foundations": {
        "queries": [
            'all:"LLM agents" AND "tool use"',
            'all:"function calling" AND "planning"',
            'all:"multi-agent systems" AND "reasoning"',
            'all:"verbal reinforcement" OR "reflexion"',
        ],
        "quota_ratio": 0.10,
        "keywords": ["agent", "tool use", "function calling", "planning", "reasoning", "multi-agent", "reflexion"],
    },
    "Evaluation & Benchmarks": {
        "queries": [
            'all:"RAGAS" OR "retrieval evaluation"',
            'all:"answer relevance" OR "context relevance"',
            'all:"Recall@K" OR "MRR" OR "NDCG"',
            'all:"benchmark design" AND "LLM evaluation"',
        ],
        "quota_ratio": 0.10,
        "keywords": ["ragas", "recall@k", "precision@k", "mrr", "ndcg", "evaluation", "benchmark", "context relevance"],
    },
    "Supporting Technologies": {
        "queries": [
            'all:"text embeddings" AND "transformers"',
            'all:"vector database" OR "information retrieval"',
            'all:"long-context language models"',
        ],
        "quota_ratio": 0.05,
        "keywords": ["embedding", "transformer", "vector database", "information retrieval", "long-context"],
    },
}


class PaperSelector:
    """Intelligent paper selection engine for research-grade RAG corpus."""

    @staticmethod
    def calculate_relevance_score(paper: PaperMetadata, topic: str) -> float:
        """
        Calculates relevance score based on:
        - Primary paper match (+50.0)
        - Title & abstract keyword match
        - Category relevance (cs.CL, cs.AI, cs.IR, cs.LG)
        - Recency weight
        """
        score = 0.0
        
        # 1. Primary paper bonus
        clean_id = paper.id.split("v")[0]
        if clean_id in PRIMARY_FOUNDATIONAL_PAPERS:
            score += 50.0

        title_lower = paper.title.lower()
        abstract_lower = paper.abstract.lower()

        # 2. Topic keyword matches
        topic_info = TOPIC_PRIORITIES.get(topic, {})
        keywords = topic_info.get("keywords", [])
        for kw in keywords:
            if kw in title_lower:
                score += 8.0
            if kw in abstract_lower:
                score += 3.0

        # 3. Category match
        preferred_cats = {"cs.CL", "cs.AI", "cs.IR", "cs.LG", "cs.SE"}
        matching_cats = set(paper.categories).intersection(preferred_cats)
        score += len(matching_cats) * 2.5

        # 4. Recency bonus (newer papers get up to 5 points)
        if paper.submitted_date:
            year = paper.submitted_date.year
            if year >= 2024:
                score += 5.0
            elif year == 2023:
                score += 3.0
            elif year == 2022:
                score += 1.5

        return round(score, 2)

    @staticmethod
    def deduplicate_and_rank(papers: List[PaperMetadata], topic: str) -> List[Tuple[PaperMetadata, float]]:
        """Deduplicates papers by ID/Title and ranks by relevance score."""
        seen_ids: Set[str] = set()
        seen_titles: Set[str] = set()
        scored_list: List[Tuple[PaperMetadata, float]] = []

        for paper in papers:
            clean_id = paper.id.split("v")[0]
            clean_title = re.sub(r"\s+", " ", paper.title.lower().strip())

            if clean_id in seen_ids or clean_title in seen_titles:
                continue

            seen_ids.add(clean_id)
            seen_titles.add(clean_title)

            score = PaperSelector.calculate_relevance_score(paper, topic)
            scored_list.append((paper, score))

        scored_list.sort(key=lambda x: x[1], reverse=True)
        return scored_list
