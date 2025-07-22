from typing import List, Dict, Any
from app.core.vector_db import get_vector_db
from app.core.embedding_model import get_embedding_model
from app.core.data_loader.korean_word_problems_loader import get_korean_word_problems
from app.core.data_loader.card_check_loader import get_card_check_data


class IndexingService:
    def __init__(self):
        """인덱싱 서비스 초기화"""
        self.vector_db = get_vector_db()
        self.embedding_model = get_embedding_model()

    def index_korean_word_problems(self) -> Dict[str, Any]:
        """
        한국어 단어 문제 데이터를 벡터 DB에 인덱싱합니다.

        Returns:
            인덱싱 결과
        """
        try:
            print("🧑🏻‍💻 한국어 단어 문제 데이터 로딩 중...")
            data = get_korean_word_problems()

            if not data:
                return {"status": "error", "message": "데이터를 찾을 수 없습니다."}

            # 문서 준비
            documents = self.embedding_model.prepare_documents_for_indexing(
                data, "korean_word_problems"
            )

            if not documents:
                return {"status": "error", "message": "처리할 문서가 없습니다."}

            # 텍스트 추출
            texts = [doc["text"] for doc in documents]
            ids = [doc["id"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]

            # 임베딩 생성
            print(f"⚒️ {len(texts)}개 문서 임베딩 중...")
            embeddings = self.embedding_model.get_embeddings(texts)

            # ChromaDB에 저장
            collection = self.vector_db.get_collection("korean_word_problems")
            collection.add(
                embeddings=embeddings,
                documents=texts,
                ids=ids,
                metadatas=metadatas
            )

            print(f"✅ {len(documents)}개 문서 인덱싱 완료")
            return {
                "status": "success",
                "indexed_count": len(documents),
                "collection": "korean_word_problems"
            }

        except Exception as e:
            print(f"❌ 한국어 단어 문제 인덱싱 실패: {e}")
            return {"status": "error", "message": str(e)}

    def index_card_check_data(self) -> Dict[str, Any]:
        """
        카드 체크 데이터를 벡터 DB에 인덱싱합니다.

        Returns:
            인덱싱 결과
        """
        try:
            print("🃏 카드 체크 데이터 로딩 중...")
            data = get_card_check_data()

            if not data:
                return {"status": "error", "message": "데이터를 찾을 수 없습니다."}

            # 문서 준비
            documents = self.embedding_model.prepare_documents_for_indexing(
                data, "card_check"
            )

            if not documents:
                return {"status": "error", "message": "처리할 문서가 없습니다."}

            # 텍스트 추출
            texts = [doc["text"] for doc in documents]
            ids = [doc["id"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]

            # 임베딩 생성
            print(f"🔎 {len(texts)}개 문서 임베딩 중...")
            embeddings = self.embedding_model.get_embeddings(texts)

            # ChromaDB에 저장
            collection = self.vector_db.get_collection("card_check")
            collection.add(
                embeddings=embeddings,
                documents=texts,
                ids=ids,
                metadatas=metadatas
            )

            print(f"✅ {len(documents)}개 문서 인덱싱 완료")
            return {
                "status": "success",
                "indexed_count": len(documents),
                "collection": "card_check"
            }

        except Exception as e:
            print(f"❌ 카드 체크 데이터 인덱싱 실패: {e}")
            return {"status": "error", "message": str(e)}

    def index_all_data(self) -> Dict[str, Any]:
        """
        모든 데이터를 벡터 DB에 인덱싱합니다.

        Returns:
            전체 인덱싱 결과
        """
        print("🚀 전체 데이터 인덱싱 시작...")

        results = {
            "korean_word_problems": self.index_korean_word_problems(),
            "card_check": self.index_card_check_data()
        }

        # 성공/실패 통계
        success_count = sum(1 for result in results.values() if result["status"] == "success")
        total_count = len(results)

        return {
            "status": "completed",
            "total_collections": total_count,
            "successful_collections": success_count,
            "results": results
        }

    def clear_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        특정 컬렉션의 모든 데이터를 삭제합니다.

        Args:
            collection_name: 삭제할 컬렉션명

        Returns:
            삭제 결과
        """
        try:
            collection = self.vector_db.get_collection(collection_name)
            if collection:
                collection.delete(where={})
                return {
                    "status": "success",
                    "message": f"컬렉션 '{collection_name}' 데이터 삭제 완료"
                }
            else:
                return {
                    "status": "error",
                    "message": f"컬렉션 '{collection_name}'을 찾을 수 없습니다."
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"컬렉션 삭제 실패: {str(e)}"
            }


# 전역 인덱싱 서비스 인스턴스
indexing_service = None


def get_indexing_service():
    """전역 인덱싱 서비스 인스턴스를 반환합니다."""
    global indexing_service
    if indexing_service is None:
        indexing_service = IndexingService()
    return indexing_service