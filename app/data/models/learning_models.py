# beneficial-be/app/data/models/learning_models.py

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class LessonSummary(BaseModel):
    """차시 요약 정보"""
    lesson_id: str = Field(..., description="차시 ID")
    title: str = Field(..., description="차시 제목")
    word_pairs: List[Dict[str, str]] = Field(..., description="학습할 단어 쌍 목록")
    is_locked: bool = Field(default=True, description="잠금 여부")
    can_start: bool = Field(default=False, description="학습 시작 가능 여부")
    is_completed: bool = Field(default=False, description="학습 완료 여부")
    completed_at: Optional[datetime] = Field(None, description="학습 완료 날짜")

class ChapterResponse(BaseModel):
    """단원별 전체 차시 정보 응답"""
    chapter_id: str = Field(..., description="단원 ID")
    chapter_title: str = Field(..., description="단원 제목")
    total_progress: int = Field(default=0, description="전체 진행도 (0-100%)")
    lessons: List[LessonSummary] = Field(..., description="차시별 요약 정보")

# 학습 진행 관련 모델들 (기존 코드는 유지)
class LessonProgress(BaseModel):
    """차시별 진행도"""
    lesson_id: str = Field(..., description="차시 ID")
    chapter_id: str = Field(..., description="단원 ID")
    current_stage: int = Field(default=1, description="현재 진행 중인 단계 (1,2,3)")
    stage1_completed: bool = Field(default=False, description="1단계 완료 여부")
    stage2_completed: bool = Field(default=False, description="2단계 완료 여부")
    stage3_completed: bool = Field(default=False, description="3단계 완료 여부")
    progress_rate: int = Field(default=0, description="전체 진행도 (25% 단위)")
    last_updated: datetime = Field(default_factory=datetime.now, description="마지막 업데이트 시간")

class LessonData(BaseModel):
    """차시 기본 정보"""
    lesson_id: str = Field(..., description="차시 ID")
    chapter_id: str = Field(..., description="단원 ID")
    title: str = Field(..., description="차시 제목")
    description: str = Field(..., description="차시 설명")
    word_count: int = Field(..., description="학습할 단어 쌍 수")

class LessonResponse(BaseModel):
    """차시 정보 응답"""
    lesson_id: str = Field(..., description="차시 ID")
    chapter_id: str = Field(..., description="단원 ID")
    title: str = Field(..., description="차시 제목")
    description: str = Field(..., description="차시 설명")
    is_locked: bool = Field(..., description="잠금 여부")
    progress: LessonProgress = Field(..., description="진행도")
    word_pairs: List[Dict[str, str]] = Field(..., description="학습할 단어 쌍 목록")


class WordCard(BaseModel):
    """어휘 학습 카드 모델"""
    word1: str = Field(..., description="첫 번째 단어")
    meaning1: str = Field(..., description="첫 번째 단어 의미")
    examples1: List[str] = Field(..., description="첫 번째 단어 예문")
    word2: str = Field(..., description="두 번째 단어")
    meaning2: str = Field(..., description="두 번째 단어 의미")
    examples2: List[str] = Field(..., description="두 번째 단어 예문")

class Stage1Response(BaseModel):
    """1단계 어휘 학습 응답"""
    lesson_id: str = Field(..., description="차시 ID")
    chapter_id: str = Field(..., description="단원 ID")
    cards: List[WordCard] = Field(..., description="학습할 카드 목록")
    total_cards: int = Field(..., description="전체 카드 수")
    viewed_cards: List[str] = Field(default_factory=list, description="확인한 카드 ID 목록")
    can_proceed: bool = Field(default=False, description="다음 단계 진행 가능 여부")

class Stage1CompleteRequest(BaseModel):
    """1단계 완료 요청"""
    lesson_id: str = Field(..., description="차시 ID")
    chapter_id: str = Field(..., description="단원 ID")
    viewed_cards: List[str] = Field(..., description="확인한 카드 ID 목록")

class LearningRecord(BaseModel):
    """학습 기록"""
    temp_user_id: str = Field(..., description="임시 사용자 ID")
    chapter_id: str = Field(..., description="단원 ID")
    lesson_id: str = Field(..., description="차시 ID")
    stage: int = Field(..., description="학습 단계 (1,2,3)")
    question_id: str = Field(..., description="문제 ID")
    answer: str = Field(..., description="제출한 답변")
    is_correct: bool = Field(..., description="정답 여부")
    created_at: datetime = Field(default_factory=datetime.now)
    review_date: Optional[datetime] = Field(None, description="다음 복습 예정일")

class SubmitAnswerRequest(BaseModel):
    """답변 제출 요청"""
    temp_user_id: str = Field(..., description="임시 사용자 ID")
    chapter_id: str = Field(..., description="단원 ID")
    lesson_id: str = Field(..., description="차시 ID")
    stage: int = Field(..., description="학습 단계 (1,2,3)")
    question_id: str = Field(..., description="문제 ID")
    answer: str = Field(..., description="제출한 답변")

class UserProgress(BaseModel):
    """사용자 진도"""
    temp_user_id: str = Field(..., description="임시 사용자 ID")
    chapter_id: str = Field(..., description="단원 ID")
    lesson_id: str = Field(..., description="차시 ID")
    current_stage: int = Field(default=1, description="현재 진행 중인 단계")
    completed_stages: List[int] = Field(default_factory=list, description="완료한 단계들")
    correct_count: int = Field(default=0, description="정답 개수")
    wrong_count: int = Field(default=0, description="오답 개수")
    last_study_date: datetime = Field(default_factory=datetime.now)
    review_words: List[str] = Field(default_factory=list, description="복습 필요한 단어들")

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