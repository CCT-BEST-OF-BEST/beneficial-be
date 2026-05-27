from typing import Any, Dict

from pydantic import BaseModel, Field


class RagDocument(BaseModel):
    document: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    distance: float = 1.0
    collection: str = "unknown"
    rrf_score: float = 0.0


class RagSearchResult(BaseModel):
    query: str
    documents: list[RagDocument] = Field(default_factory=list)
    context: str
