from fastapi import APIRouter, Depends, HTTPException

from app.common.logging.logging_config import get_logger
from app.domains.stage3.schemas import (
    Stage3AnswerRequest,
    Stage3AnswerResponse,
    Stage3ProblemsResponse,
    Stage3ProgressResponse,
)
from app.domains.auth.dependencies import get_optional_current_user
from app.domains.auth.models import User
from app.domains.learning.dependencies import get_learning_record_service
from app.domains.stage3.service import ANONYMOUS_USER_ID, get_stage3_service

router = APIRouter(prefix="/learning/stage3", tags=["stage3"])
logger = get_logger(__name__)


def _user_id(current_user: User | None) -> str:
    return current_user.user_id if current_user else ANONYMOUS_USER_ID


@router.get(
    "/problems",
    summary="3단계 문제 목록 조회",
    response_model=Stage3ProblemsResponse,
)
async def get_stage3_problems() -> Stage3ProblemsResponse:
    try:
        return get_stage3_service().get_problems()
    except Exception as e:
        logger.error(f"[ERROR] 3단계 문제 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="3단계 문제 목록 조회에 실패했습니다")


@router.get(
    "/next-problem",
    summary="다음 문제 조회",
    description="""
학습 알고리즘:
1. 순차 학습 (1→5): 정답/오답 상관없이 한 번씩 시도
2. 복습 학습: 모든 문제 시도 후 틀린 문제만 순환 출제
3. 완료: 복습 문제까지 모두 정답 시 None 반환
    """,
    response_model=dict,
)
async def get_next_problem(
    current_user: User | None = Depends(get_optional_current_user),
) -> dict:
    try:
        uid = _user_id(current_user)
        problem = get_stage3_service().get_next_problem(user_id=uid)

        if not problem:
            return {"success": True, "message": "모든 문제를 완료했습니다!", "is_completed": True}

        return {
            "success": True,
            "problem": {
                "problem_id": problem["problem_id"],
                "sentence_part1": problem["sentence_part1"],
                "sentence_part2": problem["sentence_part2"],
                "image": problem["image"],
                "badge": problem.get("badge"),
            },
            "is_completed": False,
        }
    except Exception as e:
        logger.error(f"[ERROR] 3단계 다음 문제 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="다음 문제 조회에 실패했습니다")


@router.post(
    "/submit-answer",
    summary="답변 제출",
    response_model=Stage3AnswerResponse,
)
async def submit_stage3_answer(
    request: Stage3AnswerRequest,
    current_user: User | None = Depends(get_optional_current_user),
) -> Stage3AnswerResponse:
    try:
        uid = _user_id(current_user)
        learning_svc = get_learning_record_service() if current_user else None
        return get_stage3_service(learning_record_service=learning_svc).submit_answer(
            request.problem_id,
            request.user_answer,
            user_id=uid,
        )
    except Exception as e:
        logger.error(f"[ERROR] 3단계 답변 제출 실패: {e}")
        raise HTTPException(status_code=500, detail="답변 제출에 실패했습니다")


@router.get(
    "/progress",
    summary="학습 진행도 조회",
    response_model=Stage3ProgressResponse,
)
async def get_stage3_progress(
    current_user: User | None = Depends(get_optional_current_user),
) -> Stage3ProgressResponse:
    try:
        uid = _user_id(current_user)
        return get_stage3_service().get_progress(user_id=uid)
    except Exception as e:
        logger.error(f"[ERROR] 3단계 진행도 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="진행도 조회에 실패했습니다")


@router.post(
    "/reset-progress",
    summary="진행도 초기화",
    response_model=dict,
)
async def reset_stage3_progress(
    current_user: User | None = Depends(get_optional_current_user),
) -> dict:
    try:
        uid = _user_id(current_user)
        get_stage3_service().reset_progress(user_id=uid)
        return {"success": True, "message": "진행도가 초기화되었습니다."}
    except Exception as e:
        logger.error(f"[ERROR] 3단계 진행도 초기화 실패: {e}")
        raise HTTPException(status_code=500, detail="진행도 초기화에 실패했습니다")
