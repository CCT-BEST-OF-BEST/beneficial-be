from app.common.security import utc_now
from app.domains.auth.models import User
from app.domains.classroom.service import ClassroomService
from app.domains.instruction.models import (
    AssignmentStatus,
    GeneratedProblem,
    TeacherAssignment,
)
from app.domains.instruction.repositories.base import TeacherAssignmentRepository


class InstructionError(ValueError):
    pass


class AssignmentNotFoundError(InstructionError):
    pass


class AssignmentAccessError(InstructionError):
    pass


class InvalidAssignmentTransitionError(InstructionError):
    pass


class InstructionService:
    def __init__(
        self,
        repository: TeacherAssignmentRepository,
        classroom_service: ClassroomService,
    ):
        self.repository = repository
        self.classroom_service = classroom_service

    def create_draft_assignment(
        self,
        teacher: User,
        target_type: str,
        lesson_id: str,
        concept_key: str,
        problems: list[GeneratedProblem],
        class_id: str | None = None,
        student_id: str | None = None,
        unit_id: str | None = None,
        stage: int = 3,
        generation_context: dict | None = None,
    ) -> TeacherAssignment:
        self._validate_target_access(
            teacher=teacher,
            target_type=target_type,
            class_id=class_id,
            student_id=student_id,
        )
        assignment = TeacherAssignment(
            teacher_id=teacher.user_id,
            target_type=target_type,
            class_id=class_id,
            student_id=student_id,
            unit_id=unit_id,
            lesson_id=lesson_id,
            stage=stage,
            concept_key=concept_key,
            problems=problems,
            generation_context=generation_context or {},
        )
        self.repository.create_assignment(assignment.model_dump())
        return assignment

    def list_assignments(
        self,
        teacher: User,
        status: str | None = None,
        class_id: str | None = None,
        student_id: str | None = None,
    ) -> list[TeacherAssignment]:
        docs = self.repository.find_assignments(
            teacher_id=teacher.user_id,
            status=status,
            class_id=class_id,
            student_id=student_id,
        )
        return [TeacherAssignment(**doc) for doc in docs]

    def assign(self, teacher: User, assignment_id: str) -> TeacherAssignment:
        assignment = self._get_for_teacher(teacher, assignment_id)
        if assignment.status != "draft":
            raise InvalidAssignmentTransitionError("draft 상태의 배정만 assigned로 전환할 수 있습니다.")
        return self._transition(assignment, "assigned", {"assigned_at": utc_now()})

    def cancel(self, teacher: User, assignment_id: str) -> TeacherAssignment:
        assignment = self._get_for_teacher(teacher, assignment_id)
        if assignment.status not in {"draft", "assigned"}:
            raise InvalidAssignmentTransitionError("draft 또는 assigned 상태만 취소할 수 있습니다.")
        return self._transition(assignment, "cancelled", {"cancelled_at": utc_now()})

    def complete(self, teacher: User, assignment_id: str) -> TeacherAssignment:
        assignment = self._get_for_teacher(teacher, assignment_id)
        if assignment.status != "assigned":
            raise InvalidAssignmentTransitionError("assigned 상태만 완료할 수 있습니다.")
        return self._transition(assignment, "completed", {"completed_at": utc_now()})

    def _get_for_teacher(self, teacher: User, assignment_id: str) -> TeacherAssignment:
        doc = self.repository.find_assignment_by_id(assignment_id)
        if not doc:
            raise AssignmentNotFoundError("배정을 찾을 수 없습니다.")
        assignment = TeacherAssignment(**doc)
        if teacher.role != "developer" and assignment.teacher_id != teacher.user_id:
            raise AssignmentAccessError("본인이 만든 배정만 관리할 수 있습니다.")
        return assignment

    def _transition(
        self,
        assignment: TeacherAssignment,
        status: AssignmentStatus,
        fields: dict,
    ) -> TeacherAssignment:
        update_fields = {"status": status, **fields}
        self.repository.update_assignment(assignment.assignment_id, update_fields)
        data = assignment.model_dump()
        data.update(update_fields)
        return TeacherAssignment(**data)

    def _validate_target_access(
        self,
        teacher: User,
        target_type: str,
        class_id: str | None,
        student_id: str | None,
    ) -> None:
        if target_type == "class":
            if not class_id:
                raise InstructionError("반 배정에는 class_id가 필요합니다.")
            if not self.classroom_service.get_class_for_user(class_id, teacher):
                raise AssignmentAccessError("담당 반에만 배정할 수 있습니다.")
            return

        if target_type == "student":
            if not student_id:
                raise InstructionError("학생 배정에는 student_id가 필요합니다.")
            if not self.classroom_service.can_access_student(teacher, student_id):
                raise AssignmentAccessError("담당 학생에게만 배정할 수 있습니다.")
            return

        raise InstructionError("target_type은 student 또는 class여야 합니다.")
