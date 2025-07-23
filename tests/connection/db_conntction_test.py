import os
from dotenv import load_dotenv
from pymongo import MongoClient
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)

# .env 파일 로드
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("No MONGO_URI environment variable set.")
DB_NAME = "beneficial_db"
COLLECTION_NAME = "chat_logs"

# MongoDB 연결을 시도하되, 실패해도 서버가 실행되도록 함
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    mongo_available = True
except Exception as e:
    logger.error(f"MongoDB 연결 실패: {e}")
    mongo_available = False
    client = None
    db = None
    collection = None

def mongo_test():
    if not mongo_available:
        return {
            "error": "MongoDB 연결이 설정되지 않았습니다. MONGO_URI 환경 변수를 설정하거나 MongoDB 서버를 실행하세요.",
            "status": "unavailable"
        }
    
    try:
        test_doc = {"msg": "hello, world!"}
        inserted_id = collection.insert_one(test_doc).inserted_id
        result = collection.find_one({"_id": inserted_id})
        if result and "_id" in result:
            result["_id"] = str(result["_id"])
        return {
            "inserted_id": str(inserted_id),
            "fetched_doc": result,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": f"MongoDB 작업 실패: {str(e)}",
            "status": "error"
        }

