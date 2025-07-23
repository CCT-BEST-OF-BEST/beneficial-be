from fastapi import APIRouter, HTTPException
from app.api.chat.service.chat_service import get_chat_service
from app.data.models.chat_models import ChatRequest, ChatResponse, SearchRequest, SearchResponse, ChatStatusResponse
from typing import Optional

router = APIRouter(prefix="/chat", tags=["chat"])


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
        chat_service = get_chat_service()  # 새로운 Chat 서비스 사용
        response = await chat_service.chat_with_rag(
            prompt=request.prompt,  # 사용자 질문
            collection_name=request.collection_name,  # 모든 컬렉션 검색
            top_k=request.top_k  # 상위 3개 문서 검색
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
        chat_service = get_chat_service()  # 새로운 Chat 서비스 사용
        response = await chat_service.chat_with_rag(
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
        chat_service = get_chat_service()  # 새로운 Chat 서비스 사용
        results = await chat_service.search_relevant_documents(query, collection_name, top_k)

        return SearchResponse(
            status="success",
            query=query,
            results=results,
            total_found=len(results),
            collection_searched=collection_name or "all"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 검색 실패: {str(e)}")


@router.get("/status")
async def get_chat_status():
    """채팅 시스템 상태를 확인합니다. (프론트엔드용)"""
    try:
        chat_service = get_chat_service()  # 새로운 Chat 서비스 사용
        vector_db = chat_service.vector_db

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

        return ChatStatusResponse(
            status="success",
            chat_system="active",
            rag_system="available",
            collections=collections_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 확인 실패: {str(e)}")


@router.get("/simple")
async def simple_chat(prompt: str = "안녕하세요"):
    """
    RAG 없이 간단한 채팅 (테스트용)

    Args:
        prompt: 사용자 질문

    Returns:
        GPT 응답
    """
    try:
        chat_service = get_chat_service()
        response = await chat_service.simple_chat(prompt)

        return {
            "status": "success",
            "prompt": prompt,
            "response": response,
            "type": "simple_chat"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"간단 채팅 실패: {str(e)}")