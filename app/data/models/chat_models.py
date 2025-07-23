from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    prompt: str = Field(..., description="사용자 질문")
    collection_name: Optional[str] = Field(None, description="검색할 컬렉션명 (None이면 모든 컬렉션)")
    top_k: Optional[int] = Field(3, description="참조할 문서 수")


class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    status: str = Field(..., description="응답 상태")
    prompt: str = Field(..., description="원본 질문")
    response: str = Field(..., description="GPT 응답")
    collection_used: str = Field(..., description="사용된 컬렉션")
    top_k: int = Field(..., description="참조한 문서 수")


class SearchRequest(BaseModel):
    """문서 검색 요청 모델"""
    query: str = Field(..., description="검색할 질문")
    collection_name: Optional[str] = Field(None, description="검색할 컬렉션명")
    top_k: Optional[int] = Field(3, description="반환할 문서 수")


class SearchResponse(BaseModel):
    """문서 검색 응답 모델"""
    status: str = Field(..., description="응답 상태")
    query: str = Field(..., description="원본 검색어")
    results: List[Dict[str, Any]] = Field(..., description="검색 결과")
    total_found: int = Field(..., description="찾은 문서 수")
    collection_searched: str = Field(..., description="검색한 컬렉션")


class ChatStatusResponse(BaseModel):
    """채팅 시스템 상태 응답 모델"""
    status: str = Field(..., description="응답 상태")
    chat_system: str = Field(..., description="채팅 시스템 상태")
    rag_system: str = Field(..., description="RAG 시스템 상태")
    collections: Dict[str, Dict[str, Any]] = Field(..., description="컬렉션 정보")