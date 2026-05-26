from app.domains.auth.models import User
from app.domains.classroom.models import Classroom
from app.domains.classroom.repositories.base import ClassroomRepository


class ClassroomService:
    def __init__(self, repository: ClassroomRepository):
        self.repository = repository

    def list_classes_for_user(self, user: User) -> list[Classroom]:
        if user.role == "developer":
            class_docs = self.repository.find_all_classes()
        else:
            class_docs = self.repository.find_classes_by_teacher(user.user_id)
        return [Classroom(**doc) for doc in class_docs]

    def get_class_for_user(self, class_id: str, user: User) -> Classroom | None:
        class_doc = self.repository.find_class_by_id(class_id)
        if not class_doc:
            return None

        classroom = Classroom(**class_doc)
        if user.role == "developer" or classroom.teacher_id == user.user_id:
            return classroom
        return None

    def list_students_for_class(self, class_id: str, user: User) -> list[dict]:
        classroom = self.get_class_for_user(class_id, user)
        if not classroom:
            return []

        users = self.repository.find_users_by_ids(classroom.student_ids)
        user_by_id = {student["user_id"]: student for student in users}
        return [
            user_by_id[student_id]
            for student_id in classroom.student_ids
            if student_id in user_by_id
        ]

    def can_access_student(self, user: User, student_id: str) -> bool:
        if user.role == "developer":
            return True

        classrooms = self.repository.find_classes_by_student(student_id)
        return any(classroom.get("teacher_id") == user.user_id for classroom in classrooms)

    def list_classes_for_student(self, student_id: str) -> list[Classroom]:
        class_docs = self.repository.find_classes_by_student(student_id)
        return [Classroom(**doc) for doc in class_docs]
