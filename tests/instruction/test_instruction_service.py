from datetime import datetime, timezone

import pytest

from app.domains.auth.models import User
from app.domains.instruction.models import GeneratedProblem
from app.domains.instruction.service import (
    AssignmentAccessError,
    InstructionService,
    InvalidAssignmentTransitionError,
)


def _user(user_id="teacher_1", role="teacher") -> User:
    now = datetime.now(timezone.utc)
    return User(
        user_id=user_id,
        email=f"{user_id}@example.com",
        password_hash="hash",
        display_name=user_id,
        role=role,
        created_at=now,
        updated_at=now,
    )


def _problem() -> GeneratedProblem:
    return GeneratedProblem(
        problem_id="gen_1",
        sentence_part1="숙제가 다",
        correct_answer="됐어",
        sentence_part2="?",
        full_sentence="숙제가 다 됐어?",
        explanation="'됐어'는 '되었어'의 줄임말입니다.",
    )


class FakeAssignmentRepository:
    def __init__(self):
        self.assignments = []

    def create_assignment(self, assignment):
        self.assignments.append(dict(assignment))
        return "inserted"

    def find_assignment_by_id(self, assignment_id):
        return next(
            (
                assignment
                for assignment in self.assignments
                if assignment["assignment_id"] == assignment_id
            ),
            None,
        )

    def find_assignments(self, teacher_id, status=None, class_id=None, student_id=None):
        results = [
            assignment
            for assignment in self.assignments
            if assignment["teacher_id"] == teacher_id
        ]
        if status:
            results = [assignment for assignment in results if assignment["status"] == status]
        if class_id:
            results = [assignment for assignment in results if assignment.get("class_id") == class_id]
        if student_id:
            results = [assignment for assignment in results if assignment.get("student_id") == student_id]
        return results

    def update_assignment(self, assignment_id, fields):
        assignment = self.find_assignment_by_id(assignment_id)
        if not assignment:
            return False
        assignment.update(fields)
        return True


class FakeClassroomService:
    def __init__(self, allowed_classes=None, allowed_students=None):
        self.allowed_classes = set(allowed_classes or [])
        self.allowed_students = set(allowed_students or [])

    def get_class_for_user(self, class_id, user):
        if user.role == "developer" or class_id in self.allowed_classes:
            return {"class_id": class_id}
        return None

    def can_access_student(self, user, student_id):
        return user.role == "developer" or student_id in self.allowed_students


def _service(repository=None, classroom_service=None):
    return InstructionService(
        repository or FakeAssignmentRepository(),
        classroom_service or FakeClassroomService(
            allowed_classes=["class_1"],
            allowed_students=["student_1"],
        ),
    )


def test_create_student_draft_assignment_sets_problem_keys():
    repository = FakeAssignmentRepository()
    service = _service(repository=repository)

    assignment = service.create_draft_assignment(
        teacher=_user(),
        target_type="student",
        student_id="student_1",
        lesson_id="lesson_4",
        concept_key="되/돼",
        problems=[_problem()],
    )

    assert assignment.status == "draft"
    assert assignment.student_id == "student_1"
    assert assignment.problems[0].problem_key == f"assignment:{assignment.assignment_id}:gen_1"
    assert repository.assignments[0]["assignment_id"] == assignment.assignment_id


def test_create_assignment_rejects_unowned_student():
    service = _service(classroom_service=FakeClassroomService(allowed_students=[]))

    with pytest.raises(AssignmentAccessError):
        service.create_draft_assignment(
            teacher=_user(),
            target_type="student",
            student_id="student_1",
            lesson_id="lesson_4",
            concept_key="되/돼",
            problems=[_problem()],
        )


def test_assignment_status_transitions():
    repository = FakeAssignmentRepository()
    service = _service(repository=repository)
    assignment = service.create_draft_assignment(
        teacher=_user(),
        target_type="class",
        class_id="class_1",
        lesson_id="lesson_4",
        concept_key="되/돼",
        problems=[_problem()],
    )

    assigned = service.assign(_user(), assignment.assignment_id)
    completed = service.complete(_user(), assignment.assignment_id)

    assert assigned.status == "assigned"
    assert assigned.assigned_at is not None
    assert completed.status == "completed"
    assert completed.completed_at is not None


def test_assignment_rejects_invalid_transition():
    service = _service()
    assignment = service.create_draft_assignment(
        teacher=_user(),
        target_type="class",
        class_id="class_1",
        lesson_id="lesson_4",
        concept_key="되/돼",
        problems=[_problem()],
    )

    with pytest.raises(InvalidAssignmentTransitionError):
        service.complete(_user(), assignment.assignment_id)


def test_list_assignments_filters_by_status():
    service = _service()
    assignment = service.create_draft_assignment(
        teacher=_user(),
        target_type="student",
        student_id="student_1",
        lesson_id="lesson_4",
        concept_key="되/돼",
        problems=[_problem()],
    )
    service.assign(_user(), assignment.assignment_id)

    assignments = service.list_assignments(_user(), status="assigned")

    assert len(assignments) == 1
    assert assignments[0].assignment_id == assignment.assignment_id
