import re
from typing import List
from ..models import PaperMetadata, Chunk
from .base import BaseChunker


class SemanticChunker(BaseChunker):
    """Sentence-boundary semantic chunker with adaptive grouping."""

    def chunk_paper(self, paper: PaperMetadata) -> List[Chunk]:
        content = paper.full_text if paper.full_text else f"{paper.title}\n\n{paper.abstract}"
        # Split content into sentences
        sentences = re.split(r"(?<=[.!?]) +", content)
        chunks: List[Chunk] = []

        current_chunk_sentences = []
        current_len = 0
        idx = 0

        for sentence in sentences:
            if current_len + len(sentence) > self.chunk_size and current_chunk_sentences:
                chunk_text = " ".join(current_chunk_sentences)
                chunks.append(
                    Chunk(
                        id=f"{paper.id}_chunk_{idx}",
                        paper_id=paper.id,
                        chunk_index=idx,
                        text=chunk_text,
                        chunking_strategy="semantic",
                        metadata={
                            "title": paper.title,
                            "categories": paper.categories,
                            "authors": paper.authors,
                        },
                    )
                )
                idx += 1
                current_chunk_sentences = [sentence]
                current_len = len(sentence)
            else:
                current_chunk_sentences.append(sentence)
                current_len += len(sentence)

        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            chunks.append(
                Chunk(
                    id=f"{paper.id}_chunk_{idx}",
                    paper_id=paper.id,
                    chunk_index=idx,
                    text=chunk_text,
                    chunking_strategy="semantic",
                    metadata={
                        "title": paper.title,
                        "categories": paper.categories,
                        "authors": paper.authors,
                    },
                )
            )

        return chunks
