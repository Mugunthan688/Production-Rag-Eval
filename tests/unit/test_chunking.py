from src.ingestion.chunking.fixed import FixedSizeChunker
from src.ingestion.chunking.recursive import RecursiveChunker
from src.ingestion.chunking.semantic import SemanticChunker


def test_fixed_size_chunker(sample_paper):
    chunker = FixedSizeChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk_paper(sample_paper)

    assert len(chunks) > 0
    assert chunks[0].chunking_strategy == "fixed"


def test_recursive_chunker(sample_paper):
    chunker = RecursiveChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk_paper(sample_paper)

    assert len(chunks) > 0
    assert chunks[0].chunking_strategy == "recursive"


def test_semantic_chunker(sample_paper):
    chunker = SemanticChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk_paper(sample_paper)

    assert len(chunks) > 0
    assert chunks[0].chunking_strategy == "semantic"
