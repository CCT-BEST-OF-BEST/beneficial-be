from app.domains.classroom.repository import MongoClassroomRepository
from app.domains.progress.repository import MongoLearningRecordRepository
from app.domains.progress.service import LearningRecordService
from app.infrastructure.db.mongo.mongo_client import get_mongo_client


def get_learning_record_service() -> LearningRecordService:
    mongo_client = get_mongo_client()
    return LearningRecordService(
        MongoLearningRecordRepository(mongo_client),
        classroom_repository=MongoClassroomRepository(mongo_client),
    )
