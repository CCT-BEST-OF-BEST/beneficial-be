"""
MongoDB 연결 및 관리 클라이언트
통합된 MongoDB 연결을 제공하여 중복 연결 방지
"""
import os
from typing import Optional, Dict, Any, List
from pymongo import MongoClient as PyMongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from dotenv import load_dotenv

load_dotenv()


class MongoClient:
    """MongoDB 연결 전용 클라이언트"""

    def __init__(self, connection_string: str = None, database_name: str = "beneficial_db"):
        """
        MongoDB 클라이언트 초기화

        Args:
            connection_string: MongoDB 연결 문자열 (None이면 환경변수에서 읽음)
            database_name: 사용할 데이터베이스명
        """
        self.connection_string = connection_string or os.getenv("MONGO_URI")
        self.database_name = database_name

        if not self.connection_string:
            raise ValueError("MongoDB 연결 문자열이 필요합니다. MONGO_URI 환경변수를 설정하세요.")

        # MongoDB 클라이언트 초기화
        self.client: Optional[PyMongoClient] = None
        self.db: Optional[Database] = None
        self._is_connected = False

        # 연결 시도
        self._connect()

    def _connect(self):
        """MongoDB 연결"""
        try:
            self.client = PyMongoClient(self.connection_string)
            self.db = self.client[self.database_name]

            # 연결 테스트
            self.client.admin.command('ping')
            self._is_connected = True
            print(f"✅ MongoDB 연결 성공: {self.database_name}")

        except Exception as e:
            print(f"❌ MongoDB 연결 실패: {e}")
            self._is_connected = False
            raise

    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self._is_connected

    def get_database(self) -> Database:
        """데이터베이스 인스턴스 반환"""
        if not self._is_connected:
            raise ConnectionError("MongoDB에 연결되지 않았습니다.")
        return self.db

    def get_collection(self, collection_name: str) -> Collection:
        """
        컬렉션 인스턴스 반환

        Args:
            collection_name: 컬렉션명

        Returns:
            MongoDB 컬렉션 인스턴스
        """
        if not self._is_connected:
            raise ConnectionError("MongoDB에 연결되지 않았습니다.")
        return self.db[collection_name]

    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> str:
        """
        단일 문서 삽입

        Args:
            collection_name: 컬렉션명
            document: 삽입할 문서

        Returns:
            삽입된 문서의 ID
        """
        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        return str(result.inserted_id)

    def find_one(self, collection_name: str, filter_dict: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        단일 문서 조회

        Args:
            collection_name: 컬렉션명
            filter_dict: 필터 조건

        Returns:
            조회된 문서 (없으면 None)
        """
        collection = self.get_collection(collection_name)
        filter_dict = filter_dict or {}
        return collection.find_one(filter_dict)

    def find_many(self, collection_name: str, filter_dict: Dict[str, Any] = None, limit: int = None) -> List[
        Dict[str, Any]]:
        """
        여러 문서 조회

        Args:
            collection_name: 컬렉션명
            filter_dict: 필터 조건
            limit: 조회할 문서 수 제한

        Returns:
            조회된 문서 리스트
        """
        collection = self.get_collection(collection_name)
        filter_dict = filter_dict or {}

        cursor = collection.find(filter_dict)
        if limit:
            cursor = cursor.limit(limit)

        return list(cursor)

    def update_one(self, collection_name: str, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> bool:
        """
        단일 문서 업데이트

        Args:
            collection_name: 컬렉션명
            filter_dict: 필터 조건
            update_dict: 업데이트할 내용

        Returns:
            업데이트 성공 여부
        """
        collection = self.get_collection(collection_name)
        result = collection.update_one(filter_dict, {"$set": update_dict})
        return result.modified_count > 0

    def delete_one(self, collection_name: str, filter_dict: Dict[str, Any]) -> bool:
        """
        단일 문서 삭제

        Args:
            collection_name: 컬렉션명
            filter_dict: 필터 조건

        Returns:
            삭제 성공 여부
        """
        collection = self.get_collection(collection_name)
        result = collection.delete_one(filter_dict)
        return result.deleted_count > 0

    def count_documents(self, collection_name: str, filter_dict: Dict[str, Any] = None) -> int:
        """
        문서 수 조회

        Args:
            collection_name: 컬렉션명
            filter_dict: 필터 조건

        Returns:
            문서 수
        """
        collection = self.get_collection(collection_name)
        filter_dict = filter_dict or {}
        return collection.count_documents(filter_dict)

    def close(self):
        """MongoDB 연결 종료"""
        if self.client:
            self.client.close()
            self._is_connected = False
            print("🔌 MongoDB 연결 종료")

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()


# 전역 MongoDB 클라이언트 인스턴스
_mongo_client: Optional[MongoClient] = None


def get_mongo_client() -> MongoClient:
    """전역 MongoDB 클라이언트 인스턴스 반환"""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient()
    return _mongo_client


def reset_mongo_client():
    """MongoDB 클라이언트 인스턴스 리셋 (테스트용)"""
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
    _mongo_client = None