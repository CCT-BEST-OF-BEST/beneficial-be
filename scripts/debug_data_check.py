#!/usr/bin/env python3
"""
데이터베이스 내용 확인 및 RAG 시스템 디버깅 스크립트
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.common.dependency.dependencies import get_vector_db, get_embedding_model
from app.data.data_loader.korean_word_problems_loader import get_korean_word_problems
from app.data.data_loader.card_check_loader import get_card_check_data
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)

async def check_database_contents():
    """데이터베이스 내용 확인"""
    print("\n" + "="*60)
    print("🔍 데이터베이스 내용 확인")
    print("="*60)
    
    # 1. MongoDB 데이터 확인
    print("\n📊 MongoDB 데이터 확인:")
    print("-" * 40)
    
    # 한국어 단어 문제 데이터
    korean_data = get_korean_word_problems()
    print(f"한국어 단어 문제: {len(korean_data.get('questions', []))}개 문제")
    if korean_data.get('questions'):
        print("예시 문제:")
        for i, q in enumerate(korean_data['questions'][:3]):
            print(f"  {i+1}. 문제 {q['number']}: {q['sentence']}")
            print(f"     정답: {q['answer']}")
    
    # 카드 체크 데이터
    card_data = get_card_check_data()
    print(f"\n카드 체크: {len(card_data)}개 카드")
    if card_data:
        print("예시 카드:")
        for i, card in enumerate(card_data[:3]):
            print(f"  {i+1}. 단어: {card['word']}")
            print(f"     의미: {card['meaning']}")
            if card.get('examples'):
                print(f"     예시: {', '.join(card['examples'])}")
    
    # 2. 벡터 DB 내용 확인
    print("\n\n📚 벡터 DB 내용 확인:")
    print("-" * 40)
    
    vector_db = get_vector_db()
    
    for collection_name in ["korean_word_problems", "card_check"]:
        collection = vector_db.get_collection(collection_name)
        if collection:
            count = collection.count()
            print(f"\n{collection_name}: {count}개 문서")
            
            if count > 0:
                # 모든 문서 조회
                all_docs = collection.get()
                print(f"  문서 예시 (처음 3개):")
                for i, (doc, metadata) in enumerate(zip(all_docs['documents'][:3], all_docs['metadatas'][:3])):
                    print(f"    {i+1}. ID: {all_docs['ids'][i]}")
                    print(f"       내용: {doc[:100]}...")
                    print(f"       메타데이터: {metadata}")
        else:
            print(f"\n{collection_name}: 컬렉션을 찾을 수 없음")

async def debug_rag_search():
    """RAG 검색 디버깅"""
    print("\n\n" + "="*60)
    print("🔍 RAG 검색 테스트")
    print("="*60)
    
    vector_db = get_vector_db()
    embedding_model = get_embedding_model()
    
    # 테스트 쿼리들
    test_queries = [
        "되다 와 돼다의 차이가 뭐야?",
        "한국어 동사 활용",
        "맞히다와 맞추다의 차이",
        "가르치다와 가르키다의 차이"
    ]
    
    for query in test_queries:
        print(f"\n🔍 쿼리: '{query}'")
        print("-" * 50)
        
        try:
            # 임베딩 생성
            query_embedding = await embedding_model.get_embedding(query)
            print(f"임베딩 생성 완료: {len(query_embedding)}차원")
            
            # 각 컬렉션에서 검색
            for collection_name in ["korean_word_problems", "card_check"]:
                collection = vector_db.get_collection(collection_name)
                if collection:
                    print(f"\n📂 {collection_name} 컬렉션 검색 결과:")
                    
                    search_results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=3
                    )
                    
                    for i, (doc, metadata, distance) in enumerate(zip(
                        search_results['documents'][0],
                        search_results['metadatas'][0],
                        search_results['distances'][0]
                    )):
                        similarity = round(1 - distance, 4)
                        print(f"  {i+1}. 유사도: {similarity}")
                        print(f"     내용: {doc[:100]}...")
                        print(f"     메타데이터: {metadata}")
                else:
                    print(f"⚠️ {collection_name} 컬렉션을 찾을 수 없음")
                    
        except Exception as e:
            print(f"❌ 검색 실패: {e}")

async def main():
    """메인 함수"""
    print("🚀 RAG 시스템 디버깅 시작")
    
    try:
        # 1. 데이터베이스 내용 확인
        await check_database_contents()
        
        # 2. RAG 검색 테스트
        await debug_rag_search()
        
        print("\n\n✅ 디버깅 완료!")
        
    except Exception as e:
        print(f"\n❌ 디버깅 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 