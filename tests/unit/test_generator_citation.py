import pytest
from src.generation.generator import AnswerGenerator
from src.generation.llm_provider import BaseLLMProvider


class CustomMockProvider(BaseLLMProvider):
    def __init__(self, mock_response: str):
        self.mock_response = mock_response

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Check system prompt includes methodology and clean citation requirements
        assert "METHODOLOGY" in system_prompt or "methodology" in system_prompt
        assert "### Sources" in system_prompt
        return self.mock_response


def test_generator_with_clean_response():
    mock_resp = (
        "LayerRAG-Bench is an evaluation benchmark [1]. It evaluates cross-layer reliability "
        "by systematically injecting failures into macro-reasoning and micro-matching steps [1].\n\n"
        "### Sources\n\n"
        "[1] \"LayerRAG-Bench\" (arXiv:2607.27353), Chunk 0"
    )
    gen = AnswerGenerator(provider=CustomMockProvider(mock_resp))
    chunks_info = [
        {"paper_id": "2607.27353", "chunk_id": "2607.27353_0", "paper_title": "LayerRAG-Bench", "chunk_index": 0, "text": "LayerRAG-Bench text"}
    ]

    ans = gen.generate_answer("How does LayerRAG-Bench evaluate reliability?", chunks_info)
    assert "[1]" in ans
    assert "### Sources" in ans
    assert "Sources1234" not in ans


def test_generator_insufficient_context():
    gen = AnswerGenerator()
    ans = gen.generate_answer("What is quantum RAG?", [])
    assert ans == "Insufficient context in the indexed paper corpus to answer this question."
