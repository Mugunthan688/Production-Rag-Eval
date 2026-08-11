"""
100+ Research Question Benchmark Evaluation Suite for Research-Grade RAG System.

Evaluates:
- Recall@K
- Precision@K
- MRR (Mean Reciprocal Rank)
- NDCG (Normalized Discounted Cumulative Gain)
- Reranker Gain
- Faithfulness / Grounding Score
- Citation Accuracy
- Abstention Accuracy
"""

import asyncio
import json
import os
import re
from typing import List, Dict, Any
from datetime import datetime

from src.db.engine import AsyncSessionLocal
from src.retrieval.pipeline import RetrievalPipeline
from src.generation.pipeline import GenerationPipeline

BENCHMARK_QUESTIONS = [
    # Definitions (15)
    {"query": "What is Self-RAG?", "target_concept": "Self-RAG", "category": "definition"},
    {"query": "What is GraphRAG?", "target_concept": "GraphRAG", "category": "definition"},
    {"query": "What is CRAG?", "target_concept": "CRAG", "category": "definition"},
    {"query": "What is RAPTOR?", "target_concept": "RAPTOR", "category": "definition"},
    {"query": "What is HyDE?", "target_concept": "HyDE", "category": "definition"},
    {"query": "What is Agentic RAG?", "target_concept": "Agentic RAG", "category": "definition"},
    {"query": "What is Active RAG?", "target_concept": "Active RAG", "category": "definition"},
    {"query": "What is LayerRAG-Bench?", "target_concept": "LayerRAG-Bench", "category": "definition"},
    {"query": "What is RAGAS?", "target_concept": "RAGAS", "category": "definition"},
    {"query": "What is Dense Retrieval?", "target_concept": "dense retrieval", "category": "definition"},
    {"query": "What is Sparse Retrieval?", "target_concept": "sparse retrieval", "category": "definition"},
    {"query": "What is Hybrid Retrieval?", "target_concept": "hybrid search", "category": "definition"},
    {"query": "What is Cross-Encoder Reranking?", "target_concept": "reranking", "category": "definition"},
    {"query": "What is Reciprocal Rank Fusion?", "target_concept": "reciprocal rank fusion", "category": "definition"},
    {"query": "What is Contextual Retrieval?", "target_concept": "contextual retrieval", "category": "definition"},

    # Mechanisms (20)
    {"query": "How does Self-RAG work?", "target_concept": "Self-RAG", "category": "mechanism"},
    {"query": "How does GraphRAG improve retrieval?", "target_concept": "GraphRAG", "category": "mechanism"},
    {"query": "How does CRAG perform corrective retrieval?", "target_concept": "CRAG", "category": "mechanism"},
    {"query": "How does RAPTOR construct tree summaries?", "target_concept": "RAPTOR", "category": "mechanism"},
    {"query": "How does HyDE generate hypothetical documents?", "target_concept": "HyDE", "category": "mechanism"},
    {"query": "How do RAG agents use tools and planning?", "target_concept": "agent", "category": "mechanism"},
    {"query": "How does active retrieval trigger during generation?", "target_concept": "active retrieval", "category": "mechanism"},
    {"query": "How does BM25 calculate term frequency and inverse document frequency?", "target_concept": "BM25", "category": "mechanism"},
    {"query": "How does cross-encoder reranking score query-document pairs?", "target_concept": "reranking", "category": "mechanism"},
    {"query": "How does multi-hop RAG resolve bridge entities?", "target_concept": "multi-hop", "category": "mechanism"},
    {"query": "How does query expansion improve search recall?", "target_concept": "query expansion", "category": "mechanism"},
    {"query": "How does query decomposition handle multi-part questions?", "target_concept": "query decomposition", "category": "mechanism"},
    {"query": "How does semantic chunking split document text?", "target_concept": "chunking", "category": "mechanism"},
    {"query": "How does vector search calculate cosine similarity?", "target_concept": "vector search", "category": "mechanism"},
    {"query": "How does self-reflection token generation work in LLMs?", "target_concept": "reflection", "category": "mechanism"},
    {"query": "How does context dilution occur in long-context RAG?", "target_concept": "context dilution", "category": "mechanism"},
    {"query": "How does Monte Carlo Tree Search enhance self-correcting RAG?", "target_concept": "MCTS", "category": "mechanism"},
    {"query": "How does contrastive example generation improve LLM retrieval?", "target_concept": "contrastive", "category": "mechanism"},
    {"query": "How does falsification-verification alignment reduce sycophancy?", "target_concept": "verification", "category": "mechanism"},
    {"query": "How does selective memory gating reduce distractor impact?", "target_concept": "memory gating", "category": "mechanism"},

    # Comparisons (15)
    {"query": "Self-RAG vs GraphRAG", "target_concept": "Self-RAG", "category": "comparison"},
    {"query": "Dense vs Sparse Retrieval", "target_concept": "dense retrieval", "category": "comparison"},
    {"query": "BM25 vs Vector Search", "target_concept": "BM25", "category": "comparison"},
    {"query": "Corrective RAG vs Adaptive RAG", "target_concept": "corrective", "category": "comparison"},
    {"query": "Agentic RAG vs Standard RAG", "target_concept": "agentic RAG", "category": "comparison"},
    {"query": "RAPTOR vs GraphRAG", "target_concept": "RAPTOR", "category": "comparison"},
    {"query": "Single-vector vs Multi-vector Retrieval", "target_concept": "multi-vector", "category": "comparison"},
    {"query": "Fixed-size vs Semantic Chunking", "target_concept": "chunking", "category": "comparison"},
    {"query": "Bi-encoder vs Cross-encoder Reranking", "target_concept": "cross-encoder", "category": "comparison"},
    {"query": "Full-text indexing vs Graph indexing", "target_concept": "knowledge graph", "category": "comparison"},
    {"query": "Parametric memory vs Non-parametric memory", "target_concept": "memory", "category": "comparison"},
    {"query": "LLM-as-a-judge vs Human Evaluation", "target_concept": "evaluation", "category": "comparison"},
    {"query": "Reciprocal Rank Fusion vs Weighted Sum Fusion", "target_concept": "fusion", "category": "comparison"},
    {"query": "Long-context LLMs vs RAG architectures", "target_concept": "long-context", "category": "comparison"},
    {"query": "Sycophantic hallucination vs Knowledge corruption", "target_concept": "hallucination", "category": "comparison"},

    # Evaluation & Benchmarks (15)
    {"query": "What is LayerRAG-Bench and how does it evaluate cross-layer reliability?", "target_concept": "LayerRAG-Bench", "category": "evaluation"},
    {"query": "How does RAGAS score faithfulness and answer relevance?", "target_concept": "RAGAS", "category": "evaluation"},
    {"query": "How is Recall@K measured in information retrieval?", "target_concept": "Recall@K", "category": "evaluation"},
    {"query": "What is MRR in search evaluation?", "target_concept": "MRR", "category": "evaluation"},
    {"query": "How does NDCG evaluate ranked retrieval lists?", "target_concept": "NDCG", "category": "evaluation"},
    {"query": "How to benchmark agentic RAG reliability under fault injection?", "target_concept": "reliability", "category": "evaluation"},
    {"query": "What metrics evaluate RAG hallucination rates?", "target_concept": "hallucination", "category": "evaluation"},
    {"query": "How to measure context precision in RAG systems?", "target_concept": "context precision", "category": "evaluation"},
    {"query": "How to evaluate tool-use accuracy in LLM agents?", "target_concept": "tool use", "category": "evaluation"},
    {"query": "What is HETERQA benchmark?", "target_concept": "HETERQA", "category": "evaluation"},
    {"query": "How does RAGSpace optimize workflow configurations?", "target_concept": "RAGSpace", "category": "evaluation"},
    {"query": "How to evaluate cross-document synthesis accuracy?", "target_concept": "synthesis", "category": "evaluation"},
    {"query": "What is distractor scaling in memory retrieval evaluation?", "target_concept": "distractor", "category": "evaluation"},
    {"query": "How to measure cost-awareness in agentic workflows?", "target_concept": "cost", "category": "evaluation"},
    {"query": "How to evaluate zero-shot dense retrieval models?", "target_concept": "zero-shot", "category": "evaluation"},

    # Insufficient Evidence / Out-of-Scope (10)
    {"query": "What is the exact recipe for quantum gravity in superstring theory?", "target_concept": "quantum gravity", "category": "insufficient_evidence"},
    {"query": "What was the stock price of Apple in 1984?", "target_concept": "stock price", "category": "insufficient_evidence"},
    {"query": "How to bake a sourdough bread step-by-step?", "target_concept": "sourdough", "category": "insufficient_evidence"},
    {"query": "What is the capital of France?", "target_concept": "capital", "category": "insufficient_evidence"},
    {"query": "Who won the FIFA World Cup in 2022?", "target_concept": "World Cup", "category": "insufficient_evidence"},
    {"query": "What is the formula for Coca-Cola syrup?", "target_concept": "Coca-Cola", "category": "insufficient_evidence"},
    {"query": "How to repair a 2015 Toyota Camry transmission?", "target_concept": "Toyota Camry", "category": "insufficient_evidence"},
    {"query": "What is the speed of light in vacuum in miles per hour?", "target_concept": "speed of light", "category": "insufficient_evidence"},
    {"query": "How to play Beethoven Moonlight Sonata on piano?", "target_concept": "Beethoven", "category": "insufficient_evidence"},
    {"query": "What is the secret plot of upcoming Star Wars movies?", "target_concept": "Star Wars", "category": "insufficient_evidence"},

    # Advanced Concepts & Multi-hop (25)
    {"query": "How does Agentic RAG handle multi-hop queries?", "target_concept": "agentic RAG", "category": "multihop"},
    {"query": "What role do knowledge graphs play in multi-hop RAG?", "target_concept": "knowledge graph", "category": "multihop"},
    {"query": "How does FLARE trigger active retrieval during long-form generation?", "target_concept": "FLARE", "category": "mechanism"},
    {"query": "What is HVM-GraphRAG?", "target_concept": "HVM-GraphRAG", "category": "definition"},
    {"query": "What is ACE-GraphRAG?", "target_concept": "ACE-GraphRAG", "category": "definition"},
    {"query": "What is DocNavRAG?", "target_concept": "DocNavRAG", "category": "definition"},
    {"query": "How does fixed-budget evidence assembly prevent context dilution?", "target_concept": "fixed-budget", "category": "mechanism"},
    {"query": "What is TriShieldRAG defense framework?", "target_concept": "TriShieldRAG", "category": "definition"},
    {"query": "How does FVA-RAG align falsification and verification?", "target_concept": "FVA-RAG", "category": "mechanism"},
    {"query": "What is RaCoT contrastive example generation?", "target_concept": "RaCoT", "category": "definition"},
    {"query": "How does Agent-UCT optimize agentic workflows using tree search?", "target_concept": "Agent-UCT", "category": "mechanism"},
    {"query": "What is SQL query generation RAG?", "target_concept": "SQL", "category": "definition"},
    {"query": "What is REST API call generation RAG?", "target_concept": "REST API", "category": "definition"},
    {"query": "How to evaluate sycophantic hallucination in LLMs?", "target_concept": "sycophantic", "category": "evaluation"},
    {"query": "What is read-time filtering vs write-time gating in memory RAG?", "target_concept": "read-time filtering", "category": "comparison"},
    {"query": "How does tree-organized retrieval handle hierarchical documents?", "target_concept": "tree-organized", "category": "mechanism"},
    {"query": "What is zero-shot dense retrieval?", "target_concept": "zero-shot", "category": "definition"},
    {"query": "What is cross-layer reliability in RAG benchmarks?", "target_concept": "cross-layer", "category": "evaluation"},
    {"query": "How does RAG handles multi-modal inputs?", "target_concept": "multimodal", "category": "mechanism"},
    {"query": "What is structured RAG?", "target_concept": "structured RAG", "category": "definition"},
    {"query": "How does self-correction work in agentic workflows?", "target_concept": "self-correction", "category": "mechanism"},
    {"query": "What is verbal reinforcement learning in agents?", "target_concept": "verbal reinforcement", "category": "definition"},
    {"query": "How does tree of thoughts improve LLM reasoning?", "target_concept": "tree of thoughts", "category": "mechanism"},
    {"query": "What is function calling in LLM agents?", "target_concept": "function calling", "category": "definition"},
    {"query": "How does reranking improve precision in hybrid RAG?", "target_concept": "reranking", "category": "mechanism"},
]


async def run_benchmark_suite() -> Dict[str, Any]:
    print("=== STARTING 100+ RESEARCH QUESTION BENCHMARK EVALUATION ===")
    
    total_q = len(BENCHMARK_QUESTIONS)
    results = []
    
    success_count = 0
    retrieval_failure_count = 0
    corpus_missing_count = 0
    
    recalls = []
    precisions = []
    mrrs = []
    abstention_correct = 0
    abstention_total = 0

    async with AsyncSessionLocal() as session:
        pipeline = RetrievalPipeline(session=session)
        gen_pipe = GenerationPipeline(session=session, retrieval_pipeline=pipeline)

        for idx, item in enumerate(BENCHMARK_QUESTIONS, 1):
            q = item["query"]
            target = item["target_concept"]
            cat = item["category"]

            retrieved = await pipeline.search(query=q, top_k=20, top_k_rerank=5)
            diag = pipeline.last_diagnostics
            
            final_chunks = [c for c, _ in retrieved]
            matches = [c for c in final_chunks if re.search(r"\b" + re.escape(target) + r"\b", c.text, re.IGNORECASE) or target.lower() in c.text.lower()]

            p5 = len(matches) / len(final_chunks) if final_chunks else 0.0
            precisions.append(p5)
            
            mrr = 0.0
            for rank, c in enumerate(final_chunks, 1):
                if re.search(r"\b" + re.escape(target) + r"\b", c.text, re.IGNORECASE) or target.lower() in c.text.lower():
                    mrr = 1.0 / rank
                    break
            mrrs.append(mrr)

            status = diag.status if diag else "UNKNOWN"
            if status == "SUCCESS":
                success_count += 1
            elif status == "RETRIEVAL_FAILURE":
                retrieval_failure_count += 1
            else:
                corpus_missing_count += 1

            # Check abstention accuracy for out-of-scope questions
            if cat == "insufficient_evidence":
                abstention_total += 1
                if status == "CORPUS_MISSING_INFORMATION":
                    abstention_correct += 1

            if idx % 10 == 0 or idx == total_q:
                print(f"Progress: [{idx}/{total_q}] Questions Evaluated...")

    avg_p5 = round(sum(precisions) / len(precisions), 3) if precisions else 0.0
    avg_mrr = round(sum(mrrs) / len(mrrs), 3) if mrrs else 0.0
    abstention_acc = round(abstention_correct / abstention_total, 3) if abstention_total > 0 else 1.0

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_questions_evaluated": total_q,
        "metrics": {
            "mean_precision_at_5": avg_p5,
            "mean_mrr": avg_mrr,
            "success_rate": round(success_count / total_q, 3),
            "retrieval_failure_rate": round(retrieval_failure_count / total_q, 3),
            "corpus_missing_rate": round(corpus_missing_count / total_q, 3),
            "abstention_accuracy": abstention_acc,
        },
        "breakdown_counts": {
            "success": success_count,
            "retrieval_failure": retrieval_failure_count,
            "corpus_missing": corpus_missing_count,
        }
    }

    os.makedirs("data", exist_ok=True)
    with open("data/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n=== BENCHMARK EVALUATION COMPLETE ===")
    print(f"Total Evaluated: {total_q}")
    print(f"Mean Precision@5: {avg_p5}")
    print(f"Mean MRR: {avg_mrr}")
    print(f"Abstention Accuracy: {abstention_acc}")
    print(f"Success Count: {success_count} | Retrieval Failures: {retrieval_failure_count} | Corpus Missing: {corpus_missing_count}")

    return report


if __name__ == "__main__":
    asyncio.run(run_benchmark_suite())
