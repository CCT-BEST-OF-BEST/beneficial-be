import pytest

from app.common.security import get_auth_secret
from app.main import DEFAULT_CORS_ORIGINS, get_cors_origins


def test_auth_secret_allows_dev_fallback(monkeypatch):
    monkeypatch.delenv("AUTH_SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.setenv("APP_ENV", "development")

    assert get_auth_secret() == "dev-only-change-me"


def test_auth_secret_fails_fast_in_production(monkeypatch):
    monkeypatch.delenv("AUTH_SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.setenv("APP_ENV", "production")

    with pytest.raises(RuntimeError):
        get_auth_secret()


def test_auth_secret_reads_configured_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("AUTH_SECRET_KEY", "secure-secret")

    assert get_auth_secret() == "secure-secret"


def test_cors_origins_default_to_local_development(monkeypatch):
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)

    assert get_cors_origins() == DEFAULT_CORS_ORIGINS
    assert "*" not in get_cors_origins()


def test_cors_origins_parse_env_list(monkeypatch):
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        "https://app.example.com, https://admin.example.com",
    )

    assert get_cors_origins() == [
        "https://app.example.com",
        "https://admin.example.com",
    ]
