from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class LearningRecord(BaseModel):
    user_id: str = Field(..., description="Authenticated user identifier")
    temp_user_id: Optional[str] = Field(None, description="Legacy compatibility ID")
    stage: int = Field(..., description="Learning stage")
    question_id: str = Field(..., description="Stable question identifier")
    concept_key: str = Field(..., description="Weakness concept key")
    user_answer: str = Field(..., description="Submitted answer")
    correct_answer: str = Field(..., description="Correct answer")
    is_correct: bool = Field(..., description="Whether the answer is correct")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WeakConcept(BaseModel):
    concept_key: str
    wrong_count: int
    last_wrong_at: datetime
    priority: float


class StudentWeaknessProfile(BaseModel):
    user_id: str
    weak_concepts: list[WeakConcept] = Field(default_factory=list)
