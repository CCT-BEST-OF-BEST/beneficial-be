from typing import List, Optional

from pydantic import BaseModel, Field


class Stage3Problem(BaseModel):
    """3단계 문제 모델"""
    problem_id: int = Field(..., description="문제 ID")
    sentence_part1: str = Field(..., description="문장 첫 부분")
    correct_answer: str = Field(..., description="정답")
    sentence_part2: str = Field(..., description="문장 뒷부분")
    full_sentence: str = Field(..., description="완성된 문장")
    explanation: str = Field(..., description="해설")
    image: str = Field(..., description="이미지 파일명")


class Stage3ProblemResponse(BaseModel):
    """3단계 문제 응답"""
    problem_id: int = Field(..., description="문제 ID")
    sentence_part1: str = Field(..., description="문장 첫 부분")
    sentence_part2: str = Field(..., description="문장 뒷부분")
    image: str = Field(..., description="이미지 파일명")
    badge: Optional[str] = Field(None, description="뱃지 (첫학습/훌륭해요 등)")


class Stage3ProblemsResponse(BaseModel):
    """3단계 문제 목록 응답"""
    success: bool = Field(..., description="성공 여부")
    lesson_id: Optional[str] = Field(None, description="차시 ID (Stage 3는 독립 모듈)")
    title: Optional[str] = Field(None, description="제목 (Stage 3는 독립 모듈)")
    instruction: str = Field(..., description="설명")
    total_problems: int = Field(..., description="전체 문제 수")
    problems: List[Stage3ProblemResponse] = Field(..., description="문제 목록")


class Stage3AnswerRequest(BaseModel):
    """3단계 답변 제출 요청"""
    problem_id: int = Field(..., description="문제 ID")
    user_answer: str = Field(..., description="사용자 답변")


class Stage3AnswerResponse(BaseModel):
    """3단계 답변 제출 응답"""
    success: bool = Field(..., description="성공 여부")
    problem_id: int = Field(..., description="문제 ID")
    is_correct: bool = Field(..., description="정답 여부")
    user_answer: str = Field(..., description="사용자 답변")
    correct_answer: str = Field(..., description="정답")
    explanation: str = Field(..., description="해설")
    full_sentence: str = Field(..., description="완성된 문장")
    status: str = Field(..., description="상태 (correct/wrong/review/completed)")
    badge: Optional[str] = Field(None, description="뱃지 (훌륭해요 등)")


class Stage3Progress(BaseModel):
    """3단계 진행도"""
    total_problems: int = Field(..., description="전체 문제 수")
    correct_count: int = Field(default=0, description="정답 개수")
    wrong_count: int = Field(default=0, description="오답 개수")
    review_problems: List[int] = Field(default_factory=list, description="복습 필요한 문제 ID 목록")
    completed_problems: List[int] = Field(default_factory=list, description="완료한 문제 ID 목록")
    current_problem_id: Optional[int] = Field(None, description="현재 문제 ID")
    next_problem_index: int = Field(default=1, description="다음 출제할 문제 인덱스 (1-5)")
    review_problem_index: int = Field(default=0, description="복습 문제 인덱스")


class Stage3ProgressResponse(BaseModel):
    """3단계 진행도 응답"""
    success: bool = Field(..., description="성공 여부")
    progress: Stage3Progress = Field(..., description="진행도 정보")
    is_completed: bool = Field(..., description="완료 여부")
