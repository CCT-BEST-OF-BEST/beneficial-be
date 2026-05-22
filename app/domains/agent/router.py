from fastapi import APIRouter, Depends

from app.domains.agent.schemas import AgentProfileResponse, WeakConceptResponse
from app.domains.auth.dependencies import get_current_user
from app.domains.auth.models import User
from app.domains.learning.dependencies import get_learning_record_service
from app.domains.learning.service import LearningRecordService

router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/profile/me", response_model=AgentProfileResponse)
def get_my_agent_profile(
    current_user: User = Depends(get_current_user),
    learning_record_service: LearningRecordService = Depends(get_learning_record_service),
):
    profile = learning_record_service.get_weakness_profile(current_user.user_id)
    return AgentProfileResponse(
        user_id=profile.user_id,
        weak_concepts=[
            WeakConceptResponse(**weak_concept.model_dump())
            for weak_concept in profile.weak_concepts
        ],
    )
