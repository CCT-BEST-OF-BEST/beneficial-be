from datetime import datetime, timedelta, timezone

from app.domains.learning.service import LearningRecordService, resolve_concept_key


class FakeLearningRecordRepository:
    def __init__(self):
        self.records = []

    def create_record(self, record):
        self.records.append(record)
        return "record_1"

    def find_records_by_user(self, user_id):
        return [record for record in self.records if record["user_id"] == user_id]


def test_record_answer_stores_agent_readable_fields():
    repository = FakeLearningRecordRepository()
    service = LearningRecordService(repository)

    record = service.record_answer(
        user_id="user_123",
        stage=3,
        question_id="stage3_problem_16",
        user_answer="되",
        correct_answer="돼",
        is_correct=False,
    )

    assert record.user_id == "user_123"
    assert record.concept_key == "되/돼"
    assert record.user_answer == "되"
    assert record.correct_answer == "돼"
    assert repository.records[0]["is_correct"] is False


def test_weakness_profile_groups_wrong_answers_by_concept():
    repository = FakeLearningRecordRepository()
    service = LearningRecordService(repository)
    now = datetime.now(timezone.utc)
    repository.records.extend(
        [
            {
                "user_id": "user_123",
                "concept_key": "되/돼",
                "is_correct": False,
                "created_at": now - timedelta(days=1),
            },
            {
                "user_id": "user_123",
                "concept_key": "되/돼",
                "is_correct": False,
                "created_at": now,
            },
            {
                "user_id": "user_123",
                "concept_key": "맞추다/맞히다",
                "is_correct": False,
                "created_at": now,
            },
            {
                "user_id": "other_user",
                "concept_key": "되/돼",
                "is_correct": False,
                "created_at": now,
            },
        ]
    )

    profile = service.get_weakness_profile("user_123", min_wrong_count=2)

    assert profile.user_id == "user_123"
    assert len(profile.weak_concepts) == 1
    assert profile.weak_concepts[0].concept_key == "되/돼"
    assert profile.weak_concepts[0].wrong_count == 2


def test_resolve_concept_key_falls_back_to_answer():
    assert resolve_concept_key("돼") == "되/돼"
    assert resolve_concept_key("처음보는정답") == "처음보는정답"
