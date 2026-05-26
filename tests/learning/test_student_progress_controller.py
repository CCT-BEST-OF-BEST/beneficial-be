from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.domains.agent.router import get_my_agent_profile
from app.domains.auth.models import User
from app.domains.learning.progress.router import get_my_progress


def _user(role: str = "student") -> User:
    now = datetime.now(timezone.utc)
    return User(
        user_id=f"user_{role}",
        email=f"{role}@example.com",
        password_hash="hash",
        display_name=role,
        role=role,
        created_at=now,
        updated_at=now,
    )


class FakeLearningRecordService:
    def get_student_progress_metrics(self, user_id):
        return {
            "today_solved_count": 4,
            "total_solved_count": 7,
            "streak_correct_count": 3,
            "completed_question_count": 5,
        }

    def get_weakness_profile(self, user_id):
        raise AssertionError("student profile endpoint should be blocked first")


class FakeStage3Service:
    def get_progress(self, user_id):
        return SimpleNamespace(
            progress=SimpleNamespace(
                total_problems=5,
                completed_problems=[1, 2],
            )
        )


def test_student_progress_response_uses_positive_metrics_only():
    response = get_my_progress(
        current_user=_user("student"),
        learning_record_service=FakeLearningRecordService(),
        stage3_service=FakeStage3Service(),
    )

    assert response.today_solved_count == 4
    assert response.streak_correct_count == 3
    assert response.progress_rate == 40
    assert "연속 정답" in response.badges
    assert not hasattr(response, "wrong_count")


def test_agent_profile_me_rejects_students():
    with pytest.raises(HTTPException) as exc_info:
        get_my_agent_profile(
            current_user=_user("student"),
            learning_record_service=FakeLearningRecordService(),
        )

    assert exc_info.value.status_code == 403
