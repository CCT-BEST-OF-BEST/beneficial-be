from app.common.logging.logging_config import get_logger
from app.infrastructure.db.mongo.mongo_client import get_mongo_client

logger = get_logger(__name__)


UNITS = [
    {
        "_id": "unit_1",
        "unit_id": "unit_1",
        "name": "1단원 헷갈리는 낱말",
        "order": 1,
        "lesson_ids": [
            "lesson_1",
            "lesson_2",
            "lesson_3",
            "lesson_4",
            "lesson_5",
        ],
    },
]


LESSONS = [
    {
        "_id": "lesson_1",
        "lesson_id": "lesson_1",
        "unit_id": "unit_1",
        "name": "가르치다/가르키다, 맞추다/맞히다",
        "order": 1,
        "concept_keys": ["가르치다/가르키다", "맞추다/맞히다"],
        "stage_ids": [1, 2, 3],
    },
    {
        "_id": "lesson_2",
        "lesson_id": "lesson_2",
        "unit_id": "unit_1",
        "name": "잊다/잃다, 메다/매다",
        "order": 2,
        "concept_keys": ["잊다/잃다", "메다/매다"],
        "stage_ids": [1, 2, 3],
    },
    {
        "_id": "lesson_3",
        "lesson_id": "lesson_3",
        "unit_id": "unit_1",
        "name": "바라다/바래다, 부치다/붙이다",
        "order": 3,
        "concept_keys": ["바라다/바래다", "부치다/붙이다"],
        "stage_ids": [1, 2, 3],
    },
    {
        "_id": "lesson_4",
        "lesson_id": "lesson_4",
        "unit_id": "unit_1",
        "name": "되다/돼, 안/않다",
        "order": 4,
        "concept_keys": ["되/돼", "안/않다"],
        "stage_ids": [1, 2, 3],
    },
    {
        "_id": "lesson_5",
        "lesson_id": "lesson_5",
        "unit_id": "unit_1",
        "name": "반드시/반듯이, 이따가/있다가",
        "order": 5,
        "concept_keys": ["반드시/반듯이", "이따가/있다가"],
        "stage_ids": [1, 2, 3],
    },
]


def load_content_hierarchy() -> bool:
    """단원/차시 메타데이터를 MongoDB에 저장한다."""
    try:
        mongo_client = get_mongo_client()

        mongo_client.db["units"].drop()
        mongo_client.db["lessons"].drop()
        unit_result = mongo_client.insert_many("units", UNITS)
        lesson_result = mongo_client.insert_many("lessons", LESSONS)

        logger.info(
            "[OK] 콘텐츠 계층 데이터 삽입 완료: "
            f"units={len(unit_result.inserted_ids)}, lessons={len(lesson_result.inserted_ids)}"
        )
        return True

    except Exception as e:
        logger.error(f"[ERROR] 콘텐츠 계층 데이터 로딩 실패: {e}")
        return False


if __name__ == "__main__":
    load_content_hierarchy()
