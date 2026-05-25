from typing import Any, Dict, List, Protocol


class LearningRecordRepository(Protocol):
    def create_record(self, record: Dict[str, Any]) -> str:
        ...

    def find_records_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        ...
