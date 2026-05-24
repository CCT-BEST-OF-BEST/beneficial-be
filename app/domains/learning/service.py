from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.common.security import utc_now
from app.domains.learning.models import (
    LearningRecord,
    StudentWeaknessProfile,
    WeakConcept,
)
from app.domains.learning.repositories.base import LearningRecordRepository


CONCEPT_KEY_BY_ANSWER = {
    # Stage 2/3 활용형
    "가르쳐": "가르치다/가르키다",
    "가르켰다": "가르치다/가르키다",
    "맞췄다": "맞추다/맞히다",
    "맞혀": "맞추다/맞히다",
    "맞혔다": "맞추다/맞히다",
    "잃어버렸다": "잊다/잃다",
    "잊었다": "잊다/잃다",
    "메고": "메다/매다",
    "매고": "메다/매다",
    "매었다": "메다/매다",
    "바란다": "바라다/바래다",
    "바랬다": "바라다/바래다",
    "부쳤다": "부치다/붙이다",
    "붙였다": "부치다/붙이다",
    "부치신다": "부치다/붙이다",
    "돼": "되/돼",
    "되고": "되/돼",
    "돼서": "되/돼",
    "안": "안/않다",
    "않다": "안/않다",
    "않고": "안/않다",
    "반드시": "반드시/반듯이",
    "반듯이": "반드시/반듯이",
    "이따가": "이따가/있다가",
    "있다가": "이따가/있다가",
    # Stage 1 기본형 (카드 쌍 word1/word2)
    "가르치다": "가르치다/가르키다",
    "가르키다": "가르치다/가르키다",
    "맞추다": "맞추다/맞히다",
    "맞히다": "맞추다/맞히다",
    "잊다": "잊다/잃다",
    "잃다": "잊다/잃다",
    "메다": "메다/매다",
    "매다": "메다/매다",
    "바라다": "바라다/바래다",
    "바래다": "바라다/바래다",
    "부치다": "부치다/붙이다",
    "붙이다": "부치다/붙이다",
    "되다": "되/돼",
    "돼다": "되/돼",
}


class LearningRecordService:
    def __init__(self, repository: LearningRecordRepository):
        self.repository = repository

    def record_answer(
        self,
        user_id: str,
        stage: int,
        question_id: str,
        user_answer: str,
        correct_answer: str,
        is_correct: bool,
        concept_key: Optional[str] = None,
        temp_user_id: Optional[str] = None,
    ) -> LearningRecord:
        record = LearningRecord(
            user_id=user_id,
            temp_user_id=temp_user_id,
            stage=stage,
            question_id=question_id,
            concept_key=concept_key or resolve_concept_key(correct_answer, user_answer),
            user_answer=user_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
        )
        self.repository.create_record(
            record.model_dump() if hasattr(record, "model_dump") else record.dict()
        )
        return record

    def get_weakness_profile(
        self,
        user_id: str,
        min_wrong_count: int = 2,
    ) -> StudentWeaknessProfile:
        records = self.repository.find_records_by_user(user_id)
        wrong_count_by_concept: Dict[str, int] = defaultdict(int)
        last_wrong_at_by_concept: Dict[str, datetime] = {}

        for record in records:
            if record.get("is_correct"):
                continue

            concept_key = record.get("concept_key")
            if not concept_key:
                continue

            wrong_count_by_concept[concept_key] += 1
            created_at = record.get("created_at")
            if isinstance(created_at, datetime):
                last_wrong_at_by_concept[concept_key] = max(
                    created_at,
                    last_wrong_at_by_concept.get(concept_key, created_at),
                )

        weak_concepts = []
        for concept_key, wrong_count in wrong_count_by_concept.items():
            if wrong_count < min_wrong_count:
                continue
            weak_concepts.append(
                WeakConcept(
                    concept_key=concept_key,
                    wrong_count=wrong_count,
                    last_wrong_at=last_wrong_at_by_concept[concept_key],
                    priority=_calculate_priority(wrong_count),
                )
            )

        weak_concepts.sort(key=lambda item: item.priority, reverse=True)
        return StudentWeaknessProfile(user_id=user_id, weak_concepts=weak_concepts)

    def get_records(self, user_id: str) -> list[LearningRecord]:
        return [
            LearningRecord(**record)
            for record in self.repository.find_records_by_user(user_id)
        ]

    def get_student_progress_metrics(self, user_id: str) -> Dict[str, int]:
        records = sorted(
            self.repository.find_records_by_user(user_id),
            key=_record_created_at,
            reverse=True,
        )
        today = utc_now().date()

        today_solved_count = sum(
            1 for record in records if _record_created_at(record).date() == today
        )
        streak_correct_count = 0
        for record in records:
            if record.get("is_correct"):
                streak_correct_count += 1
                continue
            break

        completed_question_ids = {
            record.get("question_id")
            for record in records
            if record.get("is_correct") and record.get("question_id")
        }

        return {
            "today_solved_count": today_solved_count,
            "total_solved_count": len(records),
            "streak_correct_count": streak_correct_count,
            "completed_question_count": len(completed_question_ids),
        }

    def record_stage1_card_check(
        self,
        pair_id: str,
        correct_word: str,
        chosen_word: str,
        user_id: Optional[str] = None,
    ) -> tuple[bool, str]:
        """1단계 카드 확인 결과를 평가하고, 로그인 사용자면 기록을 저장한다.

        Returns: (is_correct, concept_key)
        """
        is_correct = chosen_word.strip() == correct_word.strip()
        concept_key = resolve_concept_key(correct_word, chosen_word)
        if user_id:
            self.record_answer(
                user_id=user_id,
                stage=1,
                question_id=f"stage1_{pair_id}",
                user_answer=chosen_word,
                correct_answer=correct_word,
                is_correct=is_correct,
                concept_key=concept_key,
            )
        return is_correct, concept_key

    def record_stage2_answer(
        self,
        problem_id: int,
        correct_answer: str,
        user_answer: str,
        user_id: Optional[str] = None,
    ) -> tuple[bool, str]:
        """2단계 문제 답안을 평가하고, 로그인 사용자면 기록을 저장한다.

        Returns: (is_correct, concept_key)
        """
        is_correct = user_answer.strip() == correct_answer.strip()
        concept_key = resolve_concept_key(correct_answer, user_answer)
        if user_id:
            self.record_answer(
                user_id=user_id,
                stage=2,
                question_id=f"stage2_problem_{problem_id}",
                user_answer=user_answer,
                correct_answer=correct_answer,
                is_correct=is_correct,
                concept_key=concept_key,
            )
        return is_correct, concept_key


def resolve_concept_key(correct_answer: str, user_answer: str | None = None) -> str:
    correct = correct_answer.strip()
    submitted = (user_answer or "").strip()
    return (
        CONCEPT_KEY_BY_ANSWER.get(correct)
        or CONCEPT_KEY_BY_ANSWER.get(submitted)
        or correct
    )


def _calculate_priority(wrong_count: int) -> float:
    return min(1.0, round(0.5 + wrong_count * 0.15, 2))


def _record_created_at(record: Dict[str, Any]) -> datetime:
    created_at = record.get("created_at")
    if not isinstance(created_at, datetime):
        return datetime.min.replace(tzinfo=timezone.utc)
    if created_at.tzinfo is None:
        return created_at.replace(tzinfo=timezone.utc)
    return created_at.astimezone(timezone.utc)
