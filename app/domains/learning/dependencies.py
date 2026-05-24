from app.domains.learning.content.repositories.mongo import MongoContentCatalogRepository
from app.domains.learning.content.service import ContentCatalogService
from app.domains.learning.repositories.mongo import MongoLearningRecordRepository
from app.domains.learning.service import LearningRecordService
from app.infrastructure.db.mongo.mongo_client import get_mongo_client


def get_learning_record_service() -> LearningRecordService:
    return LearningRecordService(MongoLearningRecordRepository(get_mongo_client()))


def get_content_catalog_service() -> ContentCatalogService:
    return ContentCatalogService(MongoContentCatalogRepository(get_mongo_client()))
