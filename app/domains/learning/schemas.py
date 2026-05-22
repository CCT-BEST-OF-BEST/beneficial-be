from datetime import datetime

from pydantic import BaseModel, Field


class LearningRecordResponse(BaseModel):
    user_id: str
    temp_user_id: str | None = None
    stage: int
    question_id: str
    concept_key: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    created_at: datetime


class LearningRecordsResponse(BaseModel):
    records: list[LearningRecordResponse] = Field(default_factory=list)
    total_count: int
