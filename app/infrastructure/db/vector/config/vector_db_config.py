"""
1. 중앙 집중식 설정 관리: 모든 벡터 DB 관련 설정을 한 곳에서 관리
2. 환경 변수 지원: .env 파일을 통한 설정 오버라이드
3. 컬렉션별 메타데이터: 각 컬렉션의 특성에 맞는 설정
4. 검색 설정: 유사도 임계값, 기본 검색 개수 등
"""

import os

from pathlib import Path


class VectorDBConfig:
    """벡터 DB 설정 클래스"""

    # 기본 설정
    DEFAULT_PERSIST_DIRECTORY = "./chroma_db"
    DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    # 컬렉션 설정
    COLLECTIONS = {
        "korean_word_problems": {
            "description": "한국어 단어 문제 데이터",
            "metadata": {
                "type": "educational",
                "language": "korean",
                "category": "word_problems"
            }
        },
        "card_check": {
            "description": "카드 체크 데이터",
            "metadata": {
                "type": "educational",
                "language": "korean",
                "category": "vocabulary"
            }
        }
    }

    # ChromaDB 설정
    CHROMA_SETTINGS = {
        "anonymized_telemetry": False,
        "allow_reset": True,
        "is_persistent": True
    }

    # 검색 설정
    SEARCH_CONFIG = {
        "default_top_k": 3,
        "max_top_k": 10,
        "similarity_threshold": 0.7
    }

    @classmethod
    def get_persist_directory(cls):
        """저장 디렉토리를 반환합니다."""
        return os.getenv("CHROMA_PERSIST_DIR", cls.DEFAULT_PERSIST_DIRECTORY)

    @classmethod
    def get_embedding_model(cls):
        """임베딩 모델명을 반환합니다."""
        return os.getenv("EMBEDDING_MODEL", cls.DEFAULT_EMBEDDING_MODEL)

    @classmethod
    def get_collection_config(cls, collection_name: str):
        """특정 컬렉션의 설정을 반환합니다."""
        return cls.COLLECTIONS.get(collection_name, {})

    @classmethod
    def get_chroma_settings(cls):
        """ChromaDB 설정을 반환합니다."""
        return cls.CHROMA_SETTINGS

    @classmethod
    def get_search_config(cls):
        """검색 설정을 반환합니다."""
        return cls.SEARCH_CONFIG