from typing import List, Optional

from pydantic import BaseModel, Field


class AssistRequest(BaseModel):
    symptoms: str = Field(..., min_length=3, description="Free-text symptoms in English or Hindi.")
    language: str = Field(default="en", pattern="^(en|hi)$")
    medications: List[str] = Field(default_factory=list)
    location: str = Field(default="Sehore")


class AssistResponse(BaseModel):
    severity: str
    severity_color: str
    message: str
    disclaimer: str
    triage: dict
    drug: dict
    routing: dict
    transcript: Optional[str] = None
