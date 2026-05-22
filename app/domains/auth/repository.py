from datetime import datetime
from typing import Any, Dict, Optional

from app.infrastructure.db.mongo.mongo_client import MongoClient


class AuthRepository:
    users_collection = "users"
    refresh_sessions_collection = "refresh_token_sessions"

    def __init__(self, mongo_client: MongoClient):
        self.mongo_client = mongo_client

    def create_user(self, user: Dict[str, Any]) -> str:
        return self.mongo_client.insert_one(self.users_collection, user)

    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.mongo_client.find_one(self.users_collection, {"email": email})

    def find_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.mongo_client.find_one(self.users_collection, {"user_id": user_id})

    def create_refresh_session(self, session: Dict[str, Any]) -> str:
        return self.mongo_client.insert_one(self.refresh_sessions_collection, session)

    def find_refresh_session_by_hash(
        self, refresh_token_hash: str
    ) -> Optional[Dict[str, Any]]:
        return self.mongo_client.find_one(
            self.refresh_sessions_collection,
            {"refresh_token_hash": refresh_token_hash},
        )

    def revoke_refresh_session(self, session_id: str, revoked_at: datetime) -> bool:
        return self.mongo_client.update_one(
            self.refresh_sessions_collection,
            {"session_id": session_id},
            {"revoked_at": revoked_at},
        )
