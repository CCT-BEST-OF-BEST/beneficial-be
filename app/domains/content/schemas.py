from pydantic import BaseModel, Field


class LessonSummaryResponse(BaseModel):
    lesson_id: str
    unit_id: str
    name: str
    order: int
    concept_keys: list[str] = Field(default_factory=list)
    stage_ids: list[int] = Field(default_factory=list)


class UnitSummaryResponse(BaseModel):
    unit_id: str
    name: str
    order: int
    lessons: list[LessonSummaryResponse] = Field(default_factory=list)


class ContentUnitsResponse(BaseModel):
    units: list[UnitSummaryResponse] = Field(default_factory=list)
    total_count: int


class LessonDetailResponse(BaseModel):
    lesson_id: str
    unit_id: str
    name: str
    order: int
    concept_keys: list[str] = Field(default_factory=list)
    stage_ids: list[int] = Field(default_factory=list)
