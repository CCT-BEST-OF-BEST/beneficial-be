import secrets
from typing import List, Optional

from app.common.security import utc_now
from app.domains.agent.models import AgentDecision, ChatMessage, ChatSession
from app.domains.agent.repository import ChatSessionRepository
from app.domains.learning.models import StudentWeaknessProfile
from app.domains.learning.service import LearningRecordService


INTERVENTION_COOLDOWN_TURNS = 3  # proactive hint 사이 최소 assistant 턴 수
RECENT_TURNS = 10                 # Agent가 참조할 최근 대화 수


class ChatSessionService:
    def __init__(self, repository: ChatSessionRepository):
        self.repository = repository

    def get_or_create(self, user_id: str, session_id: Optional[str]) -> ChatSession:
        if session_id:
            doc = self.repository.find_by_session_id(session_id)
            if doc and doc.get("user_id") == user_id:
                return ChatSession(**doc)

        now = utc_now()
        session = ChatSession(
            session_id=f"sess_{secrets.token_urlsafe(16)}",
            user_id=user_id,
            messages=[],
            created_at=now,
            updated_at=now,
        )
        self.repository.create(session.model_dump())
        return session

    def get(self, session_id: str, user_id: str) -> Optional[ChatSession]:
        doc = self.repository.find_by_session_id(session_id)
        if doc and doc.get("user_id") == user_id:
            return ChatSession(**doc)
        return None

    def append_message(self, session: ChatSession, message: ChatMessage) -> ChatSession:
        session.messages.append(message)
        session.updated_at = utc_now()

        if message.role == "assistant" and message.agent_action:
            session.last_agent_action = message.agent_action
            if message.agent_action in ("proactive_hint", "answer_with_rag"):
                session.last_intervention_at = message.created_at

        self.repository.update_session(
            session.session_id,
            [m.model_dump() for m in session.messages],
            session.updated_at,
            session.last_agent_action,
            session.last_intervention_at,
        )
        return session

    def get_recent_messages(self, session: ChatSession) -> List[ChatMessage]:
        return session.messages[-RECENT_TURNS:]

    def delete(self, session_id: str, user_id: str) -> bool:
        doc = self.repository.find_by_session_id(session_id)
        if not doc or doc.get("user_id") != user_id:
            return False
        return self.repository.delete(session_id)


class AgentService:
    def __init__(
        self,
        session_service: ChatSessionService,
        rag_service,
        learning_record_service: LearningRecordService,
        openai_client,
    ):
        self.session_service = session_service
        self.rag_service = rag_service
        self.learning_record_service = learning_record_service
        self.openai_client = openai_client

    async def chat(
        self,
        user_id: str,
        message: str,
        session_id: Optional[str] = None,
    ) -> dict:
        session = self.session_service.get_or_create(user_id, session_id)
        weakness_profile = self.learning_record_service.get_weakness_profile(user_id)

        user_msg = ChatMessage(role="user", content=message, created_at=utc_now())
        session = self.session_service.append_message(session, user_msg)

        recent = self.session_service.get_recent_messages(session)
        decision = self._decide(message, weakness_profile, recent)

        rag_context = ""
        used_tools: List[str] = []
        if decision.should_use_rag:
            search_result = await self.rag_service.search(message)
            rag_context = search_result.context
            used_tools.append("rag_search")

        system_prompt = self._build_system_prompt(weakness_profile, decision)
        response_text = await self.openai_client.generate_response_with_context(
            prompt=message,
            context=rag_context or None,
            system_prompt=system_prompt,
        )

        assistant_msg = ChatMessage(
            role="assistant",
            content=response_text,
            agent_action=decision.action,
            target_concept=decision.target_concept,
            used_tools=used_tools,
            created_at=utc_now(),
        )
        session = self.session_service.append_message(session, assistant_msg)

        return {
            "session_id": session.session_id,
            "response": response_text,
            "agent_action": decision.action,
            "target_concept": decision.target_concept,
            "used_tools": used_tools,
            "weak_concepts": [wc.concept_key for wc in weakness_profile.weak_concepts],
        }

    def _decide(
        self,
        message: str,
        weakness_profile: StudentWeaknessProfile,
        recent_messages: List[ChatMessage],
    ) -> AgentDecision:
        if self._is_question(message):
            return AgentDecision(
                action="answer_with_rag",
                should_use_rag=True,
                reason="사용자가 질문을 했습니다.",
            )

        if weakness_profile.weak_concepts and self._should_intervene(recent_messages):
            top_concept = weakness_profile.weak_concepts[0].concept_key
            return AgentDecision(
                action="proactive_hint",
                target_concept=top_concept,
                should_use_rag=True,
                reason=f"약점 개념 '{top_concept}'에 대한 선제 힌트 제공",
            )

        if self._is_positive(message):
            return AgentDecision(
                action="encourage",
                should_use_rag=False,
                reason="학생의 긍정적 반응에 칭찬 및 격려",
            )

        return AgentDecision(
            action="small_talk",
            should_use_rag=False,
            reason="일반 대화 처리",
        )

    def _is_question(self, message: str) -> bool:
        markers = [
            "?", "？", "뭐야", "뭐예요", "왜", "어떻게", "무슨", "어떤",
            "맞아", "맞나", "인가요", "인가", "인지", "알려줘", "설명해",
            "뭐가", "어디", "언제", "누가",
        ]
        return any(m in message for m in markers)

    def _should_intervene(self, recent_messages: List[ChatMessage]) -> bool:
        assistant_turns = [m for m in recent_messages if m.role == "assistant"]
        for i, turn in enumerate(reversed(assistant_turns)):
            if turn.agent_action in ("proactive_hint", "answer_with_rag"):
                return i >= INTERVENTION_COOLDOWN_TURNS
        return True

    def _is_positive(self, message: str) -> bool:
        markers = ["고마워", "감사", "알겠어", "이해했어", "맞아!", "좋아", "완벽"]
        return any(m in message for m in markers)

    def _build_system_prompt(
        self,
        weakness_profile: StudentWeaknessProfile,
        decision: AgentDecision,
    ) -> str:
        weak_str = ""
        if weakness_profile.weak_concepts:
            items = [
                f"{wc.concept_key}({wc.wrong_count}회)"
                for wc in weakness_profile.weak_concepts[:3]
            ]
            weak_str = f"\n- 최근 틀린 개념: {', '.join(items)}"

        hint_instruction = ""
        if decision.action == "proactive_hint" and decision.target_concept:
            hint_instruction = (
                f"\n- 지금 대화에 '{decision.target_concept}' 관련 설명을 자연스럽게 섞어줘."
            )

        return (
            "너는 초등학생 돌봄 선생님이야. "
            "쉽고 친근한 말로 한국어 맞춤법을 가르쳐줘.\n"
            f"[학생 정보]{weak_str}"
            "\n[대화 방침]"
            "\n- 어려운 말은 쓰지 마."
            "\n- 칭찬을 자주 해줘."
            "\n- 설명은 짧고 간단하게."
            f"{hint_instruction}"
        )
