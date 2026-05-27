from app.domains.classroom.repository.classroom_repository import MongoClassroomRepository
from app.domains.classroom.service.classroom_service import ClassroomService
from app.infrastructure.db.mongo.mongo_client import get_mongo_client


def get_classroom_service() -> ClassroomService:
    return ClassroomService(MongoClassroomRepository(get_mongo_client()))
