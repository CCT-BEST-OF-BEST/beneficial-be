import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from app.common.logging.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)

class VectorDatabase:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        ChromaDB 벡터 데이터베이스 초기화

        Args:
            persist_directory: 벡터 데이터를 저장할 디렉토리 경로
        """
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # 컬렉션 초기화
        self.collections = {}
        self._initialize_collections()

    def _initialize_collections(self):
        """필요한 컬렉션들을 초기화합니다."""
        collections_config = {
            "korean_word_problems": {
                "metadata": {"type": "educational", "language": "korean"}
            },
            "card_check": {
                "metadata": {"type": "educational", "language": "korean"}
            },
            "pdf_documents": {  # 신규 추가
                "metadata": {"type": "document", "language": "korean", "source": "pdf"}
            }
        }

        for collection_name, config in collections_config.items():
            try:
                # description 파라미터 제거
                collection = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata=config["metadata"]
                )
                self.collections[collection_name] = collection
                logger.info(f"✅ 컬렉션 '{collection_name}' 초기화 완료")
            except Exception as e:
                logger.error(f"❌ 컬렉션 '{collection_name}' 초기화 실패: {e}")

    def get_collection(self, collection_name: str):
        """특정 컬렉션을 반환합니다."""
        return self.collections.get(collection_name)

    def list_collections(self):
        """모든 컬렉션 목록을 반환합니다."""
        return list(self.collections.keys())

    def collection_info(self, collection_name: str):
        """컬렉션 정보를 반환합니다."""
        collection = self.get_collection(collection_name)
        if collection:
            return {
                "name": collection_name,
                "count": collection.count(),
                "metadata": collection.metadata
            }
        return None

# 전역 벡터 DB 인스턴스
vector_db = None

def get_vector_db():
    """전역 벡터 DB 인스턴스를 반환합니다."""
    global vector_db
    if vector_db is None:
        vector_db = VectorDatabase()
    return vector_db

def initialize_vector_db():
    """벡터 DB를 초기화합니다."""
    global vector_db
    vector_db = VectorDatabase()
    return vector_db