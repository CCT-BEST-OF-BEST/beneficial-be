from app.domains.classroom.repository import MongoClassroomRepository
from app.domains.classroom.service import ClassroomService
from app.infrastructure.db.mongo.mongo_client import get_mongo_client


def get_classroom_service() -> ClassroomService:
    return ClassroomService(MongoClassroomRepository(get_mongo_client()))
