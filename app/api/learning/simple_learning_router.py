# beneficial-be/app/api/learning/simple_learning_router.py

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
    description="8개의 카드 이미지 경로를 순서대로 반환합니다."
)
async def get_stage1_cards() -> Dict[str, Any]:
    """1단계 어휘학습 카드 8개 조회"""
    try:
        mongo_client = get_mongo_client()
        
        # 카드 데이터 조회 (order 순으로 정렬)
        cards = list(mongo_client.find_many(
            "stage1_cards", 
            {},
            sort=[("order", 1)]
        ))
        
        if not cards:
            raise HTTPException(status_code=404, detail="카드 데이터를 찾을 수 없습니다")
        
        # 응답 데이터 구성 (이미지 경로만)
        cards_response = []
        for card in cards:
            cards_response.append({
                "card_id": card["card_id"],
                "front_image": card["front_image"],
                "back_image": card["back_image"],
                "order": card["order"]
            })
        
        logger.info(f"✅ 1단계 카드 {len(cards_response)}개 조회 완료")
        
        return {
            "success": True,
            "total_cards": len(cards_response),
            "cards": cards_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 1단계 카드 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="카드 조회에 실패했습니다")

@router.get(
    "/images/{filename}",
    summary="이미지 파일 서빙",
    description="카드 이미지 파일을 반환합니다."
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