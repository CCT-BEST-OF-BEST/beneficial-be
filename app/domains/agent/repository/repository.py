from typing import Any, Dict, List, Optional

from app.infrastructure.db.mongo.mongo_client import MongoClient


class ChatSessionRepository:
    collection = "chat_sessions"

    def __init__(self, mongo_client: MongoClient):
        self.mongo_client = mongo_client

    def create(self, session: Dict[str, Any]) -> str:
        return self.mongo_client.insert_one(self.collection, session)

    def find_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.mongo_client.find_one(self.collection, {"session_id": session_id})

    def find_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        return self.mongo_client.find_many(
            self.collection,
            {"user_id": user_id},
            sort=[("updated_at", -1)],
        )

    def update_session(
        self,
        session_id: str,
        messages: List[Dict[str, Any]],
        updated_at,
        last_agent_action: Optional[str] = None,
        last_intervention_at=None,
    ) -> bool:
        update: Dict[str, Any] = {"messages": messages, "updated_at": updated_at}
        if last_agent_action is not None:
            update["last_agent_action"] = last_agent_action
        if last_intervention_at is not None:
            update["last_intervention_at"] = last_intervention_at
        return self.mongo_client.update_one(
            self.collection, {"session_id": session_id}, update
        )

    def delete(self, session_id: str) -> bool:
        return self.mongo_client.delete_one(self.collection, {"session_id": session_id})
