from src.retrieval.query_rewriter import QueryRewriter


def test_query_rewriter_fallback():
    rewriter = QueryRewriter(api_key=None)
    queries, exact_terms = rewriter.rewrite_and_decompose("What is RAG?")
    assert queries == ["What is RAG?"]
    assert "RAG" in exact_terms
