from app.domains.classroom.dependency.classroom_dependencies import get_classroom_service
from app.domains.instruction.service.generation import OpenAIProblemGenerator
from app.domains.instruction.repository.assignment_repository import MongoTeacherAssignmentRepository
from app.domains.instruction.repository.assignment_repository import MongoStageProblemLookup
from app.domains.instruction.service.instruction_service import InstructionService
from app.infrastructure.external.openai_client import get_openai_client
from app.infrastructure.db.mongo.mongo_client import get_mongo_client


def get_instruction_service() -> InstructionService:
    mongo_client = get_mongo_client()
    return InstructionService(
        repository=MongoTeacherAssignmentRepository(mongo_client),
        classroom_service=get_classroom_service(),
        stage_problem_lookup=MongoStageProblemLookup(mongo_client),
    )


def get_problem_generator() -> OpenAIProblemGenerator:
    return OpenAIProblemGenerator(get_openai_client())
