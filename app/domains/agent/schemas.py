from datetime import datetime

from pydantic import BaseModel, Field


class WeakConceptResponse(BaseModel):
    concept_key: str
    wrong_count: int
    last_wrong_at: datetime
    priority: float


class AgentProfileResponse(BaseModel):
    user_id: str
    weak_concepts: list[WeakConceptResponse] = Field(default_factory=list)
