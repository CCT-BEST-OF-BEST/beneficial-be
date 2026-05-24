"""관리자 화이트리스트.

이메일이 ADMIN_WHITELIST_EMAILS에 포함된 사용자는 로그인/조회 시점에
role이 자동으로 'admin'으로 승격된다. DB 문서는 수정하지 않는다.
"""

ADMIN_WHITELIST_EMAILS: frozenset[str] = frozenset({
    "kgw1999zz@naver.com",
})


def is_admin_email(email: str | None) -> bool:
    if not email:
        return False
    return email.strip().lower() in ADMIN_WHITELIST_EMAILS
