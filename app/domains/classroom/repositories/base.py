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

    def find_user_by_id(self, user_id: str) -> Dict[str, Any] | None:
        ...

    def search_students_by_query(self, query: str) -> List[Dict[str, Any]]:
        ...

    def add_student_to_class(self, class_id: str, student_id: str) -> bool:
        ...

    def remove_student_from_class(self, class_id: str, student_id: str) -> bool:
        ...
