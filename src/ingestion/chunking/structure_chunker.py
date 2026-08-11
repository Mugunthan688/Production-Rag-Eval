import re
from typing import List
from .base import BaseChunker
from ..models import PaperMetadata, Chunk


class StructureAwareChunker(BaseChunker):
    """
    Structure-aware chunker that splits papers along section and paragraph boundaries,
    prefixing section context to maintain independent chunk coherence.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.section_headers = [
            "abstract", "introduction", "methodology", "method", "proposed method",
            "system architecture", "retrieval mechanism", "evaluation", "experiments",
            "results", "related work", "discussion", "conclusion"
        ]

    def _split_into_sections(self, text: str) -> List[tuple[str, str]]:
        """Splits full text into (section_header, section_content) pairs."""
        lines = text.split("\n")
        sections: List[tuple[str, str]] = []
        current_header = "Abstract / Core Overview"
        current_lines: List[str] = []

        for line in lines:
            line_clean = line.strip()
            line_lower = line_clean.lower()

            # Check if line matches a section heading
            is_header = any(
                re.match(r"^(?:\d+\.?\s*)?" + re.escape(h) + r"\b", line_lower)
                for h in self.section_headers
            )

            if is_header and current_lines:
                sections.append((current_header, "\n".join(current_lines).strip()))
                current_header = line_clean
                current_lines = []
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_header, "\n".join(current_lines).strip()))

        return sections

    def chunk_paper(self, paper: PaperMetadata) -> List[Chunk]:
        text_to_chunk = paper.full_text if (paper.full_text and len(paper.full_text) > len(paper.abstract)) else f"Abstract: {paper.abstract}"
        sections = self._split_into_sections(text_to_chunk)

        chunks: List[Chunk] = []
        chunk_idx = 0

        for sec_header, sec_content in sections:
            if not sec_content:
                continue

            # Split section into paragraphs
            paragraphs = [p.strip() for p in sec_content.split("\n\n") if p.strip()]
            current_buffer = ""

            for para in paragraphs:
                if len(current_buffer) + len(para) <= self.chunk_size:
                    current_buffer += ("\n\n" if current_buffer else "") + para
                else:
                    if current_buffer:
                        full_chunk_text = f"[Section: {sec_header}]\n{current_buffer}"
                        chunks.append(
                            Chunk(
                                id=f"{paper.id}_struct_{chunk_idx}",
                                paper_id=paper.id,
                                chunk_index=chunk_idx,
                                text=full_chunk_text,
                                chunking_strategy="structure",
                                metadata={
                                    "section_name": sec_header,
                                    "chunk_index": chunk_idx,
                                    "paper_id": paper.id,
                                },
                            )
                        )
                        chunk_idx += 1
                        # Maintain overlap
                        current_buffer = current_buffer[-self.chunk_overlap :] + "\n\n" + para if self.chunk_overlap < len(current_buffer) else para
                    else:
                        current_buffer = para

            if current_buffer:
                full_chunk_text = f"[Section: {sec_header}]\n{current_buffer}"
                chunks.append(
                    Chunk(
                        id=f"{paper.id}_struct_{chunk_idx}",
                        paper_id=paper.id,
                        chunk_index=chunk_idx,
                        text=full_chunk_text,
                        chunking_strategy="structure",
                        metadata={
                            "section_name": sec_header,
                            "chunk_index": chunk_idx,
                            "paper_id": paper.id,
                        },
                    )
                )
                chunk_idx += 1

        return chunks
