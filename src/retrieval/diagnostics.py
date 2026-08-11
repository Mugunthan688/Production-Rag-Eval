import logging
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

STATUS_SUCCESS = "SUCCESS"
STATUS_RETRIEVAL_FAILURE = "RETRIEVAL_FAILURE"
STATUS_CORPUS_MISSING_INFO = "CORPUS_MISSING_INFORMATION"


@dataclass
class RetrievalDiagnostics:
    query: str
    expanded_queries: List[str] = field(default_factory=list)
    exact_terms_checked: List[str] = field(default_factory=list)
    exact_term_in_corpus: bool = False
    
    # Candidate counts per stage
    vector_candidates_count: int = 0
    bm25_candidates_count: int = 0
    rrf_fused_count: int = 0
    reranked_count: int = 0
    
    # Target term presence per stage
    exact_term_in_vector: bool = False
    exact_term_in_bm25: bool = False
    exact_term_in_rrf: bool = False
    exact_term_in_reranked: bool = False
    exact_term_in_final_context: bool = False
    
    # Final classification
    status: str = STATUS_SUCCESS
    failure_stage: str = "none"  # "none", "vector", "bm25", "rrf_fusion", "reranking", "context_construction"
    
    def classify(self, final_chunks_texts: List[str]):
        """Classify retrieval status and identify exact failure stage."""
        # Check if exact term is in final context
        self.exact_term_in_final_context = False
        for text in final_chunks_texts:
            for term in self.exact_terms_checked:
                if re.search(r"\b" + re.escape(term) + r"\b", text, re.IGNORECASE):
                    self.exact_term_in_final_context = True
                    break

        if not self.exact_term_in_corpus:
            self.status = STATUS_CORPUS_MISSING_INFO
            self.failure_stage = "corpus_missing"
            return

        if self.exact_term_in_final_context:
            self.status = STATUS_SUCCESS
            self.failure_stage = "none"
            return

        # Evidence exists in corpus, but was lost before final context -> RETRIEVAL_FAILURE
        self.status = STATUS_RETRIEVAL_FAILURE

        if not self.exact_term_in_vector and not self.exact_term_in_bm25:
            self.failure_stage = "initial_retrieval"
        elif not self.exact_term_in_rrf:
            self.failure_stage = "rrf_fusion"
        elif not self.exact_term_in_reranked:
            self.failure_stage = "reranking"
        else:
            self.failure_stage = "context_construction"

    def to_report_string(self) -> str:
        """Development/debugging report string (not shown to end users)."""
        terms_str = ", ".join(self.exact_terms_checked) if self.exact_terms_checked else "None"
        report = (
            f"\n--- RETRIEVAL DIAGNOSTIC REPORT ---\n"
            f"Query: {self.query}\n"
            f"Terms Analyzed: [{terms_str}]\n"
            f"Status: {self.status}\n"
            f"Failure Stage: {self.failure_stage}\n"
            f"Corpus Contains Term: {'FOUND' if self.exact_term_in_corpus else 'NOT FOUND'}\n"
            f"Vector Stage: {'FOUND' if self.exact_term_in_vector else 'NOT FOUND'} ({self.vector_candidates_count} candidates)\n"
            f"BM25 Stage: {'FOUND' if self.exact_term_in_bm25 else 'NOT FOUND'} ({self.bm25_candidates_count} candidates)\n"
            f"RRF Fusion Stage: {'FOUND' if self.exact_term_in_rrf else 'NOT FOUND'} ({self.rrf_fused_count} candidates)\n"
            f"Reranked Stage: {'FOUND' if self.exact_term_in_reranked else 'NOT FOUND'} ({self.reranked_count} candidates)\n"
            f"Final Context Stage: {'FOUND' if self.exact_term_in_final_context else 'NOT FOUND'}\n"
            f"------------------------------------\n"
        )
        return report

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "status": self.status,
            "failure_stage": self.failure_stage,
            "exact_term_in_corpus": self.exact_term_in_corpus,
            "exact_term_in_vector": self.exact_term_in_vector,
            "exact_term_in_bm25": self.exact_term_in_bm25,
            "exact_term_in_rrf": self.exact_term_in_rrf,
            "exact_term_in_reranked": self.exact_term_in_reranked,
            "exact_term_in_final_context": self.exact_term_in_final_context,
            "exact_terms_checked": self.exact_terms_checked,
            "expanded_queries": self.expanded_queries,
        }
