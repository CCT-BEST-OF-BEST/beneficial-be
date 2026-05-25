from typing import Any, Dict, List

from app.infrastructure.db.mongo.mongo_client import MongoClient


class MongoLearningRecordRepository:
    collection_name = "learning_records"

    def __init__(self, mongo_client: MongoClient):
        self.mongo_client = mongo_client

    def create_record(self, record: Dict[str, Any]) -> str:
        return self.mongo_client.insert_one(self.collection_name, record)

    def find_records_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        return self.mongo_client.find_many(
            self.collection_name,
            {"user_id": user_id},
            sort=[("created_at", -1)],
        )
