from src.retrieval.reranker import CrossEncoderReranker


def test_reranker_empty():
    reranker = CrossEncoderReranker()
    res = reranker.rerank("query", [])
    assert res == []
