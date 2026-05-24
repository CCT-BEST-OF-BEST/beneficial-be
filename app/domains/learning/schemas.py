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


class Stage1SubmitRequest(BaseModel):
    pair_id: str = Field(..., description="카드 쌍 ID (예: pair_1)")
    chosen_word: str = Field(..., description="학생이 고른 단어 (word1 또는 word2)")


class Stage1SubmitResponse(BaseModel):
    pair_id: str
    is_correct: bool
    chosen_word: str
    correct_word: str
    concept_key: str


class Stage2ProblemResponse(BaseModel):
    """Stage 2 문제 1건. 정답(correct_answer, full_sentence)은 노출하지 않는다."""
    problem_id: int
    sentence_part1: str
    sentence_part2: str


class Stage2ProblemsResponse(BaseModel):
    success: bool = True
    lesson_id: str
    title: str
    instruction: str
    total_problems: int
    answer_options: list[str] = Field(default_factory=list)
    problems: list[Stage2ProblemResponse] = Field(default_factory=list)


class Stage2SubmitRequest(BaseModel):
    problem_id: int = Field(..., description="문제 ID (1~20)")
    user_answer: str = Field(..., description="학생이 입력한 답")


class Stage2SubmitResponse(BaseModel):
    problem_id: int
    is_correct: bool
    user_answer: str
    correct_answer: str
    full_sentence: str
    concept_key: str
    is_admin: bool = False
