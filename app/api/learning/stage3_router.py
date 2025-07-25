# beneficial-be/app/api/learning/stage3_router.py

from fastapi import APIRouter, HTTPException
from app.api.learning.stage3_service import Stage3Service
from app.data.models.learning_models import (
    Stage3ProblemsResponse, Stage3AnswerRequest, Stage3AnswerResponse,
    Stage3ProgressResponse
)
from app.common.logging.logging_config import get_logger

router = APIRouter(prefix="/learning/stage3", tags=["stage3"])
logger = get_logger(__name__)

# 서비스 인스턴스
stage3_service = Stage3Service()


@router.get(
    "/problems",
    summary="3단계 문제풀이 문제 목록 조회",
    description="3단계 문제풀이의 모든 문제 목록을 반환합니다.",
    response_model=Stage3ProblemsResponse
)
async def get_stage3_problems() -> Stage3ProblemsResponse:
    """3단계 문제 목록 조회"""
    try:
        response = stage3_service.get_problems()
        logger.info(f"✅ 3단계 문제 목록 조회 완료: {response.total_problems}개")
        return response
        
    except Exception as e:
        logger.error(f"❌ 3단계 문제 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="3단계 문제 목록 조회에 실패했습니다")


@router.get(
    "/next-problem",
    summary="3단계 다음 문제 조회",
    description="진행도에 따라 다음에 풀어야 할 문제를 반환합니다.",
    response_model=dict
)
async def get_next_problem() -> dict:
    """다음 문제 조회"""
    try:
        problem = stage3_service.get_next_problem()
        
        if not problem:
            return {
                "success": True,
                "message": "모든 문제를 완료했습니다!",
                "is_completed": True
            }
        
        # 정답과 해설은 제외하고 반환
        problem_response = {
            "problem_id": problem["problem_id"],
            "sentence_part1": problem["sentence_part1"],
            "sentence_part2": problem["sentence_part2"],
            "image": problem["image"],
            "badge": problem.get("badge")
        }
        
        logger.info(f"✅ 3단계 다음 문제 조회 완료: 문제 ID {problem['problem_id']}")
        
        return {
            "success": True,
            "problem": problem_response,
            "is_completed": False
        }
        
    except Exception as e:
        logger.error(f"❌ 3단계 다음 문제 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="다음 문제 조회에 실패했습니다")


@router.post(
    "/submit-answer",
    summary="3단계 답변 제출",
    description="사용자의 답변을 제출하고 결과를 반환합니다.",
    response_model=Stage3AnswerResponse
)
async def submit_stage3_answer(request: Stage3AnswerRequest) -> Stage3AnswerResponse:
    """답변 제출"""
    try:
        response = stage3_service.submit_answer(
            request.problem_id,
            request.user_answer
        )
        
        status_text = "정답" if response.is_correct else "오답"
        logger.info(f"✅ 3단계 답변 제출 완료: 문제 ID {request.problem_id} - {status_text}")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ 3단계 답변 제출 실패: {e}")
        raise HTTPException(status_code=500, detail="답변 제출에 실패했습니다")


@router.get(
    "/progress",
    summary="3단계 진행도 조회",
    description="3단계 문제풀이의 현재 진행도를 반환합니다.",
    response_model=Stage3ProgressResponse
)
async def get_stage3_progress() -> Stage3ProgressResponse:
    """진행도 조회"""
    try:
        response = stage3_service.get_progress()
        logger.info(f"✅ 3단계 진행도 조회 완료: 정답 {response.progress.correct_count}개, 오답 {response.progress.wrong_count}개")
        return response
        
    except Exception as e:
        logger.error(f"❌ 3단계 진행도 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="진행도 조회에 실패했습니다")


@router.post(
    "/reset-progress",
    summary="3단계 진행도 초기화",
    description="3단계 문제풀이의 진행도를 초기화합니다.",
    response_model=dict
)
async def reset_stage3_progress() -> dict:
    """진행도 초기화 (개발/테스트용)"""
    try:
        # 진행도 컬렉션에서 해당 문서 삭제
        stage3_service.mongo_client.delete_one(
            stage3_service.progress_collection,
            {"_id": "stage3_progress"}
        )
        
        # 초기 진행도 생성
        total_problems = stage3_service._get_total_problems()
        initial_progress = {
            "_id": "stage3_progress",
            "total_problems": total_problems,
            "correct_count": 0,
            "wrong_count": 0,
            "review_problems": [],
            "completed_problems": [],
            "current_problem_id": 1,
            "next_problem_index": 1,
            "review_problem_index": 0
        }
        
        stage3_service.mongo_client.insert_one(
            stage3_service.progress_collection,
            initial_progress
        )
        
        logger.info(f"✅ 3단계 진행도 초기화 완료: {initial_progress}")
        
        return {
            "success": True,
            "message": "진행도가 초기화되었습니다."
        }
        
    except Exception as e:
        logger.error(f"❌ 3단계 진행도 초기화 실패: {e}")
        raise HTTPException(status_code=500, detail="진행도 초기화에 실패했습니다") 