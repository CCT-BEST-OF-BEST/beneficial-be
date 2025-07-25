# beneficial-be/app/api/learning/stage3_router.py

from fastapi import APIRouter, HTTPException
from app.api.learning.stage3_service import Stage3Service
from app.data.models.learning_models import (
    Stage3ProblemsResponse, Stage3AnswerRequest, Stage3AnswerResponse,
    Stage3ProgressResponse
)
from app.common.logging.logging_config import get_logger

router = APIRouter(prefix="/learning/stage3", tags=["stage3"])
logger = get_logger(__name__)

# 서비스 인스턴스
stage3_service = Stage3Service()


@router.get(
    "/problems",
    summary="3단계 문제 목록 조회",
    description="""
## API 설명
3단계 문제풀이의 모든 문제 목록을 조회합니다.

## 프론트엔드 구현 가이드
- **학습 시작 전**: 전체 문제 목록을 미리 로드하여 학습 계획 수립
- **진행률 표시**: 전체 문제 수를 기준으로 진행률 계산

## 응답 예시
```json
{
  "success": true,
  "instruction": "빈칸에 알맞은 맞춤법을 작성하세요",
  "total_problems": 5,
  "problems": [
    {
      "problem_id": 1,
      "sentence_part1": "차에 타면 안전벨트를 매는 것을",
      "sentence_part2": "마!",
      "image": "stage3/problem_1.png",
      "badge": "첫학습"
    }
  ]
}
```

## 사용 시나리오
1. 학습 화면 진입 시 한 번만 호출
2. 문제 목록을 UI에 표시 (예: 문제 1/5, 문제 2/5...)
    """,
    response_model=Stage3ProblemsResponse
)
async def get_stage3_problems() -> Stage3ProblemsResponse:
    """3단계 문제 목록 조회"""
    try:
        response = stage3_service.get_problems()
        logger.info(f"✅ 3단계 문제 목록 조회 완료: {response.total_problems}개")
        return response
        
    except Exception as e:
        logger.error(f"❌ 3단계 문제 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="3단계 문제 목록 조회에 실패했습니다")


@router.get(
    "/next-problem",
    summary="다음 문제 조회",
    description="""
## API 설명
사용자의 현재 진행도에 따라 다음에 풀어야 할 문제를 반환합니다.

## 학습 알고리즘
### 1단계: 순차 학습 (1-5번 문제)
- 문제 1 → 문제 2 → 문제 3 → 문제 4 → 문제 5
- 모든 문제를 한 번씩 시도 (정답/오답 상관없이)

### 2단계: 복습 학습 (틀린 문제들)
- 1-5번 문제 완료 후 틀린 문제들만 복습
- 복습 문제는 순환 방식으로 출제

## 프론트엔드 구현 가이드
- **문제 출제**: `sentence_part1 + [빈칸] + sentence_part2` 형태로 문장 구성
- **뱃지 표시**: `badge` 필드에 따라 UI 스타일 적용
  - `첫학습`: 새로운 문제
  - `재도전`: 복습 문제
- **완료 처리**: `is_completed: true` 시 학습 완료 화면으로 이동

## 응답 예시
### 문제 출제
```json
{
  "success": true,
  "problem": {
    "problem_id": 1,
    "sentence_part1": "차에 타면 안전벨트를 매는 것을",
    "sentence_part2": "마!",
    "image": "stage3/problem_1.png",
    "badge": "첫학습"
  },
  "is_completed": false
}
```

### 학습 완료
```json
{
  "success": true,
  "message": "모든 문제를 완료했습니다!",
  "is_completed": true
}
```
    """,
    response_model=dict
)
async def get_next_problem() -> dict:
    """다음 문제 조회"""
    try:
        problem = stage3_service.get_next_problem()
        
        if not problem:
            return {
                "success": True,
                "message": "모든 문제를 완료했습니다!",
                "is_completed": True
            }
        
        # 정답과 해설은 제외하고 반환
        problem_response = {
            "problem_id": problem["problem_id"],
            "sentence_part1": problem["sentence_part1"],
            "sentence_part2": problem["sentence_part2"],
            "image": problem["image"],
            "badge": problem.get("badge")
        }
        
        logger.info(f"✅ 3단계 다음 문제 조회 완료: 문제 ID {problem['problem_id']}")
        
        return {
            "success": True,
            "problem": problem_response,
            "is_completed": False
        }
        
    except Exception as e:
        logger.error(f"❌ 3단계 다음 문제 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="다음 문제 조회에 실패했습니다")


@router.post(
    "/submit-answer",
    summary="답변 제출",
    description="""
## API 설명
사용자가 입력한 답변을 제출하고 정답 여부와 결과를 반환합니다.

## 프론트엔드 구현 가이드
- **결과 처리**: `is_correct` 필드에 따라 정답/오답 UI 표시
- **뱃지 시스템**: `badge` 필드에 따른 피드백
  - `훌륭해요!`: 정답
  - `잠시후복습`: 첫 오답
  - `재도전`: 복습 중 오답
- **해설 표시**: `explanation`과 `full_sentence` 필드 활용

## 응답 예시
### 정답
```json
{
  "success": true,
  "problem_id": 1,
  "is_correct": true,
  "user_answer": "잊지",
  "correct_answer": "잊지",
  "explanation": "잊지: '잊다'의 어간 '잊-'에 '-지'가 붙은 형태로, '잊지 말아라'의 준말입니다.",
  "full_sentence": "차에 타면 안전벨트를 매는 것을 잊지 마!",
  "status": "correct",
  "badge": "훌륭해요!"
}
```

### 오답
```json
{
  "success": true,
  "problem_id": 2,
  "is_correct": false,
  "user_answer": "바래",
  "correct_answer": "바랐",
  "explanation": "바랐: '바라다'의 어간 '바라-'에 '-었'이 붙은 형태로, 과거의 희망을 나타냅니다.",
  "full_sentence": "용돈이 오르기를 간절히 바랐다.",
  "status": "review",
  "badge": "잠시후복습"
}
```
    """,
    response_model=Stage3AnswerResponse
)
async def submit_stage3_answer(request: Stage3AnswerRequest) -> Stage3AnswerResponse:
    """답변 제출"""
    try:
        response = stage3_service.submit_answer(
            request.problem_id,
            request.user_answer
        )
        
        status_text = "정답" if response.is_correct else "오답"
        logger.info(f"✅ 3단계 답변 제출 완료: 문제 ID {request.problem_id} - {status_text}")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ 3단계 답변 제출 실패: {e}")
        raise HTTPException(status_code=500, detail="답변 제출에 실패했습니다")


@router.get(
    "/progress",
    summary="학습 진행도 조회",
    description="""
## API 설명
3단계 문제풀이의 현재 진행도를 조회합니다.

## 프론트엔드 구현 가이드
- **진행률 계산**: `completed_problems.length / total_problems * 100`
- **통계 표시**: `correct_count`, `wrong_count` 활용
- **복습 문제**: `review_problems` 배열로 복습 필요 문제 확인
- **완료 여부**: `is_completed` 필드로 학습 완료 상태 확인

## 응답 예시
```json
{
  "success": true,
  "progress": {
    "total_problems": 5,
    "correct_count": 3,
    "wrong_count": 2,
    "review_problems": [2, 4],
    "completed_problems": [1, 3, 5],
    "current_problem_id": 2,
    "next_problem_index": 6,
    "review_problem_index": 0
  },
  "is_completed": false
}
```
    """,
    response_model=Stage3ProgressResponse
)
async def get_stage3_progress() -> Stage3ProgressResponse:
    """진행도 조회"""
    try:
        response = stage3_service.get_progress()
        logger.info(f"✅ 3단계 진행도 조회 완료: 정답 {response.progress.correct_count}개, 오답 {response.progress.wrong_count}개")
        return response
        
    except Exception as e:
        logger.error(f"❌ 3단계 진행도 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="진행도 조회에 실패했습니다")


@router.post(
    "/reset-progress",
    summary="진행도 초기화",
    description="""
## API 설명
3단계 문제풀이의 진행도를 초기화합니다.

## 🎯프론트엔드 구현 가이드
- **요구사항 반영 완료**: 다시 3단계 문제DB 상태들을 원래 상태로 롤백 (사유 : 시연) 
- **데이터 삭제**: 모든 학습 기록이 삭제됨
- **복구 불가**: 초기화 후 이전 데이터 복구 불가능

## 응답 예시
```json
{
  "success": true,
  "message": "진행도가 초기화되었습니다."
}
```
    """,
    response_model=dict
)
async def reset_stage3_progress() -> dict:
    """진행도 초기화 (개발/테스트용)"""
    try:
        # 진행도 컬렉션에서 해당 문서 삭제
        stage3_service.mongo_client.delete_one(
            stage3_service.progress_collection,
            {"_id": "stage3_progress"}
        )
        
        # 초기 진행도 생성
        total_problems = stage3_service._get_total_problems()
        initial_progress = {
            "_id": "stage3_progress",
            "total_problems": total_problems,
            "correct_count": 0,
            "wrong_count": 0,
            "review_problems": [],
            "completed_problems": [],
            "current_problem_id": 1,
            "next_problem_index": 1,
            "review_problem_index": 0
        }
        
        stage3_service.mongo_client.insert_one(
            stage3_service.progress_collection,
            initial_progress
        )
        
        logger.info(f"✅ 3단계 진행도 초기화 완료: {initial_progress}")
        
        return {
            "success": True,
            "message": "진행도가 초기화되었습니다."
        }
        
    except Exception as e:
        logger.error(f"❌ 3단계 진행도 초기화 실패: {e}")
        raise HTTPException(status_code=500, detail="진행도 초기화에 실패했습니다") 