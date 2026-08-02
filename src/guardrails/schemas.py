from typing import Literal, Optional
from pydantic import BaseModel, Field


class AdversarialTestCase(BaseModel):
    id: str
    category: Literal["prompt_injection", "system_prompt_leak", "jailbreak"]
    prompt: str
    injected_context: Optional[str] = None
    expected_safe_behavior: str = Field(description="Description of correct safe system response")
