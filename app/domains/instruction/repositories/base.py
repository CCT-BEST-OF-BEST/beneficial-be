from typing import Any, Dict, List, Protocol


class TeacherAssignmentRepository(Protocol):
    def create_assignment(self, assignment: Dict[str, Any]) -> str:
        ...

    def find_assignment_by_id(self, assignment_id: str) -> Dict[str, Any] | None:
        ...

    def find_assignments(
        self,
        teacher_id: str,
        status: str | None = None,
        class_id: str | None = None,
        student_id: str | None = None,
    ) -> List[Dict[str, Any]]:
        ...

    def find_student_assignments(
        self,
        student_id: str,
        class_ids: list[str],
        status: str = "assigned",
        lesson_id: str | None = None,
        stage: int | None = None,
    ) -> List[Dict[str, Any]]:
        ...

    def update_assignment(self, assignment_id: str, fields: Dict[str, Any]) -> bool:
        ...
