# beneficial-be/app/api/learning/learning_service.py

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from app.data.models.learning_models import (
    LearningRecord, SubmitAnswerRequest, UserProgress,
    LessonProgress, Stage1Response, Stage1CompleteRequest,
    WordCard, ChapterResponse, LessonSummary
)
from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)

class LearningService:
    def __init__(self):
        self.mongo_client = get_mongo_client()

    async def submit_answer(self, request: SubmitAnswerRequest) -> Dict[str, Any]:
        """답변 제출 및 기록"""
        try:
            # 정답 확인
            is_correct = await self._check_answer(request)
            
            # 학습 기록 저장
            record = LearningRecord(
                temp_user_id=request.temp_user_id,
                chapter_id=request.chapter_id,
                lesson_id=request.lesson_id,
                stage=request.stage,
                question_id=request.question_id,
                answer=request.answer,
                is_correct=is_correct,
                review_date=await self._calculate_next_review(is_correct)
            )
            
            self.mongo_client.insert_one("learning_records", record.dict())
            
            # 진도 업데이트
            await self._update_progress(record)
            
            return {
                "is_correct": is_correct,
                "next_review": record.review_date
            }
            
        except Exception as e:
            logger.error(f"❌ 답변 제출 실패: {e}")
            raise

    async def _check_answer(self, request: SubmitAnswerRequest) -> bool:
        """정답 확인"""
        collection = "korean_word_problems" if request.stage in [2, 3] else "card_check"
        question = self.mongo_client.find_one(
            collection,
            {"questionId": request.question_id}
        )
        return question.get("correctAnswer") == request.answer

    async def _calculate_next_review(self, is_correct: bool) -> Optional[datetime]:
        """다음 복습 시간 계산"""
        if not is_correct:
            # 틀린 경우 즉시 복습
            return datetime.now()
            
        # 맞은 경우 망각곡선에 따라 복습 시간 설정
        intervals = [1, 2, 3, 6]  # 복습 간격 (일)
        return datetime.now() + timedelta(days=intervals[0])

    async def _update_progress(self, record: LearningRecord):
        """진도 업데이트"""
        progress = await self._get_user_progress(
            record.temp_user_id,
            record.chapter_id,
            record.lesson_id
        )
        
        if progress is None:
            progress = UserProgress(
                temp_user_id=record.temp_user_id,
                chapter_id=record.chapter_id,
                lesson_id=record.lesson_id
            )
        
        # 통계 업데이트
        if record.is_correct:
            progress.correct_count += 1
        else:
            progress.wrong_count += 1
            if record.question_id not in progress.review_words:
                progress.review_words.append(record.question_id)
        
        progress.last_study_date = datetime.now()
        
        # 진행 단계 업데이트
        if record.stage not in progress.completed_stages:
            progress.completed_stages.append(record.stage)
            progress.completed_stages.sort()
        
        # MongoDB에 저장 (upsert)
        self.mongo_client.upsert_one(
            "user_progress",
            {
                "temp_user_id": progress.temp_user_id,
                "chapter_id": progress.chapter_id,
                "lesson_id": progress.lesson_id
            },
            progress.dict()
        )

    async def _get_user_progress(
        self,
        temp_user_id: str,
        chapter_id: str,
        lesson_id: str
    ) -> Optional[UserProgress]:
        """사용자 진도 조회"""
        progress_data = self.mongo_client.find_one(
            "user_progress",
            {
                "temp_user_id": temp_user_id,
                "chapter_id": chapter_id,
                "lesson_id": lesson_id
            }
        )
        return UserProgress(**progress_data) if progress_data else None

    async def get_chapter_data(self, temp_user_id: str, chapter_id: str) -> ChapterResponse:
        """단원별 전체 차시 정보 조회 (사용자별 진도 포함)"""
        try:
            # 해당 단원의 모든 차시 데이터 조회
            lessons_data = list(self.mongo_client.find_many(
                "card_check",
                {"chapterId": chapter_id}
            ))
            
            if not lessons_data:
                raise ValueError(f"단원 데이터를 찾을 수 없습니다: {chapter_id}단원")

            # 사용자의 모든 진도 데이터 조회
            user_progress = list(self.mongo_client.find_many(
                "user_progress",
                {"temp_user_id": temp_user_id, "chapter_id": chapter_id}
            ))
            progress_map = {
                f"{p['chapter_id']}_{p['lesson_id']}": UserProgress(**p)
                for p in user_progress
            }

            # 전체 진행도 계산을 위한 변수
            completed_lessons = 0
            total_lessons = len(lessons_data)

            # 각 차시별 요약 정보 생성
            lesson_summaries = []
            for lesson in lessons_data:
                lesson_id = lesson["lessonId"]
                progress_key = f"{chapter_id}_{lesson_id}"
                user_progress = progress_map.get(progress_key)
                
                # 완료 여부 확인
                is_completed = False
                completed_at = None
                if user_progress:
                    is_completed = len(user_progress.completed_stages) == 3  # 모든 단계 완료
                    if is_completed:
                        completed_lessons += 1
                        completed_at = user_progress.last_study_date

                # 단어 쌍 데이터 정리
                word_pairs = [
                    {
                        "word1": card["word1"],
                        "word2": card["word2"]
                    }
                    for card in lesson.get("cards", [])
                ]

                lesson_summaries.append(LessonSummary(
                    lesson_id=lesson_id,
                    title=lesson.get("title", ""),
                    word_pairs=word_pairs,
                    is_locked=await self._check_lesson_lock(temp_user_id, chapter_id, lesson_id),
                    can_start=not await self._check_lesson_lock(temp_user_id, chapter_id, lesson_id),
                    is_completed=is_completed,
                    completed_at=completed_at
                ))

            # 차시 ID 기준으로 정렬
            lesson_summaries.sort(key=lambda x: int(x.lesson_id))

            # 전체 진행도 계산
            total_progress = int((completed_lessons / total_lessons) * 100)

            return ChapterResponse(
                chapter_id=chapter_id,
                chapter_title="소리도 뜻도 다른 헷갈리는 문장",
                total_progress=total_progress,
                lessons=lesson_summaries
            )

        except Exception as e:
            logger.error(f"❌ 단원 데이터 조회 실패: {e}")
            raise

    async def get_stage1_data(self, chapter_id: str, lesson_id: str) -> Stage1Response:
        """1단계 어휘 학습 데이터 조회"""
        try:
            # 카드 데이터 조회
            card_data = self.mongo_client.find_one(
                "card_check",
                {
                    "chapterId": chapter_id,
                    "lessonId": lesson_id
                }
            )
            
            if not card_data:
                raise ValueError(f"카드 데이터를 찾을 수 없습니다: {chapter_id}단원 {lesson_id}차시")

            # 학습 진행 상태 조회
            progress = await self._get_lesson_progress(chapter_id, lesson_id)
            
            # 카드 목록 생성
            cards = [WordCard(**card) for card in card_data.get("cards", [])]
            
            return Stage1Response(
                lesson_id=lesson_id,
                chapter_id=chapter_id,
                cards=cards,
                total_cards=len(cards),
                viewed_cards=progress.get("viewed_cards", []),
                can_proceed=progress.get("stage1_completed", False)
            )

        except Exception as e:
            logger.error(f"❌ 1단계 데이터 조회 실패: {e}")
            raise

    async def complete_stage1(self, request: Stage1CompleteRequest) -> Dict[str, Any]:
        """1단계 학습 완료 처리"""
        try:
            # 모든 카드 확인 여부 검증
            card_data = self.mongo_client.find_one(
                "card_check",
                {
                    "chapterId": request.chapter_id,
                    "lessonId": request.lesson_id
                }
            )
            
            total_cards = len(card_data.get("cards", []))
            if len(request.viewed_cards) < total_cards:
                raise ValueError("모든 카드를 확인하지 않았습니다.")

            # 진행도 업데이트
            update_data = {
                "stage1_completed": True,
                "current_stage": 2,
                "progress_rate": 25,
                "last_updated": datetime.now(),
                "viewed_cards": request.viewed_cards
            }
            
            self.mongo_client.update_one(
                "learning_progress",
                {
                    "chapter_id": request.chapter_id,
                    "lesson_id": request.lesson_id
                },
                update_data
            )

            return {
                "status": "success",
                "message": "1단계 학습 완료",
                "next_stage": 2,
                "progress_rate": 25
            }

        except Exception as e:
            logger.error(f"❌ 1단계 완료 처리 실패: {e}")
            raise

    async def _get_lesson_progress(
        self, 
        chapter_id: str, 
        lesson_id: str
    ) -> Dict[str, Any]:
        """차시별 진행도 조회"""
        progress_data = self.mongo_client.find_one(
            "learning_progress",
            {
                "chapter_id": chapter_id,
                "lesson_id": lesson_id
            }
        )

        if not progress_data:
            return {
                "lesson_id": lesson_id,
                "chapter_id": chapter_id,
                "current_stage": 1,
                "stage1_completed": False,
                "stage2_completed": False,
                "stage3_completed": False,
                "progress_rate": 0,
                "last_updated": datetime.now()
            }

        return progress_data

    async def _check_lesson_lock(
        self,
        temp_user_id: str,
        chapter_id: str,
        lesson_id: str
    ) -> bool:
        """차시 잠금 상태 확인"""
        try:
            # 첫 번째 차시는 항상 시작 가능
            if lesson_id == "1":
                return False
                
            # 이전 차시 완료 여부 확인
            prev_lesson_id = str(int(lesson_id) - 1)
            prev_progress = await self._get_user_progress(
                temp_user_id,
                chapter_id,
                prev_lesson_id
            )
            
            # 이전 차시가 완료되지 않았으면 잠금
            if not prev_progress or len(prev_progress.completed_stages) < 3:
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"❌ 차시 잠금 상태 확인 실패: {e}")
            return True  # 에러 발생시 안전하게 잠금

# 전역 서비스 인스턴스
_learning_service = None

def get_learning_service() -> LearningService:
    """학습 서비스 인스턴스 반환"""
    global _learning_service
    if _learning_service is None:
        _learning_service = LearningService()
    return _learning_service