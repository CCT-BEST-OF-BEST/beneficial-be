from app.domains.learning.repository import LearningRecordRepository
from app.domains.learning.service import LearningRecordService
from app.infrastructure.db.mongo.mongo_client import get_mongo_client


def get_learning_record_service() -> LearningRecordService:
    return LearningRecordService(LearningRecordRepository(get_mongo_client()))
