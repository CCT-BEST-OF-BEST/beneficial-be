import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict


DEFAULT_PASSWORD_ITERATIONS = 120_000


class TokenError(ValueError):
    """Raised when a signed token is missing, malformed, or expired."""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def get_auth_secret() -> str:
    secret = os.getenv("AUTH_SECRET_KEY") or os.getenv("JWT_SECRET_KEY")
    if not secret:
        # Development fallback. Production should set AUTH_SECRET_KEY.
        secret = "dev-only-change-me"
    return secret


def hash_password(password: str, iterations: int = DEFAULT_PASSWORD_ITERATIONS) -> str:
    salt = secrets.token_urlsafe(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt}${password_hash.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected_hash = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        ).hex()
        return hmac.compare_digest(actual_hash, expected_hash)
    except (ValueError, TypeError):
        return False


def create_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(refresh_token: str) -> str:
    return hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()


def _base64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _base64url_decode(encoded: str) -> bytes:
    padding = "=" * (-len(encoded) % 4)
    return base64.urlsafe_b64decode(encoded + padding)


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
    extra_claims: Dict[str, Any] | None = None,
) -> str:
    now = utc_now()
    expires_at = now + (expires_delta or timedelta(minutes=30))
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": subject,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": secrets.token_urlsafe(16),
    }
    if extra_claims:
        payload.update(extra_claims)

    encoded_header = _base64url_encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8")
    )
    encoded_payload = _base64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = hmac.new(
        get_auth_secret().encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    return f"{encoded_header}.{encoded_payload}.{_base64url_encode(signature)}"


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".", 2)
    except ValueError as exc:
        raise TokenError("Malformed token") from exc

    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    expected_signature = hmac.new(
        get_auth_secret().encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    actual_signature = _base64url_decode(encoded_signature)
    if not hmac.compare_digest(actual_signature, expected_signature):
        raise TokenError("Invalid token signature")

    try:
        payload = json.loads(_base64url_decode(encoded_payload))
    except (json.JSONDecodeError, ValueError) as exc:
        raise TokenError("Invalid token payload") from exc

    if payload.get("type") != "access":
        raise TokenError("Invalid token type")

    expires_at = payload.get("exp")
    if not isinstance(expires_at, int):
        raise TokenError("Missing token expiry")
    if expires_at < int(utc_now().timestamp()):
        raise TokenError("Token expired")

    return payload
