from app.domains.auth.whitelist import (
    is_answer_bypass_email,
    is_developer_email,
    is_teacher_email,
)


def test_developer_whitelist_is_separate_from_teacher_whitelist():
    assert is_developer_email(" kgw1999zz@naver.com ")
    assert not is_teacher_email("kgw1999zz@naver.com")


def test_answer_bypass_whitelist_is_separate_from_role_policy():
    assert is_answer_bypass_email("kgw1999zz@naver.com")
    assert not is_answer_bypass_email("student@example.com")
