from abc import ABC, abstractmethod
from typing import List
from ..models import PaperMetadata, Chunk


class BaseChunker(ABC):
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def chunk_paper(self, paper: PaperMetadata) -> List[Chunk]:
        """Split a paper (abstract or full text) into structured Chunks."""
        pass
