from fastapi import APIRouter, Depends

from app.domains.auth.dependencies import get_current_user
from app.domains.auth.models import User
from app.domains.learning.dependencies import get_learning_record_service
from app.domains.learning.schemas import LearningRecordResponse, LearningRecordsResponse
from app.domains.learning.service import LearningRecordService

router = APIRouter(prefix="/learning/records", tags=["learning"])


@router.get("/me", response_model=LearningRecordsResponse)
def get_my_learning_records(
    current_user: User = Depends(get_current_user),
    learning_record_service: LearningRecordService = Depends(get_learning_record_service),
):
    records = learning_record_service.get_records(current_user.user_id)
    response_records = [
        LearningRecordResponse(**record.model_dump())
        for record in records
    ]
    return LearningRecordsResponse(
        records=response_records,
        total_count=len(response_records),
    )
