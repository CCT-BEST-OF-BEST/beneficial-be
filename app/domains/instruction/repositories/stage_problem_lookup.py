from app.infrastructure.db.mongo.mongo_client import MongoClient


class MongoStageProblemLookup:
    collection_name = "stage3_problems"

    def __init__(self, mongo_client: MongoClient):
        self.mongo_client = mongo_client

    def find_stage3_full_sentences(self, lesson_id: str) -> set[str]:
        data = self.mongo_client.find_one(self.collection_name, {"lesson_id": lesson_id})
        if not data:
            return set()
        return {
            problem.get("full_sentence", "").strip()
            for problem in data.get("problems", [])
            if problem.get("full_sentence")
        }
