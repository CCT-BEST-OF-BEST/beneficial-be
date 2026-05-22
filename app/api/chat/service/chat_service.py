from typing import List, Dict, Any
from app.infrastructure.external.openai_client import OpenAIClient
from app.infrastructure.db.vector.vector_db import get_vector_db
from app.infrastructure.embedding.embedding_model import get_embedding_model
from app.infrastructure.search.hybrid_search import get_hybrid_search_service
from app.domains.rag.retriever import RagRetriever
from app.domains.rag.service import RagService
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)


class ChatService:
    """사용자 채팅 서비스 (하이브리드 RAG: BM25 + Dense + RRF)"""

    def __init__(self, openai_client: OpenAIClient = None,
                 vector_db=None, embedding_model=None):
        self.openai_client = openai_client or OpenAIClient()
        self.vector_db = vector_db or get_vector_db()
        self.embedding_model = embedding_model or get_embedding_model()
        self.hybrid_search = get_hybrid_search_service()
        self.rag_service = RagService(
            retriever=RagRetriever(self.hybrid_search),
            openai_client=self.openai_client,
        )

        self.default_system_prompt = """너는 초등학생 돌봄선생님이야. 
    주어진 참고 자료를 바탕으로 정확하고 친근하게 답변해줘.
    
    “너는 아이들에게 친절하게 알려주는 튜터야. 말투는 친구처럼 다정한 반말로 이야기해줘. 아이가 어려워하면 ’괜찮아~ 같이 해보자!’처럼 격려해주고, 궁금해하는 건 천천히 쉽게 풀어서 알려줘. 어려운 말은 쓰지 말고, 마치 옆에서 얘기해주는 것처럼 말해줘.”

⸻

추가 포인트 문구 (선택적으로 덧붙여도 좋아)
    •    “문장은 길지 않게 짧고 귀엽게 말해줘.”
    •    “아이랑 대화하는 것처럼 질문도 해줘.”
    •    “칭찬도 자주 해줘. 예를 들면, ‘오~ 잘했어!’ 같은 느낌으로.”

    
    참고 자료에 없는 내용은 일반적인 지식으로 답변하되, 
    참고 자료가 있으면 그것을 우선적으로 활용해줘."""

    async def chat_with_rag(self, prompt: str, collection_name: str = None, top_k: int = 3) -> str:
        """
        사용자 채팅 - RAG 시스템 자동 실행

        Args:
            prompt: 사용자 질문
            collection_name: 검색할 컬렉션명 (None이면 모든 컬렉션)
            top_k: 참조할 문서 수

        Returns:
            GPT 응답
        """
        try:
            logger.info(f"🔍 RAG 채팅 시작: '{prompt}' (top_k={top_k}, collection={collection_name or 'all'})")
            
            response = await self.rag_service.answer(
                query=prompt,
                system_prompt=self.default_system_prompt,
                collection_name=collection_name,
                top_k=top_k,
            )
            logger.info(f" GPT 응답 생성 완료: {len(response)}자")

            return response

        except Exception as e:
            logger.error(f"❌ RAG 채팅 실패: {e}")
            return f"죄송합니다. 채팅 처리 중 오류가 발생했습니다: {str(e)}"

    async def search_relevant_documents(
        self,
        query: str,
        collection_name: str = None,
        top_k: int = 5,
        similarity_threshold: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """BM25 + Dense 하이브리드 검색 (RRF 결합)"""
        try:
            search_result = await self.rag_service.search(
                query=query,
                collection_name=collection_name,
                top_k=top_k,
            )

            return [
                doc.model_dump() if hasattr(doc, "model_dump") else doc.dict()
                for doc in search_result.documents
            ]

        except Exception as e:
            logger.error(f"❌ 하이브리드 검색 실패: {e}")
            return []


    async def generate_response_with_context(self, prompt: str, context: str) -> str:
        """컨텍스트와 함께 GPT 응답 생성"""
        try:
            logger.debug(f" GPT 응답 생성 시작 (컨텍스트 길이: {len(context)}자)")
            
            response = await self.openai_client.generate_response_with_context(
                prompt=prompt,
                context=context,
                system_prompt=self.default_system_prompt
            )
            
            logger.debug(f"✅ GPT 응답 생성 완료: {len(response)}자")
            return response
            
        except Exception as e:
            logger.error(f"❌ GPT 응답 생성 실패: {e}")
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"


    def build_context_from_documents(self, documents: List[Dict[str, Any]]) -> str:
        """문서 리스트를 컨텍스트로 변환"""
        from app.domains.rag.schemas import RagDocument

        rag_documents = [RagDocument(**doc) for doc in documents]
        context = self.rag_service.build_context(rag_documents)
        logger.debug(f" 컨텍스트 구성 완료: {len(documents)}개 문서, {len(context)}자")
        
        return context


    async def simple_chat(self, prompt: str) -> str:
        """
        RAG 없이 간단한 채팅 (테스트용)

        Args:
            prompt: 사용자 질문

        Returns:
            GPT 응답
        """
        try:
            logger.info(f"💬 간단 채팅: '{prompt}'")
            
            messages = [
                {"role": "system", "content": self.default_system_prompt},
                {"role": "user", "content": prompt}
            ]
            response = await self.openai_client.chat_completion(messages)
            
            logger.info(f"✅ 간단 채팅 완료: {len(response)}자")
            return response
            
        except Exception as e:
            logger.error(f"❌ 간단 채팅 실패: {e}")
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"

    def _is_korean_grammar_query(self, query: str) -> bool:
        """한글 문법 관련 질문인지 판단 (초등학생이 자주 묻는 것들)"""
        korean_grammar_keywords = [
            "맞춤법", "띄어쓰기", "된소리", "외래어", "발음", "표기",
            "자음", "모음", "받침", "어간", "어미",
            "되다", "돼다", "하다", "해다", "되", "돼",
            "맞나요", "틀렸나요", "어떻게 써요", "헷갈려요",
            "구분", "차이", "올바른", "바른", "어느게", "뭐가"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in korean_grammar_keywords)


def get_chat_service() -> ChatService:
    """Chat 서비스 인스턴스 반환"""
    return ChatService()
