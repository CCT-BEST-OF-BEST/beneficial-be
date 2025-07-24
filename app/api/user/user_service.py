# beneficial-be/app/api/user/user_service.py 생성
import uuid
from datetime import datetime
from typing import Optional
from app.data.models.user_models import TempUser
from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)


class UserService:
    def __init__(self):
        self.mongo_client = get_mongo_client()

    async def create_temp_user(self, nickname: str) -> TempUser:
        """임시 사용자 생성"""
        try:
            temp_user_id = f"temp_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"

            temp_user = TempUser(
                temp_user_id=temp_user_id,
                nickname=nickname
            )

            # MongoDB에 저장
            self.mongo_client.insert_one(
                "temp_users",
                temp_user.dict()
            )

            logger.info(f"✅ 임시 사용자 생성 완료: {temp_user_id}")
            return temp_user

        except Exception as e:
            logger.error(f"❌ 임시 사용자 생성 실패: {e}")
            raise

    async def get_temp_user(self, temp_user_id: str) -> Optional[TempUser]:
        """임시 사용자 조회"""
        try:
            user_data = self.mongo_client.find_one(
                "temp_users",
                {"temp_user_id": temp_user_id}
            )

            if user_data:
                # 마지막 접속 시간 업데이트
                self.mongo_client.update_one(
                    "temp_users",
                    {"temp_user_id": temp_user_id},
                    {"last_access": datetime.now()}
                )
                return TempUser(**user_data)

            return None

        except Exception as e:
            logger.error(f"❌ 임시 사용자 조회 실패: {e}")
            raise


# 전역 서비스 인스턴스
_user_service = None


def get_user_service() -> UserService:
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service