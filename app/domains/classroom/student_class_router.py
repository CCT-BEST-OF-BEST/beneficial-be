from fastapi import APIRouter, Depends

from app.domains.auth.dependencies import get_current_user
from app.domains.auth.models import User
from app.domains.classroom.dependencies import get_classroom_service
from app.domains.classroom.schemas import StudentMyClassResponse
from app.domains.classroom.service import ClassroomService

router = APIRouter(prefix="/student/my-class", tags=["student"])


@router.get("", response_model=StudentMyClassResponse | None)
def get_my_class(
    current_user: User = Depends(get_current_user),
    classroom_service: ClassroomService = Depends(get_classroom_service),
) -> StudentMyClassResponse | None:
    info = classroom_service.get_my_class_info(current_user.user_id)
    if not info:
        return None
    return StudentMyClassResponse(**info)
