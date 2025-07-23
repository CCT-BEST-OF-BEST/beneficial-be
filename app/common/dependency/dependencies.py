"""
의존성 주입을 위한 팩토리 함수들
각 서비스의 인스턴스를 중앙에서 관리
"""
import os
from typing import Optional
from app.infrastructure.external.openai_client import OpenAIClient
from app.infrastructure.db.vector.vector_db import get_vector_db
from app.infrastructure.embedding.embedding_model import get_embedding_model
from app.api.chat.service.chat_service import ChatService


# 전역 인스턴스들
_openai_client: Optional[OpenAIClient] = None
_chat_service: Optional[ChatService] = None
_vector_db = None
_embedding_model = None


def get_openai_client() -> OpenAIClient:
    """OpenAI 클라이언트 인스턴스 반환 (싱글톤)"""
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        _openai_client = OpenAIClient(api_key=api_key)
    return _openai_client


def get_vector_db_instance():
    """벡터 DB 인스턴스 반환 (싱글톤)"""
    global _vector_db
    if _vector_db is None:
        _vector_db = get_vector_db()
    return _vector_db


def get_embedding_model_instance():
    """임베딩 모델 인스턴스 반환 (싱글톤)"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = get_embedding_model()
    return _embedding_model


def get_chat_service() -> ChatService:
    """Chat 서비스 인스턴스 반환 (싱글톤)"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService(
            openai_client=get_openai_client(),
            vector_db=get_vector_db_instance(),
            embedding_model=get_embedding_model_instance()
        )
    return _chat_service


def reset_dependencies():
    """의존성 인스턴스들을 리셋 (테스트용)"""
    global _openai_client, _chat_service, _vector_db, _embedding_model
    _openai_client = None
    _chat_service = None
    _vector_db = None
    _embedding_model = None


def initialize_dependencies():
    """모든 의존성을 초기화"""
    try:
        # 각 의존성을 미리 초기화
        get_openai_client()
        get_vector_db_instance()
        get_embedding_model_instance()
        get_chat_service()
        print("✅ 모든 의존성 초기화 완료")
    except Exception as e:
        print(f"❌ 의존성 초기화 실패: {e}")
        raise