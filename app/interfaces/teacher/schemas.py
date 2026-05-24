from datetime import datetime

from pydantic import BaseModel, Field


class TeacherClassResponse(BaseModel):
    class_id: str
    name: str
    teacher_id: str
    student_count: int


class TeacherClassesResponse(BaseModel):
    classes: list[TeacherClassResponse] = Field(default_factory=list)
    total_count: int


class TeacherStudentSummaryResponse(BaseModel):
    user_id: str
    email: str
    display_name: str
    weak_concepts: list[str] = Field(default_factory=list)
    recent_activity_at: datetime | None = None


class TeacherClassStudentsResponse(BaseModel):
    class_id: str
    students: list[TeacherStudentSummaryResponse] = Field(default_factory=list)
    total_count: int
