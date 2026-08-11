from typing import List, Tuple, Dict, Any, Union
from src.db.models import ChunkORM
from src.generation.llm_provider import BaseLLMProvider, get_llm_provider
from src.generation.prompt_templates import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT_TEMPLATE
from src.generation.validator import ResponseValidator
from config.settings import settings


class AnswerGenerator:
    """Generates grounded, methodology-focused research answers with clean citations and validation."""

    def __init__(self, provider: BaseLLMProvider | None = None):
        self.provider = provider or get_llm_provider(settings.LLM_PROVIDER)

    def generate_answer(
        self,
        query: str,
        chunks: Union[List[Tuple[ChunkORM, float]], List[Dict[str, Any]]],
    ) -> str:
        if not chunks:
            return "Insufficient context in the indexed paper corpus to answer this question."

        # Standardize chunks into enriched dictionaries
        chunks_info: List[Dict[str, Any]] = []
        for idx, item in enumerate(chunks, 1):
            if isinstance(item, tuple):
                chunk_obj, score = item
                paper = getattr(chunk_obj, "paper", None)
                chunks_info.append(
                    {
                        "chunk_id": getattr(chunk_obj, "id", f"c_{idx}"),
                        "paper_id": getattr(chunk_obj, "paper_id", f"p_{idx}"),
                        "chunk_index": getattr(chunk_obj, "chunk_index", 0),
                        "score": score,
                        "text": getattr(chunk_obj, "text", ""),
                        "paper_title": getattr(paper, "title", "arXiv Paper") if paper else "arXiv Paper",
                        "paper_authors": getattr(paper, "authors", []) if paper else [],
                    }
                )
            elif isinstance(item, dict):
                chunks_info.append(item)

        # Format context blocks cleanly as [Source 1], [Source 2] for the LLM
        context_blocks = []
        for idx, c in enumerate(chunks_info, 1):
            title = c.get("paper_title") or "arXiv Paper"
            paper_id = c.get("paper_id") or "Unknown"
            chunk_idx = c.get("chunk_index", 0)
            text = c.get("text", "").strip()

            header = f"[Source {idx}] Title: \"{title}\" | arXiv ID: {paper_id} | Chunk Index: {chunk_idx}"
            context_blocks.append(f"{header}\nExcerpts:\n{text}\n")

        formatted_context = "\n".join(context_blocks)
        user_prompt = RAG_USER_PROMPT_TEMPLATE.format(context_blocks=formatted_context, query=query)

        # Call LLM provider
        raw_answer = self.provider.generate(system_prompt=RAG_SYSTEM_PROMPT, user_prompt=user_prompt)

        # Run ResponseValidator to clean, normalize citations, and finalize output
        final_answer = ResponseValidator.validate_and_finalize(
            query=query, raw_answer=raw_answer, chunks_info=chunks_info
        )

        return final_answer
