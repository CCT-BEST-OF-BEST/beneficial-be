from typing import List, Dict, Any
from app.infrastructure.external.openai_client import OpenAIClient
from app.infrastructure.db.vector.vector_db import get_vector_db
from app.infrastructure.embedding.embedding_model import get_embedding_model


class ChatService:
    """사용자 채팅 서비스 (RAG 포함)"""

    def __init__(self, openai_client: OpenAIClient = None,
                 vector_db=None, embedding_model=None):
        # 의존성 주입 또는 기본값 사용
        self.openai_client = openai_client or OpenAIClient()
        self.vector_db = vector_db or get_vector_db()
        self.embedding_model = embedding_model or get_embedding_model()

        self.default_system_prompt = """너는 초등학생 돌봄선생님이야. 
    주어진 참고 자료를 바탕으로 정확하고 친근하게 답변해줘.
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
            # 1. 관련 문서 검색
            relevant_docs = await self.search_relevant_documents(prompt, collection_name, top_k)

            # 2. 컨텍스트 구성
            context = self.build_context_from_documents(relevant_docs)

            # 3. GPT 응답 생성
            response = await self.generate_response_with_context(prompt, context)

            return response

        except Exception as e:
            return f"죄송합니다. 채팅 처리 중 오류가 발생했습니다: {str(e)}"

    async def search_relevant_documents(self, query: str, collection_name: str = None, top_k: int = 3) -> List[
        Dict[str, Any]]:
        """관련 문서 검색"""
        try:
            query_embedding = await self.embedding_model.get_embedding(query)
            results = []

            # 검색할 컬렉션 결정
            if collection_name:
                collections = [collection_name]
            else:
                collections = ["korean_word_problems", "card_check"]

            # 각 컬렉션에서 검색
            for coll_name in collections:
                collection = self.vector_db.get_collection(coll_name)
                if collection:
                    search_results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=top_k
                    )

                    for i in range(len(search_results['documents'][0])):
                        results.append({
                            'document': search_results['documents'][0][i],
                            'metadata': search_results['metadatas'][0][i],
                            'distance': search_results['distances'][0][i],
                            'collection': coll_name
                        })

            # 유사도 순으로 정렬
            results.sort(key=lambda x: x['distance'])
            return results[:top_k]

        except Exception as e:
            print(f"문서 검색 실패: {e}")
            return []


    async def generate_response_with_context(self, prompt: str, context: str) -> str:
        """컨텍스트와 함께 GPT 응답 생성"""
        try:
            return await self.openai_client.generate_response_with_context(
                prompt=prompt,
                context=context,
                system_prompt=self.default_system_prompt
            )
        except Exception as e:
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"


    def build_context_from_documents(self, documents: List[Dict[str, Any]]) -> str:
        """문서 리스트를 컨텍스트로 변환"""
        if not documents:
            return "참고 자료가 없습니다."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"{i}. {doc.get('document', doc.get('text', ''))}")

        return "\n".join(context_parts)


    async def simple_chat(self, prompt: str) -> str:
        """
        RAG 없이 간단한 채팅 (테스트용)

        Args:
            prompt: 사용자 질문

        Returns:
            GPT 응답
        """
        try:
            messages = [
                {"role": "system", "content": self.default_system_prompt},
                {"role": "user", "content": prompt}
            ]
            return await self.openai_client.chat_completion(messages)
        except Exception as e:
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"


def get_chat_service() -> ChatService:
    """Chat 서비스 인스턴스 반환"""
    return ChatService()