from datetime import datetime

from pydantic import BaseModel, Field


class LearningRecordResponse(BaseModel):
    user_id: str
    temp_user_id: str | None = None
    class_id: str | None = None
    unit_id: str | None = None
    lesson_id: str | None = None
    stage: int
    question_id: str
    problem_key: str | None = None
    problem_id: str | int | None = None
    concept_key: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    attempt_no: int = 1
    source: str = "base"
    assignment_id: str | None = None
    created_at: datetime


class LearningRecordsResponse(BaseModel):
    records: list[LearningRecordResponse] = Field(default_factory=list)
    total_count: int


class StudentProgressResponse(BaseModel):
    success: bool = True
    today_solved_count: int = Field(..., description="오늘 제출한 답안 수")
    total_solved_count: int = Field(..., description="전체 답안 제출 수")
    streak_correct_count: int = Field(..., description="최근 연속 정답 수")
    completed_question_count: int = Field(..., description="정답 처리된 고유 문제 수")
    progress_rate: int = Field(..., ge=0, le=100, description="Stage 2 완료율")
    badges: list[str] = Field(default_factory=list, description="학생에게 보여줄 긍정 뱃지")
