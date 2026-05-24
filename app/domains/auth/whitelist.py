"""역할 승격 화이트리스트.

이메일이 화이트리스트에 포함된 사용자는 로그인/조회 시점에 role이 자동 승격된다.
DB 문서는 수정하지 않는다.
"""

TEACHER_WHITELIST_EMAILS: frozenset[str] = frozenset()

DEVELOPER_WHITELIST_EMAILS: frozenset[str] = frozenset({
    "kgw1999zz@naver.com",
})


def is_teacher_email(email: str | None) -> bool:
    if not email:
        return False
    return _normalize_email(email) in TEACHER_WHITELIST_EMAILS


def is_developer_email(email: str | None) -> bool:
    if not email:
        return False
    return _normalize_email(email) in DEVELOPER_WHITELIST_EMAILS


def _normalize_email(email: str) -> str:
    return email.strip().lower()
