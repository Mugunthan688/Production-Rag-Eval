from src.retrieval.query_rewriter import QueryRewriter


def test_query_rewriter_fallback():
    rewriter = QueryRewriter(api_key=None)
    res = rewriter.rewrite_and_decompose("What is RAG?")
    assert res == ["What is RAG?"]
