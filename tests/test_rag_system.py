#!/usr/bin/env python3
"""
RAG 시스템 테스트
"""
import pytest
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pytest-asyncio는 pytest.ini에서 설정

from app.common.dependency.dependencies import get_vector_db, get_embedding_model
from app.api.chat.service.chat_service import get_chat_service


@pytest.mark.asyncio
async def test_vector_db_connection():
    """벡터 DB 연결 테스트"""
    vector_db = get_vector_db()
    assert vector_db is not None
    
    # 컬렉션 확인
    korean_collection = vector_db.get_collection("korean_word_problems")
    card_collection = vector_db.get_collection("card_check")
    
    assert korean_collection is not None
    assert card_collection is not None


@pytest.mark.asyncio
async def test_embedding_model():
    """임베딩 모델 테스트"""
    embedding_model = get_embedding_model()
    assert embedding_model is not None
    
    # 임베딩 생성 테스트
    test_text = "테스트 문장입니다."
    embedding = await embedding_model.get_embedding(test_text)
    
    assert len(embedding) > 0
    assert isinstance(embedding, list)
    assert all(isinstance(x, (int, float)) for x in embedding)


@pytest.mark.asyncio
async def test_chat_service():
    """채팅 서비스 테스트"""
    chat_service = get_chat_service()
    assert chat_service is not None
    
    # 간단한 채팅 테스트
    response = await chat_service.simple_chat("안녕하세요")
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_rag_search():
    """RAG 검색 테스트"""
    chat_service = get_chat_service()
    
    # 문서 검색 테스트
    documents = await chat_service.search_relevant_documents(
        query="맞히다와 맞추다의 차이",
        top_k=3
    )
    
    assert isinstance(documents, list)
    assert len(documents) <= 3
    
    if documents:
        # 문서 구조 확인
        doc = documents[0]
        assert 'document' in doc
        assert 'metadata' in doc
        assert 'distance' in doc
        assert 'collection' in doc


@pytest.mark.asyncio
async def test_rag_chat():
    """RAG 채팅 테스트"""
    chat_service = get_chat_service()
    
    # RAG 채팅 테스트
    response = await chat_service.chat_with_rag(
        prompt="맞히다와 맞추다의 차이를 알려주세요",
        top_k=3
    )
    
    assert isinstance(response, str)
    assert len(response) > 0 