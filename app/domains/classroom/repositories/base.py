from typing import Any, Dict, List, Protocol


class ClassroomRepository(Protocol):
    def find_all_classes(self) -> List[Dict[str, Any]]:
        ...

    def find_classes_by_teacher(self, teacher_id: str) -> List[Dict[str, Any]]:
        ...

    def find_class_by_id(self, class_id: str) -> Dict[str, Any] | None:
        ...

    def find_classes_by_student(self, student_id: str) -> List[Dict[str, Any]]:
        ...

    def find_users_by_ids(self, user_ids: list[str]) -> List[Dict[str, Any]]:
        ...
