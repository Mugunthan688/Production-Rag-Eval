"""Chunking strategies module."""
from src.ingestion.chunking.base import BaseChunker
from src.ingestion.chunking.factory import get_chunker

__all__ = ["BaseChunker", "get_chunker"]
