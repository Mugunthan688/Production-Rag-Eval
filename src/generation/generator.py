from typing import List, Tuple
from src.db.models import ChunkORM
from src.generation.llm_provider import BaseLLMProvider, get_llm_provider
from src.generation.prompt_templates import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT_TEMPLATE
from config.settings import settings


class AnswerGenerator:
    def __init__(self, provider: BaseLLMProvider | None = None):
        self.provider = provider or get_llm_provider(settings.LLM_PROVIDER)

    def generate_answer(self, query: str, chunks: List[Tuple[ChunkORM, float]]) -> str:
        if not chunks:
            return "Insufficient context in the indexed paper corpus to answer this question."

        context_blocks = []
        for idx, (chunk, score) in enumerate(chunks):
            paper_id = chunk.paper_id
            block = f"--- [Paper ID: {paper_id} | Chunk ID: {chunk.id} | Score: {score:.4f}] ---\n{chunk.text}\n"
            context_blocks.append(block)

        formatted_context = "\n".join(context_blocks)
        user_prompt = RAG_USER_PROMPT_TEMPLATE.format(context_blocks=formatted_context, query=query)

        raw_answer = self.provider.generate(system_prompt=RAG_SYSTEM_PROMPT, user_prompt=user_prompt)

        if "Error:" in raw_answer or "API key missing" in raw_answer:
            # Fallback local synthesis without requiring paid API keys
            top_chunk, top_score = chunks[0]
            summary_lines = []
            for chunk, score in chunks[:3]:
                paper_id = chunk.paper_id
                snippet = chunk.text[:250].strip().replace("\n", " ")
                summary_lines.append(f"- According to **Paper [{paper_id}]** (Relevance Score: {score:.2f}): \"{snippet}...\"")
            
            synthesis = "\n\n".join(summary_lines)
            return f"**Synthesized Context Answer**:\n\n{synthesis}"

        return raw_answer
