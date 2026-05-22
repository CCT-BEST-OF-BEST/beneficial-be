from fastapi import APIRouter, Depends, HTTPException, status

from app.domains.agent.repository import ChatSessionRepository
from app.domains.agent.schemas import (
    AgentChatRequest,
    AgentChatResponse,
    AgentProfileResponse,
    ChatSessionResponse,
    WeakConceptResponse,
)
from app.domains.agent.service import AgentService, ChatSessionService
from app.domains.auth.dependencies import get_current_user
from app.domains.auth.models import User
from app.domains.learning.dependencies import get_learning_record_service
from app.domains.learning.service import LearningRecordService
from app.domains.rag.retriever import RagRetriever
from app.domains.rag.service import RagService
from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.infrastructure.external.openai_client import get_openai_client

router = APIRouter(prefix="/agent", tags=["agent"])


def get_chat_session_service() -> ChatSessionService:
    return ChatSessionService(ChatSessionRepository(get_mongo_client()))


def get_agent_service(
    session_service: ChatSessionService = Depends(get_chat_session_service),
    learning_record_service: LearningRecordService = Depends(get_learning_record_service),
) -> AgentService:
    rag_service = RagService(retriever=RagRetriever(), openai_client=get_openai_client())
    return AgentService(
        session_service=session_service,
        rag_service=rag_service,
        learning_record_service=learning_record_service,
        openai_client=get_openai_client(),
    )


@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(
    body: AgentChatRequest,
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
):
    result = await agent_service.chat(
        user_id=current_user.user_id,
        message=body.message,
        session_id=body.session_id,
    )
    return AgentChatResponse(**result)


@router.get("/session/{session_id}", response_model=ChatSessionResponse)
def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    session_service: ChatSessionService = Depends(get_chat_session_service),
):
    session = session_service.get(session_id, current_user.user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="세션을 찾을 수 없습니다.",
        )
    return ChatSessionResponse(**session.model_dump())


@router.delete("/session/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    session_service: ChatSessionService = Depends(get_chat_session_service),
):
    deleted = session_service.delete(session_id, current_user.user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="세션을 찾을 수 없습니다.",
        )


@router.get("/profile/me", response_model=AgentProfileResponse)
def get_my_agent_profile(
    current_user: User = Depends(get_current_user),
    learning_record_service: LearningRecordService = Depends(get_learning_record_service),
):
    profile = learning_record_service.get_weakness_profile(current_user.user_id)
    return AgentProfileResponse(
        user_id=profile.user_id,
        weak_concepts=[
            WeakConceptResponse(**wc.model_dump()) for wc in profile.weak_concepts
        ],
    )
