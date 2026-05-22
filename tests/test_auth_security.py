from datetime import timedelta

import pytest

from app.core.security import (
    TokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_verification():
    stored_hash = hash_password("password123")

    assert verify_password("password123", stored_hash)
    assert not verify_password("wrong-password", stored_hash)


def test_access_token_round_trip():
    token = create_access_token(
        subject="user_123",
        expires_delta=timedelta(minutes=5),
        extra_claims={"email": "student@example.com", "role": "student"},
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "user_123"
    assert payload["email"] == "student@example.com"
    assert payload["role"] == "student"


def test_expired_access_token_rejected():
    token = create_access_token(
        subject="user_123",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(TokenError):
        decode_access_token(token)
