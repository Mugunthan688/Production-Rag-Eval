from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PaperMetadata(BaseModel):
    id: str = Field(description="arXiv ID, e.g. 2312.00001")
    title: str
    abstract: str
    authors: List[str]
    categories: List[str]
    submitted_date: datetime
    pdf_url: str
    full_text: Optional[str] = None


class Chunk(BaseModel):
    id: str = Field(description="Unique chunk identifier, e.g. 2312.00001_chunk_0")
    paper_id: str
    chunk_index: int
    text: str
    chunking_strategy: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
