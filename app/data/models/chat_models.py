from pydantic import BaseModel, Field
from typing import Dict, Any


class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    prompt: str = Field(..., description="사용자 질문")


class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    status: str = Field(..., description="응답 상태")
    prompt: str = Field(..., description="원본 질문")
    response: str = Field(..., description="GPT 응답")
    collection_used: str = Field(..., description="사용된 컬렉션")
    top_k: int = Field(..., description="참조한 문서 수")


class ChatStatusResponse(BaseModel):
    """채팅 시스템 상태 응답 모델"""
    status: str = Field(..., description="응답 상태")
    chat_system: str = Field(..., description="채팅 시스템 상태")
    rag_system: str = Field(..., description="RAG 시스템 상태")
    collections: Dict[str, Dict[str, Any]] = Field(..., description="컬렉션 정보")