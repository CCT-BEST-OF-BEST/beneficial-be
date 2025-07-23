from fastapi import APIRouter, HTTPException
from app.api.chat.service.chat_service import get_chat_service
from app.data.models.chat_models import ChatRequest, ChatResponse, ChatStatusResponse
from app.common.logging.logging_config import get_logger

router = APIRouter(prefix="/chat", tags=["chat"])
logger = get_logger(__name__)


@router.post("/", response_model=ChatResponse, summary="RAG 시스템을 사용한 채팅")
async def chat_with_rag(request: ChatRequest):
    """
    RAG 시스템을 사용하여 GPT와 대화합니다. (초등학생 돌봄반용)

    Args:
        request: 채팅 요청 (질문만 필요)

    Returns:
        GPT 응답
    """
    try:
        # 내부 기본값 설정
        top_k = 5
        collection_name = None  # 전체 컬렉션 검색
        
        logger.info(f"📨 채팅 요청 수신: '{request.prompt}' (top_k={top_k})")
        
        chat_service = get_chat_service()
        response = await chat_service.chat_with_rag(
            prompt=request.prompt,
            collection_name=collection_name,
            top_k=top_k
        )

        logger.info(f"✅ 채팅 응답 완료: {len(response)}자")
        
        return ChatResponse(
            status="success",
            prompt=request.prompt,
            response=response,
            collection_used=collection_name or "all",
            top_k=top_k
        )
    except Exception as e:
        logger.error(f"❌ 채팅 요청 실패: {e}")
        raise HTTPException(status_code=500, detail=f"채팅 실패: {str(e)}")


@router.get("/status", summary="채팅 시스템 상태 확인(데이터가 어떻게 삽입되어있는지 - (백엔드 상태 확인용이라 딱히 건들 필요는 음슴))")
async def get_chat_status():
    """채팅 시스템 상태를 확인합니다. (시스템 모니터링용)"""
    try:
        chat_service = get_chat_service()
        vector_db = chat_service.vector_db

        # 각 컬렉션의 문서 수 확인 (PDF 컬렉션 포함)
        collections_info = {}
        for collection_name in ["korean_word_problems", "card_check", "pdf_documents"]:
            collection = vector_db.get_collection(collection_name)
            if collection:
                collections_info[collection_name] = {
                    "document_count": collection.count(),
                    "status": "available"
                }
            else:
                collections_info[collection_name] = {
                    "document_count": 0,
                    "status": "not_available"
                }

        return ChatStatusResponse(
            status="success",
            chat_system="active",
            rag_system="available",
            collections=collections_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 확인 실패: {str(e)}")