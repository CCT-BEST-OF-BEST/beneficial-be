# beneficial-be/app/api/learning/learning_router.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.logging.logging_config import get_logger
from typing import List, Dict, Any
import os

router = APIRouter(prefix="/learning", tags=["learning"])
logger = get_logger(__name__)


@router.get(
    "/stage1/cards",
    summary="1단계 어휘학습 카드 조회",
    description="""
## API 설명
1단계 어휘학습을 위한 카드 쌍 데이터를 조회합니다.

## 프론트엔드 구현 가이드
- **카드 쌍 구성**: `word1`과 `word2`로 구성된 카드 쌍
- **이미지 경로**: `card1`, `card2` 객체의 `front_image`, `back_image` 활용
- **순서 학습**: `order` 필드에 따라 순차적 학습 진행

## 응답 예시
```json
{
  "success": true,
  "total_pairs": 2,
  "card_pairs": [
    {
      "pair_id": "pair_1",
      "word1": "가르치다",
      "word2": "가르키다",
      "card1": {
        "card_id": "card_1",
        "front_image": "/images/cards/card1_front.png",
        "back_image": "/images/cards/card1_back.png"
      },
      "card2": {
        "card_id": "card_2", 
        "front_image": "/images/cards/card2_front.png",
        "back_image": "/images/cards/card2_back.png"
      },
      "order": 1
    }
  ]
}
```
    """,
    response_model=Dict[str, Any]
)
async def get_stage1_cards() -> Dict[str, Any]:
    """1단계 어휘학습 카드 쌍 조회"""
    try:
        mongo_client = get_mongo_client()

        # 카드 쌍 데이터 조회 (order 순으로 정렬)
        card_pairs = list(mongo_client.find_many(
            "stage1_cards",
            {},
            sort=[("order", 1)]
        ))

        if not card_pairs:
            raise HTTPException(status_code=404, detail="카드 데이터를 찾을 수 없습니다")

        # 응답 데이터 구성 (쌍 구조)
        pairs_response = []
        
        for pair in card_pairs:
            pair_data = {
                "pair_id": pair["pair_id"],
                "word1": pair["word1"],
                "word2": pair["word2"],
                "card1": pair["card1"],
                "card2": pair["card2"],
                "order": pair["order"]
            }
            pairs_response.append(pair_data)

        logger.info(f"✅ 1단계 카드 쌍 {len(pairs_response)}개 조회 완료")

        return {
            "success": True,
            "total_pairs": len(pairs_response),
            "card_pairs": pairs_response
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 1단계 카드 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="카드 조회에 실패했습니다")


@router.get(
    "/stage2/problems",
    summary="2단계 예제풀이 문제 조회",
    description="""
## API 설명
2단계 예제풀이를 위한 드래그&드롭 문제와 답안 옵션을 조회합니다.

## 프론트엔드 구현 가이드
- **문제 구성**: `sentence_part1 + [빈칸] + sentence_part2` 형태
- **답안 옵션**: `answer_options` 배열의 카드들을 드래그 가능하게 구현
- **정답 확인**: `problems` 배열의 `correct_answer`와 비교

## 응답 예시
```json
{
  "success": true,
  "lesson_id": "lesson1",
  "title": "2단계 예제풀이",
  "instruction": "맞춤법에 맞는 낱말 카드를 선택하세요",
  "total_problems": 8,
  "answer_options": [
    "가르쳐", "맞힐", "바라는", "가르켰", "맞춰", "잊지", "바랐", "잊으려고"
  ],
  "problems": [
    {
      "problem_id": 1,
      "sentence_part1": "왜 화가 났는지",
      "correct_answer": "가르쳐",
      "sentence_part2": "줘",
      "full_sentence": "왜 화가 났는지 가르쳐 줘"
    }
  ]
}
```
    """,
    response_model=Dict[str, Any]
)
async def get_stage2_problems() -> Dict[str, Any]:
    """2단계 예제풀이 문제 조회"""
    try:
        mongo_client = get_mongo_client()

        # 2단계 문제 데이터 조회
        stage2_data = mongo_client.find_one("stage2_problems", {"lesson_id": "lesson1"})

        if not stage2_data:
            raise HTTPException(status_code=404, detail="2단계 문제 데이터를 찾을 수 없습니다")

        logger.info(f"✅ 2단계 문제 {stage2_data['total_problems']}개 조회 완료")

        return {
            "success": True,
            "lesson_id": stage2_data["lesson_id"],
            "title": stage2_data["title"],
            "instruction": stage2_data["instruction"],
            "total_problems": stage2_data["total_problems"],
            "answer_options": stage2_data["answer_options"],
            "problems": stage2_data["problems"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 2단계 문제 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="2단계 문제 조회에 실패했습니다")


@router.get(
    "/images/{filename}",
    summary="이미지 파일 서빙",
    description="""
## API 설명
학습에 사용되는 이미지 파일(카드, 문제 이미지 등)을 서빙합니다.

## 프론트엔드 구현 가이드
- **이미지 URL**: `/learning/images/{filename}` 형태로 접근
- **에러 처리**: 이미지 로드 실패 시 기본 이미지 표시
- **성능 최적화**: 필요한 이미지 미리 로드 권장

## 사용 예시
- 카드 이미지: `/learning/images/card1_front.png`
- 문제 이미지: `/learning/images/stage3/problem_1.png`
    """
)
async def get_image(filename: str):
    """이미지 파일 서빙"""
    try:
        # 이미지 파일 경로
        image_path = f"/app/static/images/cards/{filename}"

        # 파일 존재 확인
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다")

        # 파일 확장자에 따른 media_type 설정
        if filename.lower().endswith('.png'):
            media_type = "image/png"
        elif filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            media_type = "image/jpeg"
        elif filename.lower().endswith('.svg'):
            media_type = "image/svg+xml"
        else:
            media_type = "application/octet-stream"

        return FileResponse(
            path=image_path,
            media_type=media_type,
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 이미지 서빙 실패: {e}")
        raise HTTPException(status_code=500, detail="이미지 로딩에 실패했습니다")