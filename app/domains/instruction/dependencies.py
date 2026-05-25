from app.domains.classroom.dependencies import get_classroom_service
from app.domains.instruction.repositories.mongo import MongoTeacherAssignmentRepository
from app.domains.instruction.service import InstructionService
from app.infrastructure.db.mongo.mongo_client import get_mongo_client


def get_instruction_service() -> InstructionService:
    return InstructionService(
        repository=MongoTeacherAssignmentRepository(get_mongo_client()),
        classroom_service=get_classroom_service(),
    )
