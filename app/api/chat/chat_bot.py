from fastapi import APIRouter, HTTPException
from app.core.rag_service import get_rag_service
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    prompt: str
    collection_name: Optional[str] = None
    top_k: Optional[int] = 3


class ChatResponse(BaseModel):
    status: str
    prompt: str
    response: str
    collection_used: str
    top_k: int


@router.post("/", response_model=ChatResponse)
async def chat_with_rag(request: ChatRequest):
    """
    RAG 시스템을 사용하여 GPT와 대화합니다. (프론트엔드용)

    Args:
        request: 채팅 요청 (질문, 컬렉션명, 검색 문서 수)

    Returns:
        GPT 응답
    """
    try:
        rag_service = await get_rag_service()
        response = await rag_service.chat_with_rag(
            prompt=request.prompt,
            collection_name=request.collection_name,
            top_k=request.top_k
        )

        return ChatResponse(
            status="success",
            prompt=request.prompt,
            response=response,
            collection_used=request.collection_name or "all",
            top_k=request.top_k
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채팅 실패: {str(e)}")


@router.get("/")
async def chat_get(
        prompt: str = "맞히다와 맞추다의 차이 알려줘",
        collection_name: Optional[str] = None,
        top_k: int = 3
):
    """
    RAG 시스템을 사용하여 GPT와 대화합니다. (GET 방식, 프론트엔드용)

    Args:
        prompt: 사용자 질문
        collection_name: 검색할 컬렉션명 (None이면 모든 컬렉션)
        top_k: 참조할 문서 수

    Returns:
        GPT 응답
    """
    try:
        rag_service = await get_rag_service()
        response = await rag_service.chat_with_rag(
            prompt=prompt,
            collection_name=collection_name,
            top_k=top_k
        )

        return {
            "status": "success",
            "prompt": prompt,
            "response": response,
            "collection_used": collection_name or "all",
            "top_k": top_k
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채팅 실패: {str(e)}")


@router.get("/search")
async def search_documents(
        query: str,
        collection_name: Optional[str] = None,
        top_k: int = 3
):
    """
    질문과 관련된 문서를 검색합니다. (프론트엔드용)

    Args:
        query: 검색할 질문
        collection_name: 검색할 컬렉션명 (None이면 모든 컬렉션)
        top_k: 반환할 문서 수

    Returns:
        관련 문서 리스트
    """
    try:
        rag_service = await get_rag_service()
        results = await rag_service.search_relevant_documents(query, collection_name, top_k)

        return {
            "status": "success",
            "query": query,
            "results": results,
            "total_found": len(results),
            "collection_searched": collection_name or "all"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 검색 실패: {str(e)}")


@router.get("/status")
async def get_chat_status():
    """채팅 시스템 상태를 확인합니다. (프론트엔드용)"""
    try:
        rag_service = await get_rag_service()
        vector_db = rag_service.vector_db

        # 각 컬렉션의 문서 수 확인
        collections_info = {}
        for collection_name in ["korean_word_problems", "card_check"]:
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

        return {
            "status": "success",
            "chat_system": "active",
            "rag_system": "available",
            "collections": collections_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 확인 실패: {str(e)}")