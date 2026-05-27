from app.domains.classroom.repository.classroom_repository import MongoClassroomRepository
from app.domains.progress.repository.learning_record_repository import MongoLearningRecordRepository
from app.domains.progress.service.learning_record_service import LearningRecordService
from app.infrastructure.db.mongo.mongo_client import get_mongo_client


def get_learning_record_service() -> LearningRecordService:
    mongo_client = get_mongo_client()
    return LearningRecordService(
        MongoLearningRecordRepository(mongo_client),
        classroom_repository=MongoClassroomRepository(mongo_client),
    )
