from typing import List
from ..models import PaperMetadata, Chunk
from .base import BaseChunker


class RecursiveChunker(BaseChunker):
    """Structure-aware recursive text splitter using custom split hierarchy."""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: List[str] | None = None,
    ):
        super().__init__(chunk_size, chunk_overlap)
        self.separators = separators or ["\n\n", "\n", ". ", " "]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        if not separators or len(text) <= self.chunk_size:
            return [text] if text else []

        sep = separators[0]
        new_separators = separators[1:]
        splits = text.split(sep)
        final_chunks = []
        current_chunk = ""

        for s in splits:
            item = s + sep if sep != " " else s + " "
            if len(current_chunk) + len(item) <= self.chunk_size:
                current_chunk += item
            else:
                if current_chunk:
                    final_chunks.append(current_chunk.strip())
                if len(item) > self.chunk_size and new_separators:
                    final_chunks.extend(self._split_text(item, new_separators))
                    current_chunk = ""
                else:
                    current_chunk = item

        if current_chunk:
            final_chunks.append(current_chunk.strip())

        return final_chunks

    def chunk_paper(self, paper: PaperMetadata) -> List[Chunk]:
        content = paper.full_text if paper.full_text else f"{paper.title}\n\n{paper.abstract}"
        raw_chunks = self._split_text(content, self.separators)

        return [
            Chunk(
                id=f"{paper.id}_chunk_{i}",
                paper_id=paper.id,
                chunk_index=i,
                text=chunk_str,
                chunking_strategy="recursive",
                metadata={
                    "title": paper.title,
                    "categories": paper.categories,
                    "authors": paper.authors,
                },
            )
            for i, chunk_str in enumerate(raw_chunks)
        ]
