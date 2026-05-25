from pydantic import BaseModel, Field


class StudentProgressResponse(BaseModel):
    success: bool = True
    today_solved_count: int = Field(..., description="오늘 제출한 답안 수")
    total_solved_count: int = Field(..., description="전체 답안 제출 수")
    streak_correct_count: int = Field(..., description="최근 연속 정답 수")
    completed_question_count: int = Field(..., description="정답 처리된 고유 문제 수")
    progress_rate: int = Field(..., ge=0, le=100, description="Stage 3 완료율")
    badges: list[str] = Field(default_factory=list, description="학생에게 보여줄 긍정 뱃지")
