from fastapi import APIRouter, HTTPException
from app.api.system.indexing_service import get_indexing_service

router = APIRouter(prefix="/admin/indexing", tags=["admin"])


@router.get("/status")
async def get_indexing_status():
    """인덱싱 상태를 확인합니다. (관리자 전용)"""
    try:
        indexing_service = get_indexing_service()
        vector_db = indexing_service.vector_db

        status = {}
        for collection_name in ["korean_word_problems", "card_check", "pdf_documents"]:
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