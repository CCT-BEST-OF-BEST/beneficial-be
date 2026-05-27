from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.domains.progress.schema.schemas import WeakConceptResponse, StudentWeaknessProfileResponse

# progress 도메인 스키마를 agent 라우터에서도 쓸 수 있도록 re-export
AgentProfileResponse = StudentWeaknessProfileResponse


class AgentChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class AgentChatResponse(BaseModel):
    session_id: str
    response: str
    agent_action: str
    target_concept: Optional[str] = None
    used_tools: List[str] = Field(default_factory=list)
    weak_concepts: List[str] = Field(default_factory=list)


class ChatMessageResponse(BaseModel):
    role: str
    content: str
    agent_action: Optional[str] = None
    target_concept: Optional[str] = None
    used_tools: List[str] = Field(default_factory=list)
    created_at: datetime


class ChatSessionResponse(BaseModel):
    session_id: str
    user_id: str
    messages: List[ChatMessageResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    last_agent_action: Optional[str] = None


class ChatRequest(BaseModel):
    prompt: str = Field(..., description="사용자 질문")


class ChatResponse(BaseModel):
    status: str = Field(..., description="응답 상태")
    prompt: str = Field(..., description="원본 질문")
    response: str = Field(..., description="GPT 응답")
    collection_used: str = Field(..., description="사용된 컬렉션")
    top_k: int = Field(..., description="참조한 문서 수")


class ChatStatusResponse(BaseModel):
    status: str = Field(..., description="응답 상태")
    chat_system: str = Field(..., description="채팅 시스템 상태")
    rag_system: str = Field(..., description="RAG 시스템 상태")
    collections: Dict[str, Dict[str, Any]] = Field(..., description="컬렉션 정보")
