import pytest

from app.domains.auth.service.service import (
    AuthService,
    DuplicateUserError,
    InvalidCredentialsError,
)


class FakeAuthRepository:
    def __init__(self):
        self.users_by_email = {}
        self.users_by_id = {}
        self.refresh_sessions_by_hash = {}

    def create_user(self, user):
        self.users_by_email[user["email"]] = user
        self.users_by_id[user["user_id"]] = user
        return user["user_id"]

    def find_user_by_email(self, email):
        return self.users_by_email.get(email)

    def find_user_by_id(self, user_id):
        return self.users_by_id.get(user_id)

    def create_refresh_session(self, session):
        self.refresh_sessions_by_hash[session["refresh_token_hash"]] = session
        return session["session_id"]

    def find_refresh_session_by_hash(self, refresh_token_hash):
        return self.refresh_sessions_by_hash.get(refresh_token_hash)

    def revoke_refresh_session(self, session_id, revoked_at):
        for session in self.refresh_sessions_by_hash.values():
            if session["session_id"] == session_id:
                session["revoked_at"] = revoked_at
                return True
        return False


def test_signup_normalizes_email_and_hashes_password():
    service = AuthService(FakeAuthRepository())

    user = service.signup(
        email=" Student@Example.COM ",
        password="password123",
        display_name="학생",
    )

    assert user.email == "student@example.com"
    assert user.password_hash != "password123"
    assert user.user_id.startswith("user_")


def test_signup_rejects_duplicate_email():
    service = AuthService(FakeAuthRepository())
    service.signup("student@example.com", "password123", "학생")

    with pytest.raises(DuplicateUserError):
        service.signup("student@example.com", "password123", "학생2")


def test_login_issues_token_pair():
    service = AuthService(FakeAuthRepository())
    service.signup("student@example.com", "password123", "학생")

    token_pair = service.login("student@example.com", "password123")

    assert token_pair["access_token"]
    assert token_pair["refresh_token"]
    assert token_pair["expires_in"] > 0
    assert token_pair["user"].email == "student@example.com"


def test_login_rejects_wrong_password():
    service = AuthService(FakeAuthRepository())
    service.signup("student@example.com", "password123", "학생")

    with pytest.raises(InvalidCredentialsError):
        service.login("student@example.com", "wrong-password")


def test_developer_whitelist_upgrades_role_on_login():
    service = AuthService(FakeAuthRepository())
    service.signup("kgw1999zz@naver.com", "password123", "개발자")

    token_pair = service.login("kgw1999zz@naver.com", "password123")

    assert token_pair["user"].role == "developer"


def test_legacy_admin_role_is_normalized_to_developer():
    repository = FakeAuthRepository()
    service = AuthService(repository)
    user = service.signup("legacy-admin@example.com", "password123", "관리자")
    repository.users_by_id[user.user_id]["role"] = "admin"
    repository.users_by_email[user.email]["role"] = "admin"

    normalized_user = service.get_user(user.user_id)

    assert normalized_user.role == "developer"
