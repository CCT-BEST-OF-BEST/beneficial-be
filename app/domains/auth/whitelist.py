"""권한/개발 편의 화이트리스트.

역할 화이트리스트는 로그인/조회 시점의 role 승격에 사용한다.
답안 우회 화이트리스트는 개발 중 Stage 2 정답 검증 우회에만 사용한다.
DB 문서는 수정하지 않는다.
"""

TEACHER_WHITELIST_EMAILS: frozenset[str] = frozenset()

DEVELOPER_WHITELIST_EMAILS: frozenset[str] = frozenset({
    "kgw1999zz@naver.com",
})

ANSWER_BYPASS_WHITELIST_EMAILS: frozenset[str] = frozenset({
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


def is_answer_bypass_email(email: str | None) -> bool:
    if not email:
        return False
    return _normalize_email(email) in ANSWER_BYPASS_WHITELIST_EMAILS


def _normalize_email(email: str) -> str:
    return email.strip().lower()
