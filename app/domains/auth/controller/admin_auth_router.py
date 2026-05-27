import os
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel

from app.common.security import create_access_token, create_refresh_token, hash_refresh_token, utc_now
from app.domains.auth.service.auth_service import ACCESS_TOKEN_EXPIRE_SECONDS, REFRESH_TOKEN_EXPIRE_DAYS
from app.domains.auth.schema.auth_schemas import AuthTokenResponse, UserResponse

router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])

_ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")


class AdminLoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login", response_model=AuthTokenResponse)
def admin_login(body: AdminLoginRequest, response: Response) -> AuthTokenResponse:
    if not _ADMIN_EMAIL or not _ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="관리자 계정이 설정되지 않았습니다.",
        )

    if body.email.strip().lower() != _ADMIN_EMAIL.lower() or body.password != _ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )

    user_id = "admin_hardcoded"
    access_token = create_access_token(
        subject=user_id,
        expires_delta=timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS),
        extra_claims={"email": _ADMIN_EMAIL, "role": "developer"},
    )
    refresh_token = create_refresh_token()

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/auth",
    )

    return AuthTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_SECONDS,
        user=UserResponse(
            user_id=user_id,
            email=_ADMIN_EMAIL,
            display_name="관리자",
            role="developer",
        ),
    )
