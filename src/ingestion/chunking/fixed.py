from typing import List
from ..models import PaperMetadata, Chunk
from .base import BaseChunker


class FixedSizeChunker(BaseChunker):
    """Fixed-size character/word window chunker with configurable overlap."""

    def chunk_paper(self, paper: PaperMetadata) -> List[Chunk]:
        content = paper.full_text if paper.full_text else f"{paper.title}\n\n{paper.abstract}"
        chunks: List[Chunk] = []

        if len(content) <= self.chunk_size:
            return [
                Chunk(
                    id=f"{paper.id}_chunk_0",
                    paper_id=paper.id,
                    chunk_index=0,
                    text=content,
                    chunking_strategy="fixed",
                    metadata={
                        "title": paper.title,
                        "categories": paper.categories,
                        "authors": paper.authors,
                    },
                )
            ]

        start = 0
        idx = 0
        step = self.chunk_size - self.chunk_overlap
        while start < len(content):
            end = start + self.chunk_size
            chunk_text = content[start:end]
            chunks.append(
                Chunk(
                    id=f"{paper.id}_chunk_{idx}",
                    paper_id=paper.id,
                    chunk_index=idx,
                    text=chunk_text,
                    chunking_strategy="fixed",
                    metadata={
                        "title": paper.title,
                        "categories": paper.categories,
                        "authors": paper.authors,
                    },
                )
            )
            idx += 1
            start += step

        return chunks
