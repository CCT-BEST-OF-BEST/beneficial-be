import logging
from typing import Dict, Any, Optional, List
from app.data.models.learning_models import (
    Stage3ProblemsResponse, Stage3ProblemResponse, 
    Stage3AnswerResponse, Stage3ProgressResponse
)
from app.infrastructure.db.mongo.mongo_client import MongoClient

logger = logging.getLogger(__name__)

class Stage3Service:
    """3단계 문제풀이 서비스"""
    
    def __init__(self):
        self.mongo_client = MongoClient()
        self.problems_collection = "stage3_problems"
        self.progress_collection = "stage3_progress"
    
    def get_problems(self) -> Stage3ProblemsResponse:
        """3단계 문제 목록 조회"""
        try:
            stage3_data = self.mongo_client.find_one(
                self.problems_collection,
                {"_id": "stage3_problems"}
            )
            
            if not stage3_data:
                raise Exception("3단계 문제 데이터를 찾을 수 없습니다")
            
            problems = []
            for problem in stage3_data["problems"]:
                problem_response = Stage3ProblemResponse(
                    problem_id=problem["problem_id"],
                    sentence_part1=problem["sentence_part1"],
                    sentence_part2=problem["sentence_part2"],
                    image=problem["image"],
                    badge="첫학습"  # 문제 목록에서는 모든 문제를 "첫학습"으로 표시
                )
                problems.append(problem_response)
            
            return Stage3ProblemsResponse(
                success=True,
                instruction=stage3_data["instruction"],
                total_problems=stage3_data["total_problems"],
                problems=problems
            )
            
        except Exception as e:
            logger.error(f"❌ 3단계 문제 조회 실패: {e}")
            raise
    
    def get_next_problem(self) -> Optional[Dict[str, Any]]:
        """다음 문제 조회 (진행도 기반, 순차적 선택)"""
        try:
            # 진행도 조회
            progress = self.mongo_client.find_one(
                self.progress_collection,
                {"_id": "stage3_progress"}
            )
            
            if not progress:
                # 처음 시작하는 경우
                logger.info("🚀 첫 번째 문제 시작")
                problem = self._get_problem_by_id(1)
                if problem:
                    problem["badge"] = "첫학습"
                return problem
            
            # 완료하지 않은 문제가 있는지 확인 (우선순위 1)
            next_index = progress.get("next_problem_index", 1)
            completed_problems = set(progress.get("completed_problems", []))
            
            # 다음 문제가 완료되지 않았고 범위 내에 있는지 확인
            while next_index <= 5 and next_index in completed_problems:
                next_index += 1
            
            if next_index <= 5:  # 문제 ID는 1-5
                problem = self._get_problem_by_id(next_index)
                if problem:
                    logger.info(f"📝 새로운 문제 출제: 문제 ID {next_index} (순서대로)")
                    problem["badge"] = "첫학습"  # 안 푼 문제는 "첫학습" 뱃지
                    return problem
            
            # 모든 문제가 완료되었을 때만 복습 문제 확인 (우선순위 2)
            # 복습 문제는 1-5번 문제를 모두 풀고 나서 출제
            if progress.get("review_problems"):
                # 1-5번 문제를 모두 시도했는지 확인 (정답/오답 상관없이)
                total_problems = progress.get("total_problems", 5)
                next_index = progress.get("next_problem_index", 1)
                
                # next_problem_index가 6 이상이면 모든 문제를 시도한 것
                if next_index > total_problems:
                    review_index = progress.get("review_problem_index", 0)
                    if review_index < len(progress["review_problems"]):
                        problem_id = progress["review_problems"][review_index]
                        logger.info(f"🔄 복습 문제 출제: 문제 ID {problem_id} (인덱스: {review_index + 1}/{len(progress['review_problems'])})")
                        problem = self._get_problem_by_id(problem_id)
                        if problem:
                            problem["badge"] = "재도전"  # 복습 문제는 "재도전" 뱃지
                        return problem
                    else:
                        # 복습 문제를 모두 출제했으면 완료
                        logger.info("🔄 복습 문제 모두 출제 완료")
                        return None
            
            # 모든 문제 완료
            logger.info("🎉 모든 문제 완료!")
            return None
            
        except Exception as e:
            logger.error(f"❌ 다음 문제 조회 실패: {e}")
            raise
    
    def submit_answer(self, problem_id: int, user_answer: str) -> Stage3AnswerResponse:
        """답변 제출 및 결과 처리"""
        try:
            # 문제 정보 조회
            problem = self._get_problem_by_id(problem_id)
            if not problem:
                raise Exception(f"문제 ID {problem_id}를 찾을 수 없습니다")
            
            # 정답 여부 확인
            is_correct = user_answer.strip() == problem["correct_answer"].strip()
            logger.info(f"📝 답변 제출: 문제 ID {problem_id}, 사용자 답변: '{user_answer}', 정답: '{problem['correct_answer']}', 정답여부: {is_correct}")
            
            # 응답 상태 결정 (진행도 업데이트 전에)
            status, badge = self._determine_status(problem_id, is_correct)
            
            # 진행도 업데이트
            self._update_progress(problem_id, is_correct)
            
            return Stage3AnswerResponse(
                success=True,
                problem_id=problem_id,
                is_correct=is_correct,
                user_answer=user_answer,
                correct_answer=problem["correct_answer"],
                explanation=problem["explanation"],
                full_sentence=problem["full_sentence"],
                status=status,
                badge=badge
            )
            
        except Exception as e:
            logger.error(f"❌ 답변 제출 실패: {e}")
            raise
    
    def get_progress(self) -> Stage3ProgressResponse:
        """진행도 조회"""
        try:
            progress_data = self.mongo_client.find_one(
                self.progress_collection,
                {"_id": "stage3_progress"}
            )
            
            if not progress_data:
                # 초기 진행도 생성
                total_problems = self._get_total_problems()
                progress_data = {
                    "_id": "stage3_progress",
                    "total_problems": total_problems,
                    "correct_count": 0,
                    "wrong_count": 0,
                    "review_problems": [],
                    "completed_problems": [],
                    "current_problem_id": None,
                    "next_problem_index": 1,
                    "review_problem_index": 0
                }
                
                self.mongo_client.insert_one(self.progress_collection, progress_data)
            
            # 완료 여부 확인
            is_completed = len(progress_data.get("completed_problems", [])) >= progress_data.get("total_problems", 0)
            
            return Stage3ProgressResponse(
                success=True,
                progress=progress_data,
                is_completed=is_completed
            )
            
        except Exception as e:
            logger.error(f"❌ 진행도 조회 실패: {e}")
            raise
    
    def _get_problem_by_id(self, problem_id: int) -> Optional[Dict[str, Any]]:
        """문제 ID로 문제 조회"""
        stage3_data = self.mongo_client.find_one(
            self.problems_collection,
            {"_id": "stage3_problems"}
        )
        
        if not stage3_data:
            return None
        
        for problem in stage3_data["problems"]:
            if problem["problem_id"] == problem_id:
                return problem
        
        return None
    
    def _get_all_problem_ids(self) -> List[int]:
        """모든 문제 ID 목록 조회"""
        stage3_data = self.mongo_client.find_one(
            self.problems_collection,
            {"_id": "stage3_problems"}
        )
        
        if not stage3_data:
            return []
        
        return [problem["problem_id"] for problem in stage3_data["problems"]]
    
    def _get_total_problems(self) -> int:
        """전체 문제 수 조회"""
        stage3_data = self.mongo_client.find_one(
            self.problems_collection,
            {"_id": "stage3_problems"}
        )
        
        return stage3_data.get("total_problems", 0) if stage3_data else 0
    
    def _update_progress(self, problem_id: int, is_correct: bool):
        """진행도 업데이트"""
        try:
            # 현재 진행도 조회
            progress = self.mongo_client.find_one(
                self.progress_collection,
                {"_id": "stage3_progress"}
            )
            
            logger.info(f"🔍 현재 진행도 조회: {progress}")
            
            if not progress:
                # 초기 진행도 생성
                total_problems = self._get_total_problems()
                progress = {
                    "_id": "stage3_progress",
                    "total_problems": total_problems,
                    "correct_count": 0,
                    "wrong_count": 0,
                    "review_problems": [],
                    "completed_problems": [],
                    "current_problem_id": problem_id,
                    "next_problem_index": 1,
                    "review_problem_index": 0
                }
                logger.info(f"🆕 초기 진행도 생성: {progress}")
            
            # 카운트 업데이트
            if is_correct:
                progress["correct_count"] = progress.get("correct_count", 0) + 1
                # 정답인 경우 완료 목록에 추가
                if problem_id not in progress.get("completed_problems", []):
                    progress["completed_problems"] = progress.get("completed_problems", []) + [problem_id]
                # 복습 목록에서 제거하고 복습 문제 인덱스 증가
                if problem_id in progress.get("review_problems", []):
                    progress["review_problems"] = [pid for pid in progress.get("review_problems", []) if pid != problem_id]
                    # 복습 문제가 정답이면 복습 문제 인덱스 증가
                    review_index = progress.get("review_problem_index", 0)
                    progress["review_problem_index"] = review_index + 1
                    logger.info(f"📈 복습 문제 정답으로 인덱스 증가: {review_index} → {review_index + 1}")
                    # 복습 문제가 정답일 때는 next_problem_index를 건드리지 않음 (순차적 진행 유지)
                    logger.info(f"📈 복습 문제 정답 - next_problem_index 유지: {progress.get('next_problem_index', 1)}")
                logger.info(f"✅ 정답 처리: 문제 ID {problem_id}, 완료된 문제: {len(progress.get('completed_problems', []))}개")
            else:
                progress["wrong_count"] = progress.get("wrong_count", 0) + 1
                # 오답인 경우 복습 목록에 추가
                if problem_id not in progress.get("review_problems", []):
                    progress["review_problems"] = progress.get("review_problems", []) + [problem_id]
                logger.info(f"⚠️ 오답 처리: 문제 ID {problem_id}, 복습 문제: {len(progress.get('review_problems', []))}개")
            
            # 현재 문제 ID 업데이트
            progress["current_problem_id"] = problem_id
            
            # 인덱스 업데이트 - 순차 진행 로직
            next_index = progress.get("next_problem_index", 1)
            
            # 현재 문제가 순차 진행 중인 문제인지 확인 (1-5번)
            if problem_id == next_index and next_index <= 5:
                # 순차 진행 중인 문제 - 정답/오답 상관없이 다음 문제로 진행
                progress["next_problem_index"] = next_index + 1
                logger.info(f"📈 순차 진행: {next_index} → {next_index + 1}")
            elif problem_id in progress.get("review_problems", []):
                # 복습 문제 - next_problem_index는 건드리지 않음
                logger.info(f"📈 복습 문제 - next_problem_index 유지: {next_index}")
            else:
                # 기타 경우
                logger.info(f"📈 기타 경우 - next_problem_index 유지: {next_index}")
            
            # DB에 저장/업데이트
            if "_id" in progress:
                self.mongo_client.update_one(
                    self.progress_collection,
                    {"_id": "stage3_progress"},
                    progress
                )
            else:
                self.mongo_client.insert_one(self.progress_collection, progress)
            
            logger.info(f"✅ 진행도 업데이트 완료: 정답 {progress.get('correct_count', 0)}개, 오답 {progress.get('wrong_count', 0)}개")
            
        except Exception as e:
            logger.error(f"❌ 진행도 업데이트 실패: {e}")
            raise
    
    def _determine_status(self, problem_id: int, is_correct: bool) -> tuple[str, Optional[str]]:
        """상태와 뱃지 결정"""
        try:
            if is_correct:
                # 정답인 경우 - "훌륭해요!" 뱃지
                logger.info(f"✅ 문제 {problem_id} 정답 - 뱃지: 훌륭해요!")
                return "correct", "훌륭해요!"
            else:
                # 오답인 경우 - 문제 유형에 따라 뱃지 결정
                progress = self.mongo_client.find_one(
                    self.progress_collection,
                    {"_id": "stage3_progress"}
                )
                
                if progress and problem_id in progress.get("review_problems", []):
                    # 이미 복습 중인 문제 - "재도전" 뱃지
                    logger.info(f"🔄 문제 {problem_id} 오답 (복습 중) - 뱃지: 재도전")
                    return "review", "재도전"
                else:
                    # 첫 번째 오답 - "잠시후복습" 뱃지
                    logger.info(f"🔄 문제 {problem_id} 오답 (첫 번째) - 뱃지: 잠시후복습")
                    return "review", "잠시후복습"
                
        except Exception as e:
            logger.error(f"❌ 상태 결정 실패: {e}")
            return "wrong", None 