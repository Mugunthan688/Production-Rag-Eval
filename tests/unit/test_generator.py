from src.generation.generator import AnswerGenerator
from src.generation.llm_provider import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        return "Mocked RAG Answer with citation [Paper 2312.00001]."


def test_generator():
    gen = AnswerGenerator(provider=MockLLMProvider())
    ans = gen.generate_answer("What is RAG?", [])
    assert ans == "Insufficient context in the indexed paper corpus to answer this question."
