# beneficial-be/app/data/models/user_models.py 생성
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TempUser(BaseModel):
    """임시 사용자 정보"""
    temp_user_id: str = Field(..., description="임시 사용자 ID")
    nickname: str = Field(..., description="닉네임")
    created_at: datetime = Field(default_factory=datetime.now)
    last_access: datetime = Field(default_factory=datetime.now)

class CreateTempUserRequest(BaseModel):
    """임시 사용자 생성 요청"""
    nickname: str = Field(..., description="닉네임")