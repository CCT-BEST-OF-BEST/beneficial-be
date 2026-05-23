from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class WeakConceptResponse(BaseModel):
    concept_key: str
    wrong_count: int
    last_wrong_at: datetime
    priority: float


class AgentProfileResponse(BaseModel):
    user_id: str
    weak_concepts: List[WeakConceptResponse] = Field(default_factory=list)


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
