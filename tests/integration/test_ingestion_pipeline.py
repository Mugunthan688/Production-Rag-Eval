import pytest
from src.ingestion.models import PaperMetadata, Chunk


def test_ingestion_models(sample_paper):
    assert sample_paper.id == "2312.00001"
    assert "cs.CL" in sample_paper.categories
