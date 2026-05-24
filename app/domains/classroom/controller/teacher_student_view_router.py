from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.domains.agent.schemas import AgentProfileResponse, WeakConceptResponse
from app.domains.auth.dependencies import get_current_teacher
from app.domains.auth.models import User
from app.domains.classroom.dependencies import get_classroom_service
from app.domains.classroom.service import ClassroomService
from app.domains.learning.dependencies import get_learning_record_service
from app.domains.learning.schemas import LearningRecordResponse, LearningRecordsResponse
from app.domains.learning.service import LearningRecordService

router = APIRouter(prefix="/teacher/students", tags=["teacher"])


@router.get("/{user_id}/profile", response_model=AgentProfileResponse)
def get_student_profile(
    user_id: str,
    current_user: User = Depends(get_current_teacher),
    classroom_service: ClassroomService = Depends(get_classroom_service),
    learning_record_service: LearningRecordService = Depends(get_learning_record_service),
) -> AgentProfileResponse:
    _ensure_student_access(classroom_service, current_user, user_id)
    profile = learning_record_service.get_weakness_profile(user_id)
    return AgentProfileResponse(
        user_id=profile.user_id,
        weak_concepts=[
            WeakConceptResponse(**weak_concept.model_dump())
            for weak_concept in profile.weak_concepts
        ],
    )


@router.get("/{user_id}/records", response_model=LearningRecordsResponse)
def get_student_records(
    user_id: str,
    stage: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_teacher),
    classroom_service: ClassroomService = Depends(get_classroom_service),
    learning_record_service: LearningRecordService = Depends(get_learning_record_service),
) -> LearningRecordsResponse:
    _ensure_student_access(classroom_service, current_user, user_id)
    records = learning_record_service.get_records(user_id)
    if stage is not None:
        records = [record for record in records if record.stage == stage]
    records = records[:limit]

    response_records = [
        LearningRecordResponse(**record.model_dump())
        for record in records
    ]
    return LearningRecordsResponse(
        records=response_records,
        total_count=len(response_records),
    )


def _ensure_student_access(
    classroom_service: ClassroomService,
    current_user: User,
    student_id: str,
) -> None:
    if not classroom_service.can_access_student(current_user, student_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="담당 학생 데이터만 조회할 수 있습니다.",
        )
