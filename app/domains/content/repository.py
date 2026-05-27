from typing import Any, Dict, List, Protocol

from app.infrastructure.db.mongo.mongo_client import MongoClient


class ContentCatalogRepository(Protocol):
    def find_units(self) -> List[Dict[str, Any]]:
        ...

    def find_lessons(self) -> List[Dict[str, Any]]:
        ...

    def find_lessons_by_unit(self, unit_id: str) -> List[Dict[str, Any]]:
        ...

    def find_lesson_by_id(self, lesson_id: str) -> Dict[str, Any] | None:
        ...


class MongoContentCatalogRepository:
    units_collection = "units"
    lessons_collection = "lessons"

    def __init__(self, mongo_client: MongoClient):
        self.mongo_client = mongo_client

    def find_units(self) -> List[Dict[str, Any]]:
        return self.mongo_client.find_many(
            self.units_collection,
            {},
            sort=[("order", 1)],
        )

    def find_lessons(self) -> List[Dict[str, Any]]:
        return self.mongo_client.find_many(
            self.lessons_collection,
            {},
            sort=[("unit_id", 1), ("order", 1)],
        )

    def find_lessons_by_unit(self, unit_id: str) -> List[Dict[str, Any]]:
        return self.mongo_client.find_many(
            self.lessons_collection,
            {"unit_id": unit_id},
            sort=[("order", 1)],
        )

    def find_lesson_by_id(self, lesson_id: str) -> Dict[str, Any] | None:
        return self.mongo_client.find_one(
            self.lessons_collection,
            {"lesson_id": lesson_id},
        )
