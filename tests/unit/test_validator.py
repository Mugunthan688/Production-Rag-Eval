import pytest
from src.generation.validator import ResponseValidator


def test_sanitize_garbage_text():
    raw_garbage = "According to the study [1], LayerRAG-Bench evaluates reliability. Sources123454 papers searche"
    cleaned = ResponseValidator.sanitize_garbage_text(raw_garbage)
    assert "Sources123454" not in cleaned
    assert "papers searche" not in cleaned
    assert "evaluates reliability." in cleaned


def test_normalize_inline_citations():
    raw_text = "LayerRAG-Bench [Paper ID: 2607.27353 | Chunk ID: 2607.27353_0 | Score: 0.9000] measures cross-layer errors."
    chunks_info = [
        {"paper_id": "2607.27353", "chunk_id": "2607.27353_0", "paper_title": "LayerRAG-Bench", "chunk_index": 0}
    ]

    normalized = ResponseValidator.normalize_inline_citations(raw_text, chunks_info)
    assert "[1]" in normalized
    assert "Paper ID: 2607.27353" not in normalized


def test_ensure_sources_section():
    body_text = "LayerRAG-Bench evaluates reliability [1]."
    chunks_info = [
        {"paper_id": "2607.27353", "chunk_id": "2607.27353_0", "paper_title": "LayerRAG-Bench: Evaluating Cross-Layer Reliability", "chunk_index": 0}
    ]

    finalized = ResponseValidator.ensure_sources_section(body_text, chunks_info)
    assert "### Sources" in finalized
    assert '[1] "LayerRAG-Bench: Evaluating Cross-Layer Reliability" (arXiv:2607.27353), Chunk 0' in finalized


def test_validate_and_finalize_api_error_fallback():
    raw_err = "Error: Gemini API key missing."
    chunks_info = [
        {"paper_id": "2607.27353", "chunk_id": "2607.27353_0", "paper_title": "LayerRAG-Bench", "chunk_index": 0, "text": "LayerRAG-Bench evaluates agentic RAG failures across macro and micro layers."}
    ]

    output = ResponseValidator.validate_and_finalize("What is LayerRAG-Bench?", raw_err, chunks_info)
    assert "Error: Gemini API key missing" not in output
    assert "### Sources" in output
    assert "[1]" in output
