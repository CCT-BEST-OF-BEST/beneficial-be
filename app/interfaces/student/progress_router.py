from fastapi import APIRouter, Depends

from app.domains.auth.dependencies import get_current_student
from app.domains.auth.models import User
from app.domains.learning.dependencies import get_learning_record_service
from app.domains.learning.service import LearningRecordService
from app.domains.learning.stage3_service import Stage3Service, get_stage3_service
from app.domains.learning.student_schemas import StudentProgressResponse

router = APIRouter(prefix="/student/me", tags=["student"])


def get_stage3_progress_service() -> Stage3Service:
    return get_stage3_service()


@router.get("/progress", response_model=StudentProgressResponse)
def get_my_progress(
    current_user: User = Depends(get_current_student),
    learning_record_service: LearningRecordService = Depends(get_learning_record_service),
    stage3_service: Stage3Service = Depends(get_stage3_progress_service),
) -> StudentProgressResponse:
    metrics = learning_record_service.get_student_progress_metrics(current_user.user_id)
    progress_rate = 0

    try:
        stage3_progress = stage3_service.get_progress(current_user.user_id).progress
        if stage3_progress.total_problems > 0:
            progress_rate = round(
                len(stage3_progress.completed_problems)
                / stage3_progress.total_problems
                * 100
            )
    except Exception:
        progress_rate = 0

    return StudentProgressResponse(
        **metrics,
        progress_rate=progress_rate,
        badges=_build_badges(metrics, progress_rate),
    )


def _build_badges(metrics: dict[str, int], progress_rate: int) -> list[str]:
    badges = []
    if metrics["total_solved_count"] > 0:
        badges.append("첫 학습 시작")
    if metrics["streak_correct_count"] >= 3:
        badges.append("연속 정답")
    if progress_rate >= 100:
        badges.append("Stage 3 완료")
    return badges
