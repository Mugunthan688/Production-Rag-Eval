from .base import BaseChunker
from .fixed import FixedSizeChunker
from .recursive import RecursiveChunker
from .semantic import SemanticChunker


def get_chunker(
    strategy: str = "recursive", chunk_size: int = 500, chunk_overlap: int = 50
) -> BaseChunker:
    strategy_lower = strategy.lower()
    if strategy_lower == "fixed":
        return FixedSizeChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif strategy_lower == "recursive":
        return RecursiveChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif strategy_lower == "semantic":
        return SemanticChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    else:
        raise ValueError(f"Unknown chunking strategy: '{strategy}'. Supported: fixed, recursive, semantic.")
