from typing import Literal

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str = Field(..., min_length=1, max_length=50)
    role: Literal["student", "teacher"] = "student"
    school_name: str | None = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str | None = None


class UserResponse(BaseModel):
    user_id: str
    email: str
    display_name: str
    role: str


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str
    user: UserResponse


class MessageResponse(BaseModel):
    message: str
