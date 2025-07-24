# beneficial-be/app/api/user/user_router.py 생성
from fastapi import APIRouter, HTTPException
from app.data.models.user_models import TempUser, CreateTempUserRequest
from app.api.user.user_service import get_user_service
from app.common.logging.logging_config import get_logger

router = APIRouter(prefix="/users", tags=["users"])
logger = get_logger(__name__)

@router.post("/temp", response_model=TempUser)
async def create_temp_user(request: CreateTempUserRequest):
    """임시 사용자 생성"""
    try:
        user_service = get_user_service()
        return await user_service.create_temp_user(request.nickname)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/temp/{temp_user_id}", response_model=TempUser)
async def get_temp_user(temp_user_id: str):
    """임시 사용자 조회"""
    try:
        user_service = get_user_service()
        user = await user_service.get_temp_user(temp_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))