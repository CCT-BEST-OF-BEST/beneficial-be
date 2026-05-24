from typing import Any, Dict, List, Protocol


class ContentCatalogRepository(Protocol):
    def find_units(self) -> List[Dict[str, Any]]:
        ...

    def find_lessons(self) -> List[Dict[str, Any]]:
        ...

    def find_lessons_by_unit(self, unit_id: str) -> List[Dict[str, Any]]:
        ...

    def find_lesson_by_id(self, lesson_id: str) -> Dict[str, Any] | None:
        ...
