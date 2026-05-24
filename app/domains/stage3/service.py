import logging
from typing import Any, Dict, List, Optional

from app.domains.stage3.schemas import (
    Stage3AnswerResponse,
    Stage3ProblemsResponse,
    Stage3ProblemResponse,
    Stage3ProgressResponse,
)
from app.domains.learning.service import LearningRecordService
from app.infrastructure.db.mongo.mongo_client import MongoClient, get_mongo_client

logger = logging.getLogger(__name__)


class Stage3Service:
    problems_collection = "stage3_problems"
    progress_collection = "stage3_progress"

    def __init__(
        self,
        mongo_client: MongoClient,
        learning_record_service: LearningRecordService = None,
        openai_client=None,
    ):
        self.mongo_client = mongo_client
        self.learning_record_service = learning_record_service
        self.openai_client = openai_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_problems(self) -> Stage3ProblemsResponse:
        stage3_data = self._load_problems_data()
        problems = [
            Stage3ProblemResponse(
                problem_id=p["problem_id"],
                sentence_part1=p["sentence_part1"],
                sentence_part2=p["sentence_part2"],
                image=p["image"],
                badge="첫학습",
            )
            for p in stage3_data["problems"]
        ]
        return Stage3ProblemsResponse(
            success=True,
            instruction=stage3_data["instruction"],
            total_problems=stage3_data["total_problems"],
            problems=problems,
        )

    def get_next_problem(self, user_id: str) -> Optional[Dict[str, Any]]:
        progress = self._load_progress(user_id)

        if not progress:
            problem = self._get_problem_by_id(1)
            if problem:
                problem["badge"] = "첫학습"
            return problem

        next_index = progress.get("next_problem_index", 1)
        completed = set(progress.get("completed_problems", []))

        # 순차 진행 (1→5), 완료된 문제 건너뜀
        while next_index <= 5 and next_index in completed:
            next_index += 1

        if next_index <= 5:
            problem = self._get_problem_by_id(next_index)
            if problem:
                problem["badge"] = "첫학습"
            return problem

        # 모든 문제를 시도한 뒤 복습 출제
        review_problems = progress.get("review_problems", [])
        if review_problems and progress.get("next_problem_index", 1) > 5:
            review_index = progress.get("review_problem_index", 0)
            if review_index >= len(review_problems):
                review_index = 0
                self._patch_progress(user_id, {"review_problem_index": 0})

            problem = self._get_problem_by_id(review_problems[review_index])
            if problem:
                problem["badge"] = "재도전"
            return problem

        return None

    async def submit_answer(
        self,
        problem_id: int,
        user_answer: str,
        user_id: str,
    ) -> Stage3AnswerResponse:
        problem = self._get_problem_by_id(problem_id)
        if not problem:
            raise ValueError(f"문제 ID {problem_id}를 찾을 수 없습니다")

        is_correct = user_answer.strip() == problem["correct_answer"].strip()
        status, badge = self._determine_status(problem_id, is_correct, user_id)
        self._update_progress(problem_id, is_correct, user_id)

        if self.learning_record_service:
            self.learning_record_service.record_answer(
                user_id=user_id,
                stage=3,
                question_id=f"stage3_problem_{problem_id}",
                user_answer=user_answer,
                correct_answer=problem["correct_answer"],
                is_correct=is_correct,
            )

        explanation = await self._resolve_explanation(problem, user_answer, is_correct)

        return Stage3AnswerResponse(
            success=True,
            problem_id=problem_id,
            is_correct=is_correct,
            user_answer=user_answer,
            correct_answer=problem["correct_answer"],
            explanation=explanation,
            full_sentence=problem["full_sentence"],
            status=status,
            badge=badge,
        )

    async def _resolve_explanation(
        self,
        problem: Dict[str, Any],
        user_answer: str,
        is_correct: bool,
    ) -> str:
        """정답이면 기본 해설, 오답이면 매핑 → 매핑 없으면 LLM fallback."""
        if is_correct:
            return problem["explanation"]

        mapped = problem.get("wrong_explanations", {}).get(user_answer.strip())
        if mapped:
            return mapped

        if self.openai_client is not None:
            try:
                return await self._llm_fallback_explanation(problem, user_answer)
            except Exception as e:
                logger.warning(
                    f"[stage3] LLM fallback 실패, 정적 해설로 대체: {e}"
                )

        return problem["explanation"]

    async def _llm_fallback_explanation(
        self,
        problem: Dict[str, Any],
        user_answer: str,
    ) -> str:
        system_prompt = (
            "너는 초등학생 돌봄 선생님이야. 한국어 맞춤법을 쉽고 친근하게 설명해. "
            "1) 학생이 적은 답을 짚어주고, 2) 그게 왜 안 맞는지 짧게 알려주고, "
            "3) 정답이 맞는 이유로 마무리해. 두세 문장으로 짧게, 반말로."
        )
        user_prompt = (
            f"문장: {problem['full_sentence']}\n"
            f"정답: {problem['correct_answer']}\n"
            f"학생이 적은 답: {user_answer}\n"
            f"참고 설명: {problem.get('explanation', '')}\n\n"
            f"위 정보를 바탕으로 학생에게 맞춤형 피드백을 만들어줘."
        )
        return await self.openai_client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=200,
            temperature=0.5,
        )

    def get_progress(self, user_id: str) -> Stage3ProgressResponse:
        progress = self._load_progress(user_id)
        if not progress:
            total = self._get_total_problems()
            progress = self._create_initial_progress(user_id, total)
            self.mongo_client.insert_one(self.progress_collection, progress)

        is_completed = len(progress.get("completed_problems", [])) >= progress.get(
            "total_problems", 0
        )
        return Stage3ProgressResponse(
            success=True, progress=progress, is_completed=is_completed
        )

    def reset_progress(self, user_id: str) -> None:
        self.mongo_client.delete_one(
            self.progress_collection, {"user_id": user_id}
        )
        total = self._get_total_problems()
        self.mongo_client.insert_one(
            self.progress_collection, self._create_initial_progress(user_id, total)
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_progress(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.mongo_client.find_one(
            self.progress_collection, {"user_id": user_id}
        )

    def _patch_progress(self, user_id: str, fields: Dict[str, Any]) -> None:
        self.mongo_client.update_one(
            self.progress_collection, {"user_id": user_id}, fields
        )

    def _create_initial_progress(self, user_id: str, total: int) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "total_problems": total,
            "correct_count": 0,
            "wrong_count": 0,
            "review_problems": [],
            "completed_problems": [],
            "current_problem_id": None,
            "next_problem_index": 1,
            "review_problem_index": 0,
        }

    def _update_progress(self, problem_id: int, is_correct: bool, user_id: str) -> None:
        progress = self._load_progress(user_id)
        if not progress:
            total = self._get_total_problems()
            progress = self._create_initial_progress(user_id, total)
            self.mongo_client.insert_one(self.progress_collection, progress)
            # reload to get the inserted doc
            progress = self._load_progress(user_id)

        if is_correct:
            progress["correct_count"] = progress.get("correct_count", 0) + 1
            if problem_id not in progress.get("completed_problems", []):
                progress["completed_problems"] = progress.get("completed_problems", []) + [problem_id]
            if problem_id in progress.get("review_problems", []):
                progress["review_problems"] = [
                    pid for pid in progress["review_problems"] if pid != problem_id
                ]
                progress["review_problem_index"] = progress.get("review_problem_index", 0) + 1
        else:
            progress["wrong_count"] = progress.get("wrong_count", 0) + 1
            if problem_id not in progress.get("review_problems", []):
                progress["review_problems"] = progress.get("review_problems", []) + [problem_id]

        progress["current_problem_id"] = problem_id
        next_index = progress.get("next_problem_index", 1)

        if problem_id == next_index and next_index <= 5:
            progress["next_problem_index"] = next_index + 1
        elif problem_id in progress.get("review_problems", []) and not is_correct:
            progress["review_problem_index"] = progress.get("review_problem_index", 0) + 1

        # _id 는 filter 에서만 사용하므로 update dict 에서 제거
        update_fields = {k: v for k, v in progress.items() if k not in ("_id", "user_id")}
        self.mongo_client.update_one(
            self.progress_collection, {"user_id": user_id}, update_fields
        )

    def _determine_status(
        self, problem_id: int, is_correct: bool, user_id: str
    ) -> tuple:
        if is_correct:
            return "correct", "훌륭해요!"

        progress = self._load_progress(user_id)
        if progress and problem_id in progress.get("review_problems", []):
            return "review", "재도전"
        return "review", "잠시후복습"

    def _get_problem_by_id(self, problem_id: int) -> Optional[Dict[str, Any]]:
        data = self._load_problems_data()
        if not data:
            return None
        for p in data.get("problems", []):
            if p["problem_id"] == problem_id:
                return dict(p)
        return None

    def _load_problems_data(self) -> Dict[str, Any]:
        data = self.mongo_client.find_one(
            self.problems_collection, {"_id": "stage3_problems"}
        )
        if not data:
            raise RuntimeError("3단계 문제 데이터를 찾을 수 없습니다")
        return data

    def _get_total_problems(self) -> int:
        data = self.mongo_client.find_one(
            self.problems_collection, {"_id": "stage3_problems"}
        )
        return data.get("total_problems", 0) if data else 0


def get_stage3_service(
    learning_record_service: LearningRecordService = None,
    openai_client=None,
) -> Stage3Service:
    return Stage3Service(
        mongo_client=get_mongo_client(),
        learning_record_service=learning_record_service,
        openai_client=openai_client,
    )
