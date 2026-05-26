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

    def create_class(self, class_doc: Dict[str, Any]) -> str:
        return self.mongo_client.insert_one(self.classes_collection, class_doc)

    def find_user_by_id(self, user_id: str) -> Dict[str, Any] | None:
        return self.mongo_client.find_one(
            self.users_collection,
            {"user_id": user_id},
        )

    def search_students_by_query(self, query: str) -> List[Dict[str, Any]]:
        pattern = {"$regex": query, "$options": "i"}
        return self.mongo_client.find_many(
            self.users_collection,
            {"role": "student", "$or": [{"display_name": pattern}, {"email": pattern}]},
            sort=[("display_name", 1)],
            limit=20,
        )

    def add_student_to_class(self, class_id: str, student_id: str) -> bool:
        return self.mongo_client.update_one_operator(
            self.classes_collection,
            {"class_id": class_id},
            {"$addToSet": {"student_ids": student_id}},
        )

    def remove_student_from_class(self, class_id: str, student_id: str) -> bool:
        return self.mongo_client.update_one_operator(
            self.classes_collection,
            {"class_id": class_id},
            {"$pull": {"student_ids": student_id}},
        )
