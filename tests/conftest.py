import pytest
from datetime import datetime
from src.ingestion.models import PaperMetadata, Chunk


@pytest.fixture
def sample_paper():
    return PaperMetadata(
        id="2312.00001",
        title="Retrieval-Augmented Generation for Large Language Models: A Survey",
        abstract="Retrieval-Augmented Generation (RAG) enhances LLMs by retrieving relevant documents from external knowledge bases. This paper provides a comprehensive survey of RAG techniques, architectures, and evaluation methods.",
        authors=["Yunfan Gao", "Yun Xiong", "Xinyu Gao"],
        categories=["cs.CL", "cs.AI"],
        submitted_date=datetime(2023, 12, 1),
        pdf_url="https://arxiv.org/pdf/2312.00001.pdf",
    )


@pytest.fixture
def sample_chunks(sample_paper):
    return [
        Chunk(
            id="2312.00001_chunk_0",
            paper_id=sample_paper.id,
            chunk_index=0,
            text=sample_paper.abstract,
            chunking_strategy="recursive",
            embedding=[0.1] * 1536,
            metadata={"title": sample_paper.title},
        )
    ]
