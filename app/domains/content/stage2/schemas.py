from pydantic import BaseModel, Field


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
    is_answer_bypass_enabled: bool = False
    is_admin: bool = False
