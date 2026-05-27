from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GeneratedProblemRequest(BaseModel):
    problem_id: str | None = None
    type: Literal["fill_blank"] = "fill_blank"
    sentence_part1: str
    correct_answer: str
    sentence_part2: str
    full_sentence: str
    explanation: str
    visual_hint: str | None = None
    accent_color: str | None = None
    validation_status: str = "pending"


class GeneratedProblemResponse(BaseModel):
    problem_id: str
    problem_key: str | None = None
    type: str
    sentence_part1: str
    correct_answer: str
    sentence_part2: str
    full_sentence: str
    explanation: str
    visual_hint: str | None = None
    accent_color: str | None = None
    validation_status: str


class CreateAssignmentDraftRequest(BaseModel):
    target_type: Literal["student", "class"]
    class_id: str | None = None
    student_id: str | None = None
    unit_id: str | None = None
    lesson_id: str
    stage: int = 3
    concept_key: str
    problems: list[GeneratedProblemRequest] = Field(default_factory=list)
    generation_context: dict = Field(default_factory=dict)


class GenerateProblemsRequest(BaseModel):
    target_type: Literal["student", "class"]
    class_id: str | None = None
    student_id: str | None = None
    unit_id: str | None = None
    lesson_id: str
    stage: int = 3
    concept_key: str
    count: int = Field(default=3, ge=1, le=10)
    difficulty: Literal["easy", "normal", "hard"] | None = "normal"
    generation_context: dict = Field(default_factory=dict)


class AssignmentResponse(BaseModel):
    assignment_id: str
    teacher_id: str
    class_id: str | None = None
    student_id: str | None = None
    target_type: str
    unit_id: str | None = None
    lesson_id: str
    stage: int
    concept_key: str
    status: str
    source: str
    problems: list[GeneratedProblemResponse] = Field(default_factory=list)
    student_progress: dict[str, list[str]] = Field(default_factory=dict)
    generation_context: dict = Field(default_factory=dict)
    created_at: datetime
    assigned_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None


class AssignmentListResponse(BaseModel):
    assignments: list[AssignmentResponse] = Field(default_factory=list)
    total_count: int


class ProblemValidationResponse(BaseModel):
    problem: GeneratedProblemResponse
    is_valid: bool
    reasons: list[str] = Field(default_factory=list)


class GenerateProblemsResponse(BaseModel):
    assignment: AssignmentResponse | None = None
    validation_results: list[ProblemValidationResponse] = Field(default_factory=list)
    total_generated: int
    total_valid: int


class StudentAssignmentProblemResponse(BaseModel):
    problem_id: str
    problem_key: str | None = None
    type: str
    sentence_part1: str
    sentence_part2: str
    visual_hint: str | None = None
    accent_color: str | None = None


class StudentAssignmentResponse(BaseModel):
    assignment_id: str
    lesson_id: str
    unit_id: str | None = None
    stage: int
    concept_key: str
    status: str
    problems: list[StudentAssignmentProblemResponse] = Field(default_factory=list)
    completed_problem_ids: list[str] = Field(default_factory=list)
    assigned_at: datetime | None = None


class StudentAssignmentListResponse(BaseModel):
    assignments: list[StudentAssignmentResponse] = Field(default_factory=list)
    total_count: int
