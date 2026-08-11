"""
Evaluation benchmark for named technical concepts in RAG retrieval.
Tests queries such as:
- What is Self-RAG?
- What is GraphRAG?
- What is CRAG?
- What is RAPTOR?
- What is Agentic RAG?
- What is HyDE?
- How does Self-RAG work?

Measures:
- Recall@K
- Precision@K
- MRR (Mean Reciprocal Rank)
- Reranker retention rate
- Final context presence
- Failure status (RETRIEVAL_FAILURE vs CORPUS_MISSING_INFORMATION vs SUCCESS)
"""

import asyncio
import re
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.engine import AsyncSessionLocal
from src.retrieval.pipeline import RetrievalPipeline
from src.retrieval.diagnostics import STATUS_SUCCESS, STATUS_RETRIEVAL_FAILURE, STATUS_CORPUS_MISSING_INFO


TEST_CONCEPT_QUERIES = [
    {"query": "What is Self-RAG and how does it work?", "target_term": "Self-RAG"},
    {"query": "What is GraphRAG?", "target_term": "GraphRAG"},
    {"query": "What is CRAG?", "target_term": "CRAG"},
    {"query": "What is RAPTOR?", "target_term": "RAPTOR"},
    {"query": "What is Agentic RAG?", "target_term": "Agentic RAG"},
    {"query": "What is HyDE?", "target_term": "HyDE"},
    {"query": "How does Self-RAG work?", "target_term": "Self-RAG"},
]


def contains_target(text: str, target: str) -> bool:
    return bool(re.search(r"\b" + re.escape(target) + r"\b", text, re.IGNORECASE) or target.lower() in text.lower())


async def evaluate_concept_retrieval() -> List[Dict[str, Any]]:
    results = []
    
    async with AsyncSessionLocal() as session:
        pipeline = RetrievalPipeline(session=session)
        
        print("=== RUNNING NAMED CONCEPT RETRIEVAL EVALUATION BENCHMARK ===")
        
        for item in TEST_CONCEPT_QUERIES:
            query = item["query"]
            target = item["target_term"]
            
            # Perform search
            retrieved = await pipeline.search(query=query, top_k=20, top_k_rerank=5)
            diag = pipeline.last_diagnostics
            
            final_chunks = [c for c, _ in retrieved]
            relevant_in_final = [c for c in final_chunks if contains_target(c.text, target)]
            
            # Metrics
            final_k = len(final_chunks)
            precision_at_k = len(relevant_in_final) / final_k if final_k > 0 else 0.0
            
            # MRR (Mean Reciprocal Rank)
            mrr = 0.0
            for rank, chunk in enumerate(final_chunks, 1):
                if contains_target(chunk.text, target):
                    mrr = 1.0 / rank
                    break
            
            # Reranker retention rate
            in_rrf = diag.exact_term_in_rrf if diag else False
            in_final = diag.exact_term_in_final_context if diag else False
            reranker_retention = 1.0 if (in_rrf and in_final) else (0.0 if in_rrf else 1.0)

            res = {
                "query": query,
                "target_term": target,
                "status": diag.status if diag else "UNKNOWN",
                "failure_stage": diag.failure_stage if diag else "UNKNOWN",
                "corpus_has_term": diag.exact_term_in_corpus if diag else False,
                "final_context_has_term": in_final,
                "precision_at_5": round(precision_at_k, 3),
                "mrr": round(mrr, 3),
                "reranker_retention": reranker_retention,
            }
            results.append(res)
            
            print(f"\nQuery: '{query}' | Target: '{target}'")
            print(f"  Status: {res['status']} | Failure Stage: {res['failure_stage']}")
            print(f"  Corpus match: {res['corpus_has_term']} | Final Context match: {res['final_context_has_term']}")
            print(f"  Precision@5: {res['precision_at_5']} | MRR: {res['mrr']}")

    return results


if __name__ == "__main__":
    asyncio.run(evaluate_concept_retrieval())
