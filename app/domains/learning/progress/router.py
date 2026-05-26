from fastapi import APIRouter, Depends

from app.domains.auth.dependencies import get_current_student
from app.domains.auth.models import User
from app.domains.learning.content.service import ContentCatalogService
from app.domains.learning.dependencies import get_content_catalog_service
from app.domains.learning.dependencies import get_learning_record_service
from app.domains.learning.service import LearningRecordService
from app.domains.learning.student_schemas import StudentProgressResponse

router = APIRouter(prefix="/student/me", tags=["student"])


@router.get("/progress", response_model=StudentProgressResponse)
def get_my_progress(
    current_user: User = Depends(get_current_student),
    learning_record_service: LearningRecordService = Depends(get_learning_record_service),
    content_service: ContentCatalogService = Depends(get_content_catalog_service),
) -> StudentProgressResponse:
    metrics = learning_record_service.get_student_progress_metrics(current_user.user_id)
    progress_rate = _calculate_progress_rate(current_user.user_id, learning_record_service, content_service)

    return StudentProgressResponse(
        **metrics,
        progress_rate=progress_rate,
        badges=_build_badges(metrics, progress_rate),
    )


def _calculate_progress_rate(
    user_id: str,
    learning_record_service: LearningRecordService,
    content_service: ContentCatalogService,
) -> int:
    """Stage 2를 통과한 차시 수 / 전체 차시 수로 진행도를 계산한다."""
    try:
        units_with_lessons = content_service.list_units_with_lessons()
        total_lessons = sum(len(lessons) for _, lessons in units_with_lessons)
        if total_lessons == 0:
            return 0

        records = learning_record_service.get_records(user_id)
        completed_lesson_ids = {
            record.lesson_id
            for record in records
            if record.is_correct and record.lesson_id and record.stage == 2
        }
        return round(len(completed_lesson_ids) / total_lessons * 100)
    except Exception:
        return 0


def _build_badges(metrics: dict[str, int], progress_rate: int) -> list[str]:
    badges = []
    if metrics["total_solved_count"] > 0:
        badges.append("첫 학습 시작")
    if metrics["streak_correct_count"] >= 3:
        badges.append("연속 정답")
    if progress_rate >= 100:
        badges.append("전체 학습 완료")
    return badges
