#!/usr/bin/env python3
"""
벡터 DB 초기화 및 테스트 스크립트
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.vector_db import initialize_vector_db, get_vector_db
from app.common.config.vector_db_config import VectorDBConfig


def test_vector_db_initialization():
    """벡터 DB 초기화 및 기본 기능을 테스트합니다."""
    print("🚀 벡터 DB 초기화 테스트 시작...")

    try:
        # 1. 설정 확인
        print("📋 설정 확인 중...")
        persist_dir = VectorDBConfig.get_persist_directory()
        print(f"   저장 디렉토리: {persist_dir}")

        # 2. 벡터 DB 초기화
        print("📦 벡터 DB 초기화 중...")
        vector_db = initialize_vector_db()

        # 3. 컬렉션 목록 확인
        collections = vector_db.list_collections()
        print(f"✅ 초기화된 컬렉션: {collections}")

        # 4. 각 컬렉션 정보 확인
        print("📊 컬렉션 정보:")
        for collection_name in collections:
            info = vector_db.collection_info(collection_name)
            if info:
                print(f"   - {collection_name}: {info['count']}개 문서")
            else:
                print(f"   - {collection_name}: 정보 조회 실패")

        # 5. 클라이언트 연결 상태 확인
        print("🔗 클라이언트 연결 상태 확인...")
        client = vector_db.client
        print(f"   클라이언트 타입: {type(client).__name__}")
        print(f"   저장 경로: {vector_db.persist_directory}")

        print("🎉 벡터 DB 초기화 테스트 완료!")
        return True

    except Exception as e:
        print(f"❌ 벡터 DB 초기화 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_collection_status():
    """컬렉션 상태를 확인합니다."""
    print("\n🔍 컬렉션 상태 확인...")

    try:
        vector_db = get_vector_db()

        for collection_name in ["korean_word_problems", "card_check"]:
            collection = vector_db.get_collection(collection_name)
            if collection:
                count = collection.count()
                print(f"   {collection_name}: {count}개 문서")

                # 메타데이터 확인
                metadata = collection.metadata
                print(f"     메타데이터: {metadata}")
            else:
                print(f"   {collection_name}: 컬렉션을 찾을 수 없음")

    except Exception as e:
        print(f"❌ 컬렉션 상태 확인 실패: {e}")


def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("벡터 DB 초기화 스크립트")
    print("=" * 50)

    # 초기화 테스트
    success = test_vector_db_initialization()

    if success:
        # 컬렉션 상태 확인
        check_collection_status()
        print("\n✅ 모든 테스트 통과!")
    else:
        print("\n❌ 테스트 실패!")
        sys.exit(1)


if __name__ == "__main__":
    main()