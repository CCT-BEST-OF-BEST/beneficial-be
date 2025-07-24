# beneficial-be/app/api/learning/learning_router.py

from fastapi import APIRouter, HTTPException
from app.data.models.learning_models import (
    ChapterResponse, Stage1Response, Stage1CompleteRequest,
    SubmitAnswerRequest
)
from app.api.learning.learning_service import get_learning_service
from app.common.logging.logging_config import get_logger

router = APIRouter(prefix="/learning", tags=["learning"])
logger = get_logger(__name__)

@router.post("/submit-answer")
async def submit_answer(request: SubmitAnswerRequest):
    """
    답변 제출 및 기록
    - 정답 여부 확인
    - 학습 기록 저장
    - 진도 업데이트
    - 다음 복습 시간 계산
    """
    try:
        logger.info(f"✍️ 답변 제출: {request.temp_user_id} - {request.chapter_id}단원 {request.lesson_id}차시")
        
        learning_service = get_learning_service()
        result = await learning_service.submit_answer(request)
        
        logger.info("✅ 답변 제출 완료")
        return result
        
    except Exception as e:
        logger.error(f"❌ 답변 제출 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chapter/{chapter_id}", response_model=ChapterResponse)
async def get_chapter_data(chapter_id: str, temp_user_id: str):
    """
    단원별 전체 차시 정보 조회
    - 각 차시별 진행도
    - 잠금 상태
    - 학습할 단어 목록
    """
    try:
        logger.info(f"📚 단원 데이터 조회: {temp_user_id} - {chapter_id}단원")
        
        learning_service = get_learning_service()
        response = await learning_service.get_chapter_data(temp_user_id, chapter_id)
        
        logger.info(f"✅ 단원 데이터 조회 완료: 총 {len(response.lessons)}개 차시")
        return response
        
    except Exception as e:
        logger.error(f"❌ 단원 데이터 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stage1/{chapter_id}/{lesson_id}", response_model=Stage1Response)
async def get_stage1_data(chapter_id: str, lesson_id: str, temp_user_id: str):
    """
    1단계 어휘 학습 데이터 조회
    - 카드 목록
    - 학습 진행 상태
    """
    try:
        logger.info(f"📚 1단계 어휘 학습 데이터 조회: {temp_user_id} - {chapter_id}단원 {lesson_id}차시")
        
        learning_service = get_learning_service()
        response = await learning_service.get_stage1_data(temp_user_id, chapter_id, lesson_id)
        
        logger.info(f"✅ 1단계 데이터 조회 완료: {response.total_cards}개 카드")
        return response
        
    except Exception as e:
        logger.error(f"❌ 1단계 데이터 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stage1/complete")
async def complete_stage1(request: Stage1CompleteRequest):
    """
    1단계 학습 완료 처리
    - 모든 카드 확인 완료
    - 2단계 잠금 해제
    """
    try:
        logger.info(f"✍️ 1단계 완료 요청: {request.chapter_id}단원 {request.lesson_id}차시")
        
        learning_service = get_learning_service()
        result = await learning_service.complete_stage1(request)
        
        logger.info("✅ 1단계 완료 처리 완료")
        return result
        
    except Exception as e:
        logger.error(f"❌ 1단계 완료 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))