import asyncio
import json
import re
from src.db.engine import AsyncSessionLocal
from src.generation.pipeline import GenerationPipeline

TARGET_QUERIES = [
    "What is Self-RAG and how does it work?",
    "How does GraphRAG improve retrieval?",
    "How do knowledge graphs enhance RAG?",
    "What is LayerRAG-Bench and how does it evaluate cross-layer reliability in agentic RAG systems?",
    "What is DualG-MRAG and how does it decouple macro-reasoning from micro-matching in multimodal RAG?",
]

async def run_5_query_benchmark():
    print("\n==================================================")
    print("STARTING 5-QUERY TARGET VERIFICATION SUITE")
    print("==================================================\n")

    results = []

    async with AsyncSessionLocal() as session:
        pipeline = GenerationPipeline(session)

        for i, q in enumerate(TARGET_QUERIES, 1):
            print(f"\n--------------------------------------------------")
            print(f"TEST {i}/5: {q}")
            print(f"--------------------------------------------------")

            response_data = await pipeline.answer_query(q)
            answer_text = response_data.get("answer", "")
            diagnostics = response_data.get("retrieval_diagnostics", {})

            # 1. Validate bidirectional citation integrity
            sources_match = re.search(r"###\s*Sources\b", answer_text, flags=re.IGNORECASE)
            if sources_match:
                body_text = answer_text[:sources_match.start()]
                sources_text = answer_text[sources_match.start():]
            else:
                body_text = answer_text
                sources_text = ""

            used_citations = set(re.findall(r"\[(\d+)\]", body_text))
            defined_sources = set(re.findall(r"^\[(\d+)\]", sources_text, flags=re.MULTILINE))

            citation_valid = (used_citations == defined_sources) if defined_sources else False

            print("\n[RETRIEVAL DIAGNOSTICS]:")
            print(f"Status: {diagnostics.get('status')}")
            print(f"Failure Stage: {diagnostics.get('failure_stage')}")
            print(f"Exact Terms Checked: {diagnostics.get('exact_terms_checked')}")
            print(f"Exact Term in Final Context: {diagnostics.get('exact_term_in_final_context')}")

            print("\n[CITATION INTEGRITY]:")
            print(f"Used Citations in Body: {sorted([int(x) for x in used_citations])}")
            print(f"Defined Sources in List: {sorted([int(x) for x in defined_sources])}")
            print(f"Bidirectional Match (USED == DEFINED): {citation_valid}")

            print("\n[GENERATED ANSWER]:")
            print(answer_text)

            results.append({
                "query": q,
                "diagnostics": diagnostics,
                "citation_valid": citation_valid,
                "used_citations": list(used_citations),
                "defined_sources": list(defined_sources),
                "answer_length": len(answer_text),
            })

    print("\n==================================================")
    print("5-QUERY TARGET SUITE COMPLETE")
    print(f"All 5 Queries Handled: {len(results) == 5}")
    print(f"All Citation Integrities Valid: {all(r['citation_valid'] for r in results)}")
    print("==================================================\n")

if __name__ == "__main__":
    asyncio.run(run_5_query_benchmark())
