from typing import List, Optional
from pydantic import BaseModel, Field


class FeedbackSubmission(BaseModel):
    query: str
    answer: str
    chunks_used: List[str]
    rating: int = Field(description="+1 for positive, -1 for negative")
    comments: Optional[str] = None
