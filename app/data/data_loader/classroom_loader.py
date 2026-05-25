from app.common.logging.logging_config import get_logger
from app.common.security import utc_now
from app.infrastructure.db.mongo.mongo_client import get_mongo_client

logger = get_logger(__name__)


CLASSROOMS = [
    {
        "_id": "class_demo_1",
        "class_id": "class_demo_1",
        "name": "돌봄 한국어 1반",
        "teacher_id": "teacher_demo_1",
        "student_ids": ["student_demo_1", "student_demo_2", "student_demo_3"],
    },
]


def load_classrooms() -> bool:
    """교사용 읽기 API를 확인할 수 있는 기본 반 매핑 데이터를 저장한다."""
    try:
        mongo_client = get_mongo_client()
        existing_classes = mongo_client.count_documents("classes")
        if existing_classes > 0:
            logger.info(f"[STATUS] classes 데이터 이미 존재: {existing_classes}개")
            return True

        now = utc_now()
        documents = [
            {
                **classroom,
                "created_at": now,
                "updated_at": now,
            }
            for classroom in CLASSROOMS
        ]
        mongo_client.insert_many("classes", documents)
        logger.info(f"[OK] classes 시드 완료: {len(documents)}개")
        return True

    except Exception as e:
        logger.error(f"[ERROR] classes 시드 실패: {e}")
        return False


if __name__ == "__main__":
    load_classrooms()
