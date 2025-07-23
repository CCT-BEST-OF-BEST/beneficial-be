from fastapi import APIRouter, HTTPException
from app.api.system.indexing_service import get_indexing_service

router = APIRouter(prefix="/admin/indexing", tags=["admin"])


@router.post("/korean-word-problems")
async def index_korean_word_problems():
    """한국어 단어 문제 데이터를 벡터 DB에 인덱싱합니다. (관리자 전용)"""
    try:
        indexing_service = get_indexing_service()
        result = await indexing_service.index_korean_word_problems()

        if result["status"] == "success":
            return {
                "status": "success",
                "message": "한국어 단어 문제 데이터 인덱싱 완료",
                "indexed_count": result["indexed_count"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인덱싱 실패: {str(e)}")


@router.post("/card-check")
async def index_card_check_data():
    """카드 체크 데이터를 벡터 DB에 인덱싱합니다. (관리자 전용)"""
    try:
        indexing_service = get_indexing_service()
        result = await indexing_service.index_card_check_data()

        if result["status"] == "success":
            return {
                "status": "success",
                "message": "카드 체크 데이터 인덱싱 완료",
                "indexed_count": result["indexed_count"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인덱싱 실패: {str(e)}")


@router.post("/all")
async def index_all_data():
    """모든 데이터를 벡터 DB에 인덱싱합니다. (관리자 전용)"""
    try:
        indexing_service = get_indexing_service()
        result = await indexing_service.index_all_data()

        return {
            "status": "success",
            "message": "전체 데이터 인덱싱 완료",
            "total_collections": result["total_collections"],
            "successful_collections": result["successful_collections"],
            "results": result["results"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인덱싱 실패: {str(e)}")


@router.delete("/collections/{collection_name}")
async def clear_collection(collection_name: str):
    """특정 컬렉션의 모든 데이터를 삭제합니다. (관리자 전용)"""
    try:
        indexing_service = get_indexing_service()
        result = indexing_service.clear_collection(collection_name)

        if result["status"] == "success":
            return {
                "status": "success",
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"컬렉션 삭제 실패: {str(e)}")


@router.get("/status")
async def get_indexing_status():
    """인덱싱 상태를 확인합니다. (관리자 전용)"""
    try:
        indexing_service = get_indexing_service()
        vector_db = indexing_service.vector_db

        status = {}
        for collection_name in ["korean_word_problems", "card_check"]:
            collection = vector_db.get_collection(collection_name)
            if collection:
                status[collection_name] = {
                    "document_count": collection.count(),
                    "status": "available"
                }
            else:
                status[collection_name] = {
                    "document_count": 0,
                    "status": "not_available"
                }

        return {
            "status": "success",
            "indexing_status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 확인 실패: {str(e)}")