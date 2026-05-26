from typing import Any, Dict, List

from app.infrastructure.db.mongo.mongo_client import MongoClient


class MongoTeacherAssignmentRepository:
    collection_name = "teacher_assignments"

    def __init__(self, mongo_client: MongoClient):
        self.mongo_client = mongo_client

    def create_assignment(self, assignment: Dict[str, Any]) -> str:
        return self.mongo_client.insert_one(self.collection_name, assignment)

    def find_assignment_by_id(self, assignment_id: str) -> Dict[str, Any] | None:
        return self.mongo_client.find_one(
            self.collection_name,
            {"assignment_id": assignment_id},
        )

    def find_assignments(
        self,
        teacher_id: str,
        status: str | None = None,
        class_id: str | None = None,
        student_id: str | None = None,
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"teacher_id": teacher_id}
        if status:
            query["status"] = status
        if class_id:
            query["class_id"] = class_id
        if student_id:
            query["student_id"] = student_id
        return self.mongo_client.find_many(
            self.collection_name,
            query,
            sort=[("created_at", -1)],
        )

    def find_student_assignments(
        self,
        student_id: str,
        class_ids: list[str],
        status: str = "assigned",
        lesson_id: str | None = None,
        stage: int | None = None,
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {
            "status": status,
            "$or": [
                {"target_type": "student", "student_id": student_id},
                {"target_type": "class", "class_id": {"$in": class_ids}},
            ],
        }
        if lesson_id:
            query["lesson_id"] = lesson_id
        if stage is not None:
            query["stage"] = stage
        return self.mongo_client.find_many(
            self.collection_name,
            query,
            sort=[("assigned_at", 1), ("created_at", 1)],
        )

    def update_assignment(self, assignment_id: str, fields: Dict[str, Any]) -> bool:
        return self.mongo_client.update_one(
            self.collection_name,
            {"assignment_id": assignment_id},
            fields,
        )
