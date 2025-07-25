"""
애플리케이션 초기화 서비스
main.py에서 복잡한 초기화 로직을 분리
"""
import logging
from typing import Dict, Any
from app.common.dependency.dependencies import initialize_dependencies
from app.infrastructure.db.vector.vector_db import initialize_vector_db
from app.api.system.indexing_service import get_indexing_service
from app.data.data_loader.stage3_problems_loader import load_stage3_problems

logger = logging.getLogger(__name__)


class InitializationService:
    """애플리케이션 초기화 서비스"""

    def __init__(self):
        self.vector_db = None
        self.indexing_service = None

    async def initialize_application(self) -> Dict[str, Any]:
        """
        애플리케이션 전체 초기화

        Returns:
            초기화 결과 정보
        """
        try:
            logger.info("🚀 애플리케이션 초기화 시작...")

            # 1. 의존성 초기화
            initialize_dependencies()
            logger.info("✅ 의존성 초기화 완료")

            # 2. 벡터 DB 초기화
            self.vector_db = initialize_vector_db()
            logger.info("✅ 벡터 DB 초기화 완료")

            # 3. 인덱싱 서비스 초기화
            self.indexing_service = get_indexing_service()

            # 4. 데이터 상태 확인 및 자동 인덱싱
            indexing_result = await self._check_and_index_data()

            # 5. 3단계 문제 데이터 로딩
            stage3_result = self._load_stage3_data()

            return {
                "status": "success",
                "message": "애플리케이션 초기화 완료",
                "indexing_result": indexing_result,
                "stage3_result": stage3_result
            }

        except Exception as e:
            logger.error(f"❌ 애플리케이션 초기화 실패: {e}")
            return {
                "status": "error",
                "message": f"초기화 실패: {str(e)}"
            }

    async def _check_and_index_data(self) -> Dict[str, Any]:
        """데이터 상태 확인 및 필요시 자동 인덱싱"""
        try:
            # 기존 데이터 확인 (PDF 문서 컬렉션 포함)
            korean_collection = self.vector_db.get_collection("korean_word_problems")
            card_collection = self.vector_db.get_collection("card_check")
            pdf_collection = self.vector_db.get_collection("pdf_documents")

            korean_count = korean_collection.count() if korean_collection else 0
            card_count = card_collection.count() if card_collection else 0
            pdf_count = pdf_collection.count() if pdf_collection else 0

            logger.info(f"🩺 데이터 상태: 문제({korean_count}개), 카드({card_count}개), PDF({pdf_count}개)")

            # 데이터가 없으면 자동 인덱싱
            if korean_count == 0 or card_count == 0:
                logger.info("📚 데이터가 없어서 자동 인덱싱을 시작합니다...")
                result = await self.indexing_service.index_all_data()
                logger.info(f"✅ 자동 인덱싱 완료: 성공 {result['successful_collections']}/{result['total_collections']}개 컬렉션")
                return result
            else:
                logger.info("📊 기존 데이터가 충분합니다.")
                return {
                    "status": "no_indexing_needed",
                    "korean_count": korean_count,
                    "card_count": card_count,
                    "pdf_count": pdf_count
                }

        except Exception as e:
            logger.error(f"❌ 데이터 확인/인덱싱 실패: {e}")
            return {
                "status": "error",
                "message": f"데이터 처리 실패: {str(e)}"
            }

    def _load_stage3_data(self) -> Dict[str, Any]:
        """3단계 문제 데이터 로딩"""
        try:
            result = load_stage3_problems()
            if result:
                logger.info("✅ 3단계 문제 데이터 로딩 완료")
                return {
                    "status": "success",
                    "message": "3단계 문제 데이터 로딩 완료"
                }
            else:
                logger.warning("⚠️ 3단계 문제 데이터 로딩 실패")
                return {
                    "status": "warning",
                    "message": "3단계 문제 데이터 로딩 실패"
                }
        except Exception as e:
            logger.error(f"❌ 3단계 문제 데이터 로딩 실패: {e}")
            return {
                "status": "error",
                "message": f"3단계 문제 데이터 로딩 실패: {str(e)}"
            }

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 확인"""
        try:
            collections_info = {}
            for collection_name in ["korean_word_problems", "card_check", "pdf_documents"]:
                collection = self.vector_db.get_collection(collection_name)
                if collection:
                    collections_info[collection_name] = {
                        "document_count": collection.count(),
                        "status": "available"
                    }
                else:
                    collections_info[collection_name] = {
                        "document_count": 0,
                        "status": "not_available"
                    }

            return {
                "status": "success",
                "system": "active",
                "collections": collections_info
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"상태 확인 실패: {str(e)}"
            }


# 전역 초기화 서비스 인스턴스
initialization_service = None


def get_initialization_service() -> InitializationService:
    """초기화 서비스 인스턴스 반환"""
    global initialization_service
    if initialization_service is None:
        initialization_service = InitializationService()
    return initialization_service