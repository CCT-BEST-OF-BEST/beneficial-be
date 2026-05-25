from typing import Any, Dict, List

from app.infrastructure.db.mongo.mongo_client import MongoClient


class MongoClassroomRepository:
    classes_collection = "classes"
    users_collection = "users"

    def __init__(self, mongo_client: MongoClient):
        self.mongo_client = mongo_client

    def find_all_classes(self) -> List[Dict[str, Any]]:
        return self.mongo_client.find_many(
            self.classes_collection,
            {},
            sort=[("name", 1)],
        )

    def find_classes_by_teacher(self, teacher_id: str) -> List[Dict[str, Any]]:
        return self.mongo_client.find_many(
            self.classes_collection,
            {"teacher_id": teacher_id},
            sort=[("name", 1)],
        )

    def find_class_by_id(self, class_id: str) -> Dict[str, Any] | None:
        return self.mongo_client.find_one(
            self.classes_collection,
            {"class_id": class_id},
        )

    def find_classes_by_student(self, student_id: str) -> List[Dict[str, Any]]:
        return self.mongo_client.find_many(
            self.classes_collection,
            {"student_ids": student_id},
            sort=[("name", 1)],
        )

    def find_users_by_ids(self, user_ids: list[str]) -> List[Dict[str, Any]]:
        if not user_ids:
            return []
        return self.mongo_client.find_many(
            self.users_collection,
            {"user_id": {"$in": user_ids}},
            sort=[("display_name", 1)],
        )
